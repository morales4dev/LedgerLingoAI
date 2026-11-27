from decimal import Decimal

import pytest
from pydantic import ValidationError

from ledgerlingo.models import FinancialResult, QueryValidation, StructuredQuery


def test_structured_query_requires_metric_and_defaults_period_and_filters() -> None:
    query = StructuredQuery(metric="revenue")

    assert query.metric == "revenue"
    assert query.period is None
    assert query.filters == {}


def test_structured_query_rejects_empty_metric() -> None:
    with pytest.raises(ValidationError):
        StructuredQuery(metric="")


def test_query_validation_defaults_feedback_to_empty() -> None:
    validation = QueryValidation(is_valid=True)

    assert validation.is_valid
    assert validation.feedback == []


def test_financial_result_preserves_decimal_precision() -> None:
    result = FinancialResult(amount="68.10")

    assert result.amount == Decimal("68.10")
    assert result.amount.as_tuple().exponent == -2
