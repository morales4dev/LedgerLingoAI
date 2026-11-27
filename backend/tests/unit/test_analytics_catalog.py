from pathlib import Path

import pytest
import yaml

from ledgerlingo.config import ConfigurationError
from ledgerlingo.analytics_catalog import load_analytics_catalog

RESOURCE_DIR = Path(__file__).parents[2] / "src" / "resources"
METRIC_IDS = {
    "gross_profit",
    "total_operating_costs",
    "operating_profit",
    "ebitda",
    "net_finance_result",
    "profit_before_tax",
    "net_income",
    "net_assets",
    "working_capital",
    "net_debt",
    "gross_margin_pct",
    "operating_margin_pct",
    "ebitda_margin_pct",
    "net_profit_margin_pct",
    "current_ratio",
    "quick_ratio",
    "debt_to_equity",
    "roa_pct",
    "roe_pct",
    "untagged_pnl_check",
}


def test_load_analytics_catalog_covers_metrics_and_tagged_dependencies() -> None:
    catalog = load_analytics_catalog()

    assert set(catalog.metrics) == METRIC_IDS
    assert catalog.base_concepts["operating_revenue"].tag_ids == ["operating_revenue"]
    assert catalog.base_concepts["total_revenue"].tag_ids == []
    assert catalog.metrics["ebitda"].aliases


def test_load_analytics_catalog_rejects_physical_bindings(
    tmp_path: Path,
) -> None:
    resource_path = RESOURCE_DIR / "mvp-analytics-catalog.yaml"
    payload = yaml.safe_load(resource_path.read_text(encoding="utf-8"))
    payload["base_concepts"]["operating_revenue"]["physical_table"] = (
        "core.journal_entry_line"
    )
    invalid_path = tmp_path / "invalid-catalog.yaml"
    invalid_path.write_text(yaml.safe_dump(payload), encoding="utf-8")

    with pytest.raises(ConfigurationError, match="schema validation failed"):
        load_analytics_catalog(invalid_path)


def test_load_analytics_catalog_rejects_physical_column_names(
    tmp_path: Path,
) -> None:
    resource_path = RESOURCE_DIR / "mvp-analytics-catalog.yaml"
    payload = yaml.safe_load(resource_path.read_text(encoding="utf-8"))
    payload["base_concepts"]["operating_revenue"]["aliases"].append("account_code")
    invalid_path = tmp_path / "invalid-catalog.yaml"
    invalid_path.write_text(yaml.safe_dump(payload), encoding="utf-8")

    with pytest.raises(ConfigurationError, match="schema validation failed"):
        load_analytics_catalog(invalid_path)


def test_load_analytics_catalog_rejects_sql_expressions(
    tmp_path: Path,
) -> None:
    resource_path = RESOURCE_DIR / "mvp-analytics-catalog.yaml"
    payload = yaml.safe_load(resource_path.read_text(encoding="utf-8"))
    payload["base_concepts"]["operating_revenue"]["description"] = (
        "SUM(jel.credit_amount - jel.debit_amount)"
    )
    invalid_path = tmp_path / "invalid-catalog.yaml"
    invalid_path.write_text(yaml.safe_dump(payload), encoding="utf-8")

    with pytest.raises(ConfigurationError, match="schema validation failed"):
        load_analytics_catalog(invalid_path)


def test_load_analytics_catalog_rejects_unresolved_formula_dependencies(
    tmp_path: Path,
) -> None:
    metrics_path = RESOURCE_DIR / "metrics.yaml"
    payload = yaml.safe_load(metrics_path.read_text(encoding="utf-8"))
    payload["metrics"]["gross_profit"]["formula"]["left"] = "unknown_concept"
    invalid_path = tmp_path / "invalid-metrics.yaml"
    invalid_path.write_text(yaml.safe_dump(payload), encoding="utf-8")

    with pytest.raises(ConfigurationError, match="unknown dependency"):
        load_analytics_catalog(metrics_path=invalid_path)
