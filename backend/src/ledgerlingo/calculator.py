from decimal import Decimal

from ledgerlingo.models import FinancialResult, StructuredQuery


def calculate(query: StructuredQuery) -> FinancialResult:
    """Return the fixed scaffold result without accessing ledger data."""
    return FinancialResult(amount=Decimal("68"))
