import asyncio
from datetime import date
from typing import Callable

from agents import FunctionTool, function_tool

from ledgerlingo.analytics_catalog import (
    AnalyticsCatalog,
    load_analytics_catalog,
)
from ledgerlingo.calendar import (
    CalendarConfig,
    PeriodResolutionError,
    load_calendar_config,
    normalize_reporting_period,
)
from ledgerlingo.dimension_lookup import (
    DimensionMemberLookup,
)

MAX_CATALOG_RESULTS = 8


def _catalog_entries(catalog: AnalyticsCatalog) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for metric_id, metric in catalog.metrics.items():
        entries.append(
            {
                "kind": "metric",
                "id": metric_id,
                "name": metric.name,
                "aliases": metric.aliases,
                "metric_kind": metric.kind,
            }
        )
    for concept_id, concept in catalog.base_concepts.items():
        entries.append(
            {
                "kind": "base_concept",
                "id": concept_id,
                "name": concept.name,
                "aliases": concept.aliases,
                "account_class": concept.account_class,
                "tag_ids": concept.tag_ids,
                "time_behavior": concept.time_behavior,
            }
        )
    for dimension_id, dimension in catalog.dimensions.items():
        entries.append(
            {
                "kind": "dimension",
                "id": dimension_id,
                "name": dimension.name,
                "aliases": dimension.aliases,
                "role": dimension.role,
            }
        )
    return entries


def _catalog_search_results(
    catalog: AnalyticsCatalog,
    search_term: str,
) -> list[dict[str, object]]:
    term = search_term.strip().casefold()
    if not term:
        raise ValueError("A non-empty catalog search term is required.")

    matches: list[tuple[int, str, dict[str, object]]] = []
    for entry in _catalog_entries(catalog):
        aliases = entry["aliases"]
        if not isinstance(aliases, list) or not all(
            isinstance(alias, str) for alias in aliases
        ):
            raise TypeError("Catalog aliases must be a list of strings.")
        searchable = [str(entry["id"]), str(entry["name"]), *aliases]
        normalized = [value.casefold() for value in searchable]
        if not any(term in value for value in normalized):
            continue
        rank = (
            0
            if term in normalized
            else 1
            if any(value.startswith(term) for value in normalized)
            else 2
        )
        matches.append((rank, str(entry["id"]), entry))
    matches.sort(key=lambda result: (result[0], result[1]))
    return [entry for _, _, entry in matches[:MAX_CATALOG_RESULTS]]


def create_discovery_tools(
    catalog: AnalyticsCatalog | None = None,
    calendar: CalendarConfig | None = None,
    reference_date_provider: Callable[[], date] = date.today,
    dimension_lookup: DimensionMemberLookup | None = None,
) -> tuple[FunctionTool, FunctionTool, FunctionTool, FunctionTool]:
    """Create bounded catalog, period, and dimension-discovery tools."""
    loaded_catalog = catalog or load_analytics_catalog()
    loaded_calendar = calendar or load_calendar_config()
    loaded_dimension_lookup = dimension_lookup or DimensionMemberLookup()

    @function_tool
    async def search_analytics_catalog(search_term: str) -> dict[str, object]:
        """Find supported metrics, logical base concepts, or approved dimensions."""
        return {
            "matches": _catalog_search_results(loaded_catalog, search_term),
            "max_results": MAX_CATALOG_RESULTS,
        }

    @function_tool
    async def resolve_reporting_period(period: str | None) -> dict[str, object]:
        """Normalize a reporting period or request clarification when unresolved."""
        try:
            resolved = normalize_reporting_period(
                period,
                loaded_calendar,
                reference_date_provider(),
            )
        except PeriodResolutionError:
            return {
                "status": "clarification",
                "reason": "period_not_recognized",
            }
        if resolved is None:
            return {
                "status": "clarification",
                "reason": "reporting_period_required",
            }
        return {
            "status": "resolved",
            "period": resolved.model_dump(mode="json"),
        }

    @function_tool
    async def resolve_dimension_member(
        dimension_id: str,
        search_term: str,
    ) -> dict[str, object]:
        """Resolve a member using an approved logical dimension identifier."""
        resolution = await asyncio.to_thread(
            loaded_dimension_lookup.resolve_dimension_member,
            dimension_id,
            search_term,
        )
        return resolution.model_dump(mode="json")

    @function_tool
    async def resolve_company_scope() -> dict[str, object]:
        """Resolve omitted company scope only when exactly one company exists."""
        candidates = await asyncio.to_thread(
            loaded_dimension_lookup.company_code_candidates
        )
        if len(candidates) == 1:
            return {
                "status": "resolved",
                "dimension_id": "company_code",
                "member": candidates[0],
            }
        return {
            "status": "ambiguous" if candidates else "missing",
            "dimension_id": "company_code",
            "candidates": list(candidates),
        }

    return (
        search_analytics_catalog,
        resolve_reporting_period,
        resolve_dimension_member,
        resolve_company_scope,
    )
