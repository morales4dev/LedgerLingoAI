from openai import AsyncOpenAI

from ledgerlingo.agent import (
    AgentConfigurationError,
    AgentError,
    InvalidModelResponseError,
    PROCESSING_FAILURE_RESPONSE,
    interpret_query,
)
from ledgerlingo.calculator import calculate
from ledgerlingo.config import Settings
from ledgerlingo.models import QueryInterpretation
from ledgerlingo.reporting import report_result
from ledgerlingo.validation import validate_query


async def process_question(
    question: str,
    settings: Settings,
    client: AsyncOpenAI,
) -> str:
    """Orchestrate one independent question and return one English response."""
    try:
        interpretation = await interpret_query(question, settings, client)
        if interpretation.kind == "clarification":
            if interpretation.clarification is None:
                raise InvalidModelResponseError(
                    "The model returned an incomplete clarification."
                )
            return interpretation.clarification

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
    except (AgentError, RuntimeError):
        return PROCESSING_FAILURE_RESPONSE
