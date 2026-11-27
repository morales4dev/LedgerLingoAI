import asyncio
from datetime import date
from pathlib import Path

import yaml

from ledgerlingo.analytics_catalog import load_analytics_catalog
from ledgerlingo.calendar import load_calendar_config
from ledgerlingo.discovery_tools import (
    MAX_CATALOG_RESULTS,
    create_discovery_tools,
)

RESOURCE_DIR = Path(__file__).parents[2] / "src" / "resources"


def test_catalog_search_returns_bounded_logical_ids_without_physical_details() -> None:
    search_tool, *_ = create_discovery_tools(
        catalog=load_analytics_catalog(),
        calendar=load_calendar_config(),
    )

    result = asyncio.run(search_tool.__wrapped__("asset"))
    serialized = str(result).lower()

    assert len(result["matches"]) <= MAX_CATALOG_RESULTS
    assert any(match["id"] == "total_assets" for match in result["matches"])
    assert all("id" in match and "kind" in match for match in result["matches"])
    assert "core." not in serialized
    assert "select" not in serialized


def test_period_tool_returns_normalized_range_using_injected_reference_date() -> None:
    _, period_tool, *_ = create_discovery_tools(
        catalog=load_analytics_catalog(),
        calendar=load_calendar_config(),
        reference_date_provider=lambda: date(2024, 5, 3),
    )

    result = asyncio.run(period_tool.__wrapped__("last quarter"))

    assert result == {
        "status": "resolved",
        "period": {
            "kind": "calendar_quarter",
            "label": "Q1 2024",
            "start_date": "2024-01-01",
            "end_date_exclusive": "2024-04-01",
        },
    }


def test_period_tool_uses_default_or_requests_clarification(tmp_path: Path) -> None:
    payload = yaml.safe_load(
        (RESOURCE_DIR / "mvp-calendar.yaml").read_text(encoding="utf-8")
    )
    payload["default_reporting_period"] = "Q4 2023"
    calendar_path = tmp_path / "calendar-with-default.yaml"
    calendar_path.write_text(yaml.safe_dump(payload), encoding="utf-8")
    calendar = load_calendar_config(calendar_path)
    _, period_tool, *_ = create_discovery_tools(
        catalog=load_analytics_catalog(),
        calendar=calendar,
        reference_date_provider=lambda: date(2024, 5, 3),
    )
    _, no_default_tool, *_ = create_discovery_tools(
        catalog=load_analytics_catalog(),
        calendar=load_calendar_config(),
        reference_date_provider=lambda: date(2024, 5, 3),
    )

    default_result = asyncio.run(period_tool.__wrapped__(None))
    clarification = asyncio.run(no_default_tool.__wrapped__(None))

    assert default_result["status"] == "resolved"
    assert default_result["period"]["start_date"] == "2023-10-01"
    assert clarification == {
        "status": "clarification",
        "reason": "reporting_period_required",
    }
