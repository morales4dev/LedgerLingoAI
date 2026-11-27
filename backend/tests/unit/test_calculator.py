from decimal import Decimal

from ledgerlingo.calculator import calculate
from ledgerlingo.models import FinancialResult, StructuredQuery


def test_calculate_returns_fixed_financial_result_for_structured_query(
    valid_structured_query: StructuredQuery,
) -> None:
    query = valid_structured_query

    result = calculate(query)

    assert result == FinancialResult(amount=Decimal("68"))
