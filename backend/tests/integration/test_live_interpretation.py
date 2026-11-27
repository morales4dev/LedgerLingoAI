import asyncio
import os
from pathlib import Path

import pytest
import yaml

from ledgerlingo.agent import interpret_query
from ledgerlingo.config import load_settings
from ledgerlingo.discovery_tools import create_discovery_tools
from ledgerlingo.dimension_lookup import DimensionMemberResolution

GOLDEN_SET_PATH = (
    Path(__file__).parents[1] / "fixtures" / "analytics-interpretation-golden.yaml"
)


class _GoldenDimensionLookup:
    def resolve_dimension_member(
        self,
        dimension_id: str,
        search_term: str,
    ) -> DimensionMemberResolution:
        if dimension_id == "cost_center" and search_term.casefold() == "north":
            return DimensionMemberResolution(
                dimension_id=dimension_id,
                query=search_term,
                status="ambiguous",
                candidates=["NORTH-1", "NORTH-2"],
            )
        if dimension_id == "company_code" and search_term.casefold() == "acme":
            return DimensionMemberResolution(
                dimension_id=dimension_id,
                query=search_term,
                status="resolved",
                member="ACME",
                candidates=["ACME"],
            )
        return DimensionMemberResolution(
            dimension_id=dimension_id,
            query=search_term,
            status="missing",
        )

    def company_code_candidates(self) -> tuple[str, ...]:
        return ("ACME",)


@pytest.mark.skipif(
    os.getenv("LEDGERLINGO_RUN_LIVE_INTERPRETATION_EVAL") != "1",
    reason="Set LEDGERLINGO_RUN_LIVE_INTERPRETATION_EVAL=1 to call the configured provider.",
)
def test_live_provider_returns_expected_logical_fields() -> None:
    golden_set = yaml.safe_load(GOLDEN_SET_PATH.read_text(encoding="utf-8"))
    settings = load_settings()
    tools = create_discovery_tools(dimension_lookup=_GoldenDimensionLookup())

    for case in golden_set["cases"]:
        interpretation = asyncio.run(
            interpret_query(case["question"], settings, tools=tools)
        )
        expected = case["expected"]

        assert interpretation.kind == expected["kind"], case["id"]
        if expected["kind"] == "query":
            assert interpretation.query is not None
            assert interpretation.query.model_dump(mode="json") == expected["query"], (
                case["id"]
            )
