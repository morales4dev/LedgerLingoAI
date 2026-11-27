from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StructuredQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")

    metric: str = Field(min_length=1)
    period: str | None = None
    filters: dict[str, str] = Field(default_factory=dict)


class QueryInterpretation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["query", "clarification"]
    query: StructuredQuery | None = None
    clarification: str | None = None

    @model_validator(mode="after")
    def validate_outcome(self) -> "QueryInterpretation":
        if self.kind == "query":
            if self.query is None or self.clarification is not None:
                raise ValueError("A query outcome requires only a structured query.")
        elif (
            self.query is not None
            or self.clarification is None
            or not self.clarification.strip()
        ):
            raise ValueError("A clarification outcome requires only a non-empty message.")
        return self


class QueryValidation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_valid: bool
    feedback: list[str] = Field(default_factory=list)


class FinancialResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: Decimal
