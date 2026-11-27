from ledgerlingo.models import FinancialResult


def report_result(result: FinancialResult) -> str:
    """Render a financial result as one English sentence."""
    return f"The result is {result.amount}."
