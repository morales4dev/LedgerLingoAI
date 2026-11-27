from decimal import Decimal

from ledgerlingo.models import FinancialResult
from ledgerlingo.reporting import report_result


def test_report_result_formats_fixed_amount_in_english() -> None:
    result = FinancialResult(amount=Decimal("68"))

    answer = report_result(result)

    assert answer == "The result is 68."


def test_report_result_preserves_decimal_places() -> None:
    result = FinancialResult(amount=Decimal("68.10"))

    answer = report_result(result)

    assert answer == "The result is 68.10."
