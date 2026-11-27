from decimal import Decimal

import pytest
from pydantic import ValidationError

from ledgerlingo.calendar import ResolvedPeriod
from ledgerlingo.models import (
    FinancialResult,
    QueryInterpretation,
    QueryValidation,
    StructuredQuery,
)


def test_structured_query_requires_metric_period_and_company_scope(
    valid_structured_query: StructuredQuery,
) -> None:
    query = valid_structured_query

    assert query.metrics == ["gross_profit"]
    assert query.period.start_date.isoformat() == "2024-01-01"
    assert query.group_by == []
    assert query.filters == {"company_code": "ACME"}
    assert query.time_grain is None


def test_structured_query_rejects_empty_metric_list() -> None:
    with pytest.raises(ValidationError):
        StructuredQuery(
            metrics=[],
            period={
                "kind": "fiscal_year",
                "label": "FY2024",
                "start_date": "2024-01-01",
                "end_date_exclusive": "2025-01-01",
            },
            filters={"company_code": "ACME"},
        )


@pytest.mark.parametrize(
    "values",
    [
        {"metrics": ["unlisted_metric"]},
        {"group_by": ["currency"]},
        {"filters": {"country": "US", "company_code": "ACME"}},
        {"filters": {"company_code": " "}},
        {"filters": {}},
    ],
)
def test_structured_query_rejects_unapproved_or_incomplete_fields(
    valid_structured_query: StructuredQuery,
    values: dict[str, object],
) -> None:
    payload = valid_structured_query.model_dump()
    payload.update(values)

    with pytest.raises(ValidationError):
        StructuredQuery.model_validate(payload)


def test_query_interpretation_validates_all_three_outcome_shapes(
    valid_structured_query: StructuredQuery,
) -> None:
    assert (
        QueryInterpretation(
            kind="query",
            query=valid_structured_query,
        ).kind
        == "query"
    )
    assert (
        QueryInterpretation(
            kind="clarification",
            clarification="Which company should I use?",
        ).kind
        == "clarification"
    )
    assert (
        QueryInterpretation(
            kind="unsupported",
            unsupported="Ranking is outside the MVP scope.",
        ).kind
        == "unsupported"
    )

    with pytest.raises(ValidationError):
        QueryInterpretation(
            kind="unsupported",
            query=valid_structured_query,
            unsupported="Not supported.",
        )


def test_resolved_period_rejects_empty_date_range() -> None:
    with pytest.raises(ValidationError):
        ResolvedPeriod(
            kind="fiscal_year",
            label="FY2024",
            start_date="2024-01-01",
            end_date_exclusive="2024-01-01",
        )


def test_query_validation_defaults_feedback_to_empty() -> None:
    validation = QueryValidation(is_valid=True)

    assert validation.is_valid
    assert validation.feedback == []


def test_financial_result_preserves_decimal_precision() -> None:
    result = FinancialResult(amount="68.10")

    assert result.amount == Decimal("68.10")
    assert result.amount.as_tuple().exponent == -2
