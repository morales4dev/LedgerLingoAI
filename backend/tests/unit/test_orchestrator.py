import asyncio
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from ledgerlingo.agent import (
    PROCESSING_FAILURE_RESPONSE,
    InvalidModelResponseError,
)
from ledgerlingo.models import (
    FinancialResult,
    QueryInterpretation,
    QueryValidation,
    StructuredQuery,
)
from ledgerlingo.orchestrator import process_question


def test_process_question_runs_pipeline_in_order() -> None:
    query = StructuredQuery(metric="revenue", period="2024")
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
        patch("ledgerlingo.orchestrator.interpret_query", new=AsyncMock(side_effect=interpret)),
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


def test_process_question_does_not_calculate_invalid_query() -> None:
    query = StructuredQuery(metric="revenue")

    with (
        patch(
            "ledgerlingo.orchestrator.interpret_query",
            new=AsyncMock(
                return_value=QueryInterpretation(kind="query", query=query)
            ),
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
