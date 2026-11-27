from datetime import date

import pytest

from ledgerlingo.calendar import ResolvedPeriod
from ledgerlingo.models import StructuredQuery


@pytest.fixture
def valid_structured_query() -> StructuredQuery:
    return StructuredQuery(
        metrics=["gross_profit"],
        period=ResolvedPeriod(
            kind="fiscal_year",
            label="FY2024",
            start_date=date(2024, 1, 1),
            end_date_exclusive=date(2025, 1, 1),
        ),
        filters={"company_code": "ACME"},
    )
