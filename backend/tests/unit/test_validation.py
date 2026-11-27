from ledgerlingo.models import QueryValidation, StructuredQuery
from ledgerlingo.validation import validate_query


def test_validate_query_returns_typed_valid_result() -> None:
    query = StructuredQuery(metric="revenue", period="2024")

    validation = validate_query(query)

    assert validation == QueryValidation(is_valid=True)
