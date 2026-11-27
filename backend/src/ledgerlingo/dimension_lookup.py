import os
from collections.abc import Sequence
from contextlib import AbstractContextManager
from types import TracebackType
from typing import Callable, Literal, Protocol, Self

from pydantic import BaseModel, ConfigDict, Field

DATABASE_URL_ENV = "LEDGERLINGO_READONLY_DATABASE_URL"
MAX_MEMBER_RESULTS = 10
COMPANY_CARDINALITY_LIMIT = 2

_DIMENSION_COLUMNS = {
    "company_code": ("journal_entry_header", "company_code"),
    "fiscal_year": ("journal_entry_header", "fiscal_year"),
    "fiscal_period": ("journal_entry_header", "fiscal_period"),
    "posting_date": ("journal_entry_header", "posting_date"),
    "document_date": ("journal_entry_header", "document_date"),
    "cost_center": ("journal_entry_line", "cost_center"),
    "profit_center": ("journal_entry_line", "profit_center"),
    "tax_code": ("journal_entry_line", "tax_code"),
}


class DimensionLookupError(RuntimeError):
    """Raised when a controlled dimension lookup cannot be performed."""


class _Cursor(Protocol):
    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None: ...

    def execute(self, query: str, params: tuple[object, ...]) -> None: ...

    def fetchall(self) -> Sequence[tuple[object, ...]]: ...


class _Connection(Protocol):
    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None: ...

    def cursor(self) -> AbstractContextManager[_Cursor]: ...


class DimensionMemberResolution(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dimension_id: str
    query: str
    status: Literal["resolved", "ambiguous", "missing"]
    member: str | None = None
    candidates: list[str] = Field(default_factory=list)


ConnectionFactory = Callable[[], _Connection]


class DimensionMemberLookup:
    """Read-only member discovery over an explicit logical-dimension allowlist."""

    def __init__(
        self,
        database_url: str | None = None,
        connection_factory: ConnectionFactory | None = None,
    ) -> None:
        configured_url = database_url or os.getenv(DATABASE_URL_ENV)
        self._database_url = configured_url
        self._connection_factory = connection_factory or self._connect

    def _connect(self) -> _Connection:
        if self._database_url is None:
            raise DimensionLookupError(
                f"Set {DATABASE_URL_ENV} to a read-only PostgreSQL connection URL."
            )
        try:
            import psycopg
        except ImportError as error:
            raise DimensionLookupError(
                "The PostgreSQL dimension adapter requires psycopg."
            ) from error
        return psycopg.connect(
            self._database_url,
            options="-c default_transaction_read_only=on",
        )

    @staticmethod
    def _dimension_column(dimension_id: str) -> tuple[str, str]:
        try:
            return _DIMENSION_COLUMNS[dimension_id]
        except KeyError:
            raise DimensionLookupError(
                f"Unsupported dimension identifier: {dimension_id!r}."
            ) from None

    @staticmethod
    def _values(rows: Sequence[tuple[object, ...]]) -> tuple[str, ...]:
        values: list[str] = []
        for row in rows:
            if not row or row[0] is None:
                continue
            if not isinstance(row[0], str):
                raise DimensionLookupError(
                    "Dimension lookup returned a non-text member value."
                )
            values.append(row[0])
        return tuple(values)

    def _execute(
        self,
        query: str,
        params: tuple[object, ...],
    ) -> tuple[str, ...]:
        with self._connection_factory() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                return self._values(cursor.fetchall())

    def search_dimension_members(
        self,
        dimension_id: str,
        search_term: str,
    ) -> tuple[str, ...]:
        table, column = self._dimension_column(dimension_id)
        term = search_term.strip()
        if not term:
            raise DimensionLookupError("A non-empty dimension search term is required.")
        query = (
            f"SELECT DISTINCT {column}::text FROM core.{table} "
            f"WHERE {column}::text ILIKE %s ORDER BY 1 LIMIT %s"
        )
        return self._execute(
            query,
            (f"%{term}%", MAX_MEMBER_RESULTS),
        )

    def resolve_dimension_member(
        self,
        dimension_id: str,
        search_term: str,
    ) -> DimensionMemberResolution:
        candidates = self.search_dimension_members(dimension_id, search_term)
        exact_matches = [
            member
            for member in candidates
            if member.casefold() == search_term.strip().casefold()
        ]
        if len(exact_matches) == 1:
            return DimensionMemberResolution(
                dimension_id=dimension_id,
                query=search_term,
                status="resolved",
                member=exact_matches[0],
                candidates=list(candidates),
            )
        if len(exact_matches) > 1:
            return DimensionMemberResolution(
                dimension_id=dimension_id,
                query=search_term,
                status="ambiguous",
                candidates=exact_matches,
            )
        if len(candidates) == 1:
            return DimensionMemberResolution(
                dimension_id=dimension_id,
                query=search_term,
                status="resolved",
                member=candidates[0],
                candidates=list(candidates),
            )
        return DimensionMemberResolution(
            dimension_id=dimension_id,
            query=search_term,
            status="ambiguous" if candidates else "missing",
            candidates=list(candidates),
        )

    def company_code_candidates(self) -> tuple[str, ...]:
        table, column = self._dimension_column("company_code")
        query = (
            f"SELECT DISTINCT {column}::text FROM core.{table} "
            f"WHERE {column} IS NOT NULL ORDER BY 1 LIMIT %s"
        )
        return self._execute(query, (COMPANY_CARDINALITY_LIMIT,))
