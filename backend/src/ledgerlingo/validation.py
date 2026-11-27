from ledgerlingo.models import QueryValidation, StructuredQuery


def validate_query(query: StructuredQuery) -> QueryValidation:
    """Return the initial validation stub result for a structured query."""
    return QueryValidation(is_valid=True)
