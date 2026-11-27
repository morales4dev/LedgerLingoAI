import asyncio
import logging
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest

from ledgerlingo.agent import (
    PROCESSING_FAILURE_RESPONSE,
    InvalidModelResponseError,
)
from ledgerlingo.client import ModelProviderError
from ledgerlingo.models import (
    FinancialResult,
    QueryInterpretation,
    QueryValidation,
    StructuredQuery,
)
from ledgerlingo.orchestrator import process_question


def test_process_question_runs_pipeline_in_order(
    valid_structured_query: StructuredQuery,
) -> None:
    query = valid_structured_query
    events: list[str] = []
    client = Mock()

    async def interpret(*args):
        events.append("interpret")
        return QueryInterpretation(kind="query", query=query)

    def validate(received_query):
        events.append("validate")
        assert received_query == query
        return QueryValidation(is_valid=True)

    def calculate(received_query):
        events.append("calculate")
        assert received_query == query
        return FinancialResult(amount=Decimal("68"))

    def report(result):
        events.append("report")
        assert result == FinancialResult(amount=Decimal("68"))
        return "The result is 68."

    with (
        patch(
            "ledgerlingo.orchestrator.interpret_query",
            new=AsyncMock(side_effect=interpret),
        ),
        patch("ledgerlingo.orchestrator.validate_query", side_effect=validate),
        patch("ledgerlingo.orchestrator.calculate", side_effect=calculate),
        patch("ledgerlingo.orchestrator.report_result", side_effect=report),
    ):
        answer = asyncio.run(
            process_question(
                "What was revenue in 2024?",
                SimpleNamespace(model_name="test-model"),
                client,
            )
        )

    assert answer == "The result is 68."
    assert events == ["interpret", "validate", "calculate", "report"]


def test_process_question_returns_clarification_without_downstream_calls() -> None:
    client = Mock()
    clarification = "Which reporting period?"

    with (
        patch(
            "ledgerlingo.orchestrator.interpret_query",
            new=AsyncMock(
                return_value=QueryInterpretation(
                    kind="clarification", clarification=clarification
                )
            ),
        ),
        patch("ledgerlingo.orchestrator.validate_query") as validate,
        patch("ledgerlingo.orchestrator.calculate") as calculate,
        patch("ledgerlingo.orchestrator.report_result") as report,
    ):
        answer = asyncio.run(
            process_question(
                "What is the revenue?",
                SimpleNamespace(model_name="test-model"),
                client,
            )
        )

    assert answer == clarification
    validate.assert_not_called()
    calculate.assert_not_called()
    report.assert_not_called()


def test_process_question_returns_unsupported_without_downstream_calls() -> None:
    client = Mock()
    unsupported = "Customer ranking is outside the MVP scope."

    with (
        patch(
            "ledgerlingo.orchestrator.interpret_query",
            new=AsyncMock(
                return_value=QueryInterpretation(
                    kind="unsupported",
                    unsupported=unsupported,
                )
            ),
        ),
        patch("ledgerlingo.orchestrator.validate_query") as validate,
        patch("ledgerlingo.orchestrator.calculate") as calculate,
        patch("ledgerlingo.orchestrator.report_result") as report,
    ):
        answer = asyncio.run(
            process_question(
                "Rank customers by revenue.",
                SimpleNamespace(model_name="test-model"),
                client,
            )
        )

    assert answer == unsupported
    validate.assert_not_called()
    calculate.assert_not_called()
    report.assert_not_called()


def test_process_question_does_not_calculate_invalid_query(
    valid_structured_query: StructuredQuery,
) -> None:
    query = valid_structured_query

    with (
        patch(
            "ledgerlingo.orchestrator.interpret_query",
            new=AsyncMock(return_value=QueryInterpretation(kind="query", query=query)),
        ),
        patch(
            "ledgerlingo.orchestrator.validate_query",
            return_value=QueryValidation(is_valid=False, feedback=["unsupported"]),
        ),
        patch("ledgerlingo.orchestrator.calculate") as calculate,
        patch("ledgerlingo.orchestrator.report_result") as report,
    ):
        answer = asyncio.run(
            process_question(
                "What is revenue?",
                SimpleNamespace(model_name="test-model"),
                Mock(),
            )
        )

    assert answer == PROCESSING_FAILURE_RESPONSE
    calculate.assert_not_called()
    report.assert_not_called()


def test_process_question_maps_interpretation_failure_to_safe_response() -> None:
    with patch(
        "ledgerlingo.orchestrator.interpret_query",
        new=AsyncMock(side_effect=InvalidModelResponseError("invalid output")),
    ):
        answer = asyncio.run(
            process_question(
                "What is revenue?",
                SimpleNamespace(model_name="test-model"),
                Mock(),
            )
        )

    assert answer == PROCESSING_FAILURE_RESPONSE


class AuthenticationError(RuntimeError):
    status_code = 401


def _provider_authentication_failure(*_args: object) -> ModelProviderError:
    try:
        raise AuthenticationError("credential=must-not-appear-in-normal-log")
    except AuthenticationError as cause:
        raise ModelProviderError("Provider request failed.") from cause


def test_process_question_logs_actionable_hint_without_provider_error_details(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with (
        caplog.at_level(logging.ERROR),
        patch(
            "ledgerlingo.orchestrator.interpret_query",
            new=AsyncMock(side_effect=_provider_authentication_failure),
        ),
    ):
        answer = asyncio.run(
            process_question(
                "What is gross profit?",
                SimpleNamespace(model_name="test-model"),
                Mock(),
            )
        )

    assert answer == PROCESSING_FAILURE_RESPONSE
    assert "AuthenticationError, HTTP 401" in caplog.text
    assert "Check MODEL_NAME and the API key" in caplog.text
    assert "credential=must-not-appear" not in caplog.text


def test_process_question_debug_mode_logs_exception_traceback(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with (
        caplog.at_level(logging.ERROR),
        patch(
            "ledgerlingo.orchestrator.interpret_query",
            new=AsyncMock(side_effect=_provider_authentication_failure),
        ),
    ):
        asyncio.run(
            process_question(
                "What is gross profit?",
                SimpleNamespace(model_name="test-model"),
                Mock(),
                debug=True,
            )
        )

    assert "LedgerLingo request failure details" in caplog.text
    assert "credential=must-not-appear-in-normal-log" in caplog.text
