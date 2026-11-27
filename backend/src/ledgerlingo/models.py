from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ledgerlingo.analytics_catalog import APPROVED_DIMENSION_IDS, METRIC_IDS
from ledgerlingo.calendar import ResolvedPeriod


class StructuredQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")

    metrics: list[str] = Field(min_length=1, max_length=len(METRIC_IDS))
    period: ResolvedPeriod
    group_by: list[str] = Field(default_factory=list)
    filters: dict[str, str] = Field(default_factory=dict, validate_default=True)
    time_grain: Literal["month", "quarter", "year"] | None = None

    @field_validator("metrics")
    @classmethod
    def validate_metrics(cls, values: list[str]) -> list[str]:
        unknown = set(values) - METRIC_IDS
        if unknown:
            raise ValueError(f"Unknown metric IDs: {', '.join(sorted(unknown))}.")
        if len(values) != len(set(values)):
            raise ValueError("Metric IDs must be unique.")
        return values

    @field_validator("group_by")
    @classmethod
    def validate_group_by(cls, values: list[str]) -> list[str]:
        unknown = set(values) - APPROVED_DIMENSION_IDS
        if unknown:
            raise ValueError(
                f"Unapproved query dimensions: {', '.join(sorted(unknown))}."
            )
        if len(values) != len(set(values)):
            raise ValueError("Query dimensions must be unique.")
        return values

    @field_validator("filters")
    @classmethod
    def validate_filters(cls, values: dict[str, str]) -> dict[str, str]:
        unknown = set(values) - APPROVED_DIMENSION_IDS
        if unknown:
            raise ValueError(
                f"Unapproved filter dimensions: {', '.join(sorted(unknown))}."
            )
        if any(not value.strip() for value in values.values()):
            raise ValueError("Filter values must not be empty.")
        if "company_code" not in values:
            raise ValueError("A query requires a resolved company_code filter.")
        return values


class QueryInterpretation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["query", "clarification", "unsupported"]
    query: StructuredQuery | None = None
    clarification: str | None = None
    unsupported: str | None = None

    @model_validator(mode="after")
    def validate_outcome(self) -> "QueryInterpretation":
        if self.kind == "query":
            if (
                self.query is None
                or self.clarification is not None
                or self.unsupported is not None
            ):
                raise ValueError("A query outcome requires only a structured query.")
        elif self.kind == "clarification":
            if (
                self.query is not None
                or self.unsupported is not None
                or self.clarification is None
                or not self.clarification.strip()
            ):
                raise ValueError(
                    "A clarification outcome requires only a non-empty message."
                )
        elif (
            self.query is not None
            or self.clarification is not None
            or self.unsupported is None
            or not self.unsupported.strip()
        ):
            raise ValueError(
                "An unsupported outcome requires only a non-empty explanation."
            )
        return self


class QueryValidation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_valid: bool
    feedback: list[str] = Field(default_factory=list)


class FinancialResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: Decimal
