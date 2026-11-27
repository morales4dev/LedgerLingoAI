import logging

from ledgerlingo.agent import (
    AgentConfigurationError,
    AgentError,
    InvalidModelResponseError,
    PROCESSING_FAILURE_RESPONSE,
    interpret_query,
)
from ledgerlingo.calculator import calculate
from ledgerlingo.client import CompletionCall, complete_model
from ledgerlingo.config import Settings
from ledgerlingo.reporting import report_result
from ledgerlingo.validation import validate_query

LOGGER = logging.getLogger(__name__)


def _log_processing_failure(error: RuntimeError, debug: bool) -> None:
    root_cause: BaseException = error
    while root_cause.__cause__ is not None:
        root_cause = root_cause.__cause__

    error_name = type(root_cause).__name__
    status_code = getattr(root_cause, "status_code", None)
    status = f", HTTP {status_code}" if isinstance(status_code, int) else ""
    if status_code in (401, 403) or error_name == "AuthenticationError":
        hint = "Check MODEL_NAME and the API key for its provider."
    elif status_code == 404 or error_name == "NotFoundError":
        hint = "Check that MODEL_NAME names an available provider/model."
    elif status_code == 429 or error_name == "RateLimitError":
        hint = "Check the provider's quota and rate limits."
    elif "Connection" in error_name:
        hint = "Check provider connectivity."
    else:
        hint = "Run with --debug to see the exception traceback."

    LOGGER.error("Request failed (%s%s). %s", error_name, status, hint)
    if debug:
        LOGGER.exception("LedgerLingo request failure details")


async def process_question(
    question: str,
    settings: Settings,
    client: CompletionCall = complete_model,
    *,
    debug: bool = False,
) -> str:
    """Orchestrate one independent question and return one English response."""
    try:
        interpretation = await interpret_query(question, settings, client)
        if interpretation.kind in ("clarification", "unsupported"):
            message = (
                interpretation.clarification
                if interpretation.kind == "clarification"
                else interpretation.unsupported
            )
            if message is None:
                raise InvalidModelResponseError(
                    f"The model returned an incomplete {interpretation.kind} outcome."
                )
            return message

        query = interpretation.query
        if query is None:
            raise InvalidModelResponseError(
                "The model returned an incomplete structured query."
            )
        validation = validate_query(query)
        if not validation.is_valid:
            return PROCESSING_FAILURE_RESPONSE

        return report_result(calculate(query))
    except AgentConfigurationError:
        raise
    except (AgentError, RuntimeError) as error:
        _log_processing_failure(error, debug)
        return PROCESSING_FAILURE_RESPONSE
