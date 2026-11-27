import asyncio
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import yaml

from ledgerlingo.analytics_catalog import METRIC_IDS, load_analytics_catalog
from ledgerlingo.agent import interpret_query

GOLDEN_SET_PATH = (
    Path(__file__).parents[1] / "fixtures" / "analytics-interpretation-golden.yaml"
)


def _client(payload: dict[str, object]) -> AsyncMock:
    message = SimpleNamespace(
        content=json.dumps(payload),
        tool_calls=None,
    )
    completion = SimpleNamespace(choices=[SimpleNamespace(message=message)])
    return AsyncMock(return_value=completion)


def test_golden_set_covers_every_metric_alias_and_outcome_family() -> None:
    catalog = load_analytics_catalog()
    golden_set = yaml.safe_load(GOLDEN_SET_PATH.read_text(encoding="utf-8"))
    cases = golden_set["cases"]
    metric_cases = [case for case in cases if "metric_id" in case]

    assert len({case["metric_id"] for case in metric_cases}) == len(METRIC_IDS)
    assert {case["metric_id"] for case in metric_cases} == METRIC_IDS
    for case in metric_cases:
        metric_id = case["metric_id"]
        matched_alias = case["matched_alias"]
        assert matched_alias in catalog.metrics[metric_id].aliases
        assert matched_alias.casefold() in case["question"].casefold()

    assert {case["expected"]["kind"] for case in cases} == {
        "query",
        "clarification",
        "unsupported",
    }
    assert any(case["id"] == "single-company-defaulting" for case in cases)
    assert any(case["id"] == "grouped-time-series" for case in cases)


def test_golden_set_outputs_match_typed_interpretation_contract() -> None:
    golden_set = yaml.safe_load(GOLDEN_SET_PATH.read_text(encoding="utf-8"))
    settings = SimpleNamespace(model_name="test-model")

    for case in golden_set["cases"]:
        expected = case["expected"]
        payload = dict(expected)
        if expected["kind"] == "clarification":
            payload["clarification"] = "Could you clarify the request?"
        elif expected["kind"] == "unsupported":
            payload["unsupported"] = "This request is outside the MVP scope."
        else:
            payload["query"] = expected["query"]

        interpretation = asyncio.run(
            interpret_query(
                case["question"],
                settings,
                _client(payload),
                tools=(),
            )
        )

        assert interpretation.kind == expected["kind"], case["id"]
        if expected["kind"] == "query":
            assert interpretation.query is not None
            assert interpretation.query.model_dump(mode="json") == expected["query"], (
                case["id"]
            )
        elif expected["kind"] == "clarification":
            assert interpretation.clarification
        else:
            assert interpretation.unsupported
