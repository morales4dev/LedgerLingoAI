from ledgerlingo.models import QueryValidation, StructuredQuery
from ledgerlingo.validation import validate_query


def test_validate_query_returns_typed_valid_result(
    valid_structured_query: StructuredQuery,
) -> None:
    query = valid_structured_query

    validation = validate_query(query)

    assert validation == QueryValidation(is_valid=True)
