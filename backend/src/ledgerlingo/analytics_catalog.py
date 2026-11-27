import re
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ledgerlingo.config import ConfigurationError, load_yaml_config

RESOURCE_DIR = Path(__file__).resolve().parents[1] / "resources"

METRIC_IDS = frozenset(
    {
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
)

DIMENSION_ROLES = {
    "company_code": "dimension",
    "cost_center": "dimension",
    "profit_center": "dimension",
    "tax_code": "dimension",
    "fiscal_year": "time_dimension",
    "fiscal_period": "time_dimension",
    "posting_date": "time_dimension",
    "document_date": "time_dimension",
}
APPROVED_DIMENSION_IDS = frozenset(DIMENSION_ROLES)

_FORBIDDEN_TEXT = re.compile(
    r"\b(?:core|stg|raw|audit|jel|jeh|gla|gat)\.[a-z_][a-z0-9_]*\b"
    r"|\b(?:SELECT|INSERT|UPDATE|DELETE|FROM|JOIN|WHERE)\b"
    r"|\b(?:SUM|COALESCE|COUNT|AVG|MIN|MAX)\s*\(",
    re.IGNORECASE,
)
_FORBIDDEN_PHYSICAL_IDENTIFIERS = re.compile(
    r"\b(?:account_code|account_type|debit_amount|credit_amount|"
    r"journal_entry_line|gl_account)\b",
    re.IGNORECASE,
)
_TAG_ID = re.compile(r"^[a-z][a-z0-9_]*$")


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class MetricEntry(_StrictModel):
    name: str = Field(min_length=1)
    aliases: list[str] = Field(min_length=1)
    kind: Literal["derived", "ratio", "control"]


class BaseConceptEntry(_StrictModel):
    name: str = Field(min_length=1)
    aliases: list[str] = Field(default_factory=list)
    account_class: Literal["asset", "liability", "equity", "revenue", "expense"]
    tag_ids: list[str] = Field(default_factory=list)
    time_behavior: Literal["flow", "point_in_time"]

    @model_validator(mode="after")
    def validate_tag_ids(self) -> "BaseConceptEntry":
        if any(not _TAG_ID.fullmatch(tag_id) for tag_id in self.tag_ids):
            raise ValueError("Tag IDs must be stable snake_case identifiers.")
        return self


class DimensionEntry(_StrictModel):
    name: str = Field(min_length=1)
    aliases: list[str] = Field(default_factory=list)
    role: Literal["dimension", "time_dimension"]


class AnalyticsCatalog(_StrictModel):
    version: str = Field(min_length=1)
    metrics: dict[str, MetricEntry]
    base_concepts: dict[str, BaseConceptEntry]
    dimensions: dict[str, DimensionEntry]

    @model_validator(mode="before")
    @classmethod
    def reject_physical_or_sql_text(cls, value: object) -> object:
        def scan(node: object) -> None:
            if isinstance(node, str) and (
                _FORBIDDEN_TEXT.search(node)
                or _FORBIDDEN_PHYSICAL_IDENTIFIERS.search(node)
            ):
                raise ValueError("Catalog contains physical or SQL text.")
            if isinstance(node, dict):
                for child in node.values():
                    scan(child)
            elif isinstance(node, list):
                for child in node:
                    scan(child)

        scan(value)
        return value

    @model_validator(mode="after")
    def validate_catalog_scope(self) -> "AnalyticsCatalog":
        if set(self.metrics) != METRIC_IDS:
            raise ValueError("Catalog must contain the complete MVP metric set.")
        if {
            dimension_id: entry.role for dimension_id, entry in self.dimensions.items()
        } != DIMENSION_ROLES:
            raise ValueError("Catalog dimensions must match the approved whitelist.")
        return self


class _MetricDefinition(_StrictModel):
    model_config = ConfigDict(extra="allow")
    formula: dict[str, object]


class _MetricsFile(_StrictModel):
    metrics: dict[str, _MetricDefinition]


def _formula_references(value: object) -> set[str]:
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        return set().union(*(_formula_references(item) for item in value))
    if isinstance(value, dict):
        return set().union(
            *(_formula_references(item) for key, item in value.items() if key != "type")
        )
    return set()


def load_analytics_catalog(
    catalog_path: str | Path | None = None,
    metrics_path: str | Path | None = None,
) -> AnalyticsCatalog:
    """Load the logical catalog and verify its metric formula dependencies."""
    catalog_file = (
        Path(catalog_path)
        if catalog_path
        else RESOURCE_DIR / "mvp-analytics-catalog.yaml"
    )
    metrics_file = Path(metrics_path) if metrics_path else RESOURCE_DIR / "metrics.yaml"

    catalog = load_yaml_config(catalog_file, AnalyticsCatalog)
    formulas = load_yaml_config(metrics_file, _MetricsFile)
    if set(formulas.metrics) != set(catalog.metrics):
        raise ConfigurationError(
            "Logical catalog metric IDs do not match metrics.yaml."
        )

    known_ids = set(catalog.metrics) | set(catalog.base_concepts)
    for metric_id, definition in formulas.metrics.items():
        unknown = _formula_references(definition.formula) - known_ids
        if unknown:
            dependencies = ", ".join(sorted(unknown))
            raise ConfigurationError(
                f"Metric '{metric_id}' references unknown dependency: {dependencies}."
            )
    return catalog
