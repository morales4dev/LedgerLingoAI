from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from typing import Self

import pytest

from ledgerlingo.dimension_lookup import (
    DimensionLookupError,
    DimensionMemberLookup,
)


class FakeCursor:
    def __init__(
        self,
        rows: list[tuple[object, ...]],
        statements: list[tuple[str, tuple[object, ...]]],
    ) -> None:
        self._rows = rows
        self._statements = statements

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def execute(
        self,
        query: str,
        params: tuple[object, ...],
    ) -> None:
        self._statements.append((query, params))

    def fetchall(self) -> Sequence[tuple[object, ...]]:
        return self._rows


class FakeConnection:
    def __init__(
        self,
        rows: list[tuple[object, ...]],
        statements: list[tuple[str, tuple[object, ...]]],
    ) -> None:
        self._rows = rows
        self._statements = statements

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        return None

    @contextmanager
    def cursor(self) -> Iterator[FakeCursor]:
        yield FakeCursor(self._rows, self._statements)


def build_lookup(
    rows: list[tuple[object, ...]],
    statements: list[tuple[str, tuple[object, ...]]],
) -> DimensionMemberLookup:
    return DimensionMemberLookup(
        connection_factory=lambda: FakeConnection(rows, statements)
    )


def test_search_uses_allowlisted_column_and_parameterized_bounded_term() -> None:
    statements: list[tuple[str, tuple[object, ...]]] = []
    lookup = build_lookup([("ACME",), ("ACME-UK",)], statements)

    resolution = lookup.resolve_dimension_member("company_code", "ACME")

    assert resolution.status == "resolved"
    assert resolution.member == "ACME"
    query, params = statements[0]
    assert "company_code::text FROM core.journal_entry_header" in query
    assert "ILIKE %s" in query
    assert params == ("%ACME%", 10)


@pytest.mark.parametrize(
    ("rows", "expected_status"),
    [
        ([("Northeast",), ("Northwest",)], "ambiguous"),
        ([], "missing"),
    ],
)
def test_resolve_dimension_member_handles_ambiguous_and_missing_matches(
    rows: list[tuple[object, ...]],
    expected_status: str,
) -> None:
    lookup = build_lookup(rows, [])

    resolution = lookup.resolve_dimension_member("cost_center", "North")

    assert resolution.status == expected_status


def test_unknown_dimension_is_rejected_before_database_access() -> None:
    statements: list[tuple[str, tuple[object, ...]]] = []
    lookup = build_lookup([], statements)

    with pytest.raises(DimensionLookupError, match="Unsupported dimension"):
        lookup.search_dimension_members("country", "US")

    assert statements == []


def test_company_cardinality_lookup_stops_after_two_distinct_codes() -> None:
    statements: list[tuple[str, tuple[object, ...]]] = []
    lookup = build_lookup([("A",), ("B",)], statements)

    candidates = lookup.company_code_candidates()

    assert candidates == ("A", "B")
    query, params = statements[0]
    assert "SELECT DISTINCT company_code::text" in query
    assert params == (2,)
