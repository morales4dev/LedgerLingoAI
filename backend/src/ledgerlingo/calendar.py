import re
from datetime import date
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ledgerlingo.config import load_yaml_config

RESOURCE_DIR = Path(__file__).resolve().parents[1] / "resources"


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class MonthDay(_StrictModel):
    month: int = Field(ge=1, le=12)
    day: int = Field(ge=1, le=31)

    @model_validator(mode="after")
    def validate_recurring_date(self) -> "MonthDay":
        try:
            date(2001, self.month, self.day)
        except ValueError as error:
            raise ValueError("Calendar boundaries must be valid every year.") from error
        return self


class FiscalYearConfig(_StrictModel):
    start: MonthDay
    label_year: Literal["start", "end"]


class CalendarConfig(_StrictModel):
    version: str = Field(min_length=1)
    fiscal_year: FiscalYearConfig
    quarter_starts: list[MonthDay] = Field(min_length=4, max_length=4)
    default_reporting_period: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def validate_quarter_boundaries(self) -> "CalendarConfig":
        boundaries = [(item.month, item.day) for item in self.quarter_starts]
        if len(set(boundaries)) != 4:
            raise ValueError("Quarter start boundaries must be unique.")
        return self


class ResolvedPeriod(_StrictModel):
    kind: Literal["calendar_quarter", "fiscal_year"]
    label: str
    start_date: date
    end_date_exclusive: date

    @model_validator(mode="after")
    def validate_date_range(self) -> "ResolvedPeriod":
        if self.end_date_exclusive <= self.start_date:
            raise ValueError("A normalized period must have a positive date range.")
        return self


class PeriodResolutionError(ValueError):
    """Raised when a reporting period cannot be normalized."""


def load_calendar_config(path: str | Path | None = None) -> CalendarConfig:
    config_path = Path(path) if path else RESOURCE_DIR / "mvp-calendar.yaml"
    return load_yaml_config(config_path, CalendarConfig)


def _quarter_year_offsets(calendar: CalendarConfig) -> list[int]:
    offsets = [0]
    previous = calendar.quarter_starts[0]
    for boundary in calendar.quarter_starts[1:]:
        previous_key = (previous.month, previous.day)
        boundary_key = (boundary.month, boundary.day)
        year_offset = 1 if boundary_key < previous_key else 0
        offsets.append(offsets[-1] + year_offset)
        previous = boundary
    return offsets


def _quarter_bounds(
    calendar: CalendarConfig,
    quarter: int,
    cycle_year: int,
) -> tuple[date, date]:
    offsets = _quarter_year_offsets(calendar)
    index = quarter - 1
    start_boundary = calendar.quarter_starts[index]
    start = date(
        cycle_year + offsets[index],
        start_boundary.month,
        start_boundary.day,
    )
    if quarter < 4:
        end_boundary = calendar.quarter_starts[index + 1]
        end = date(
            cycle_year + offsets[index + 1],
            end_boundary.month,
            end_boundary.day,
        )
    else:
        first_boundary = calendar.quarter_starts[0]
        end = date(
            cycle_year + 1,
            first_boundary.month,
            first_boundary.day,
        )
    return start, end


def _resolve_last_quarter(
    calendar: CalendarConfig,
    reference_date: date,
) -> ResolvedPeriod:
    candidates: list[tuple[int, int, date, date]] = []
    for cycle_year in range(reference_date.year - 2, reference_date.year + 2):
        for quarter in range(1, 5):
            start, end = _quarter_bounds(calendar, quarter, cycle_year)
            if end <= reference_date:
                candidates.append((cycle_year, quarter, start, end))
    if not candidates:
        raise PeriodResolutionError(
            "No completed quarter exists before the reference date."
        )

    cycle_year, quarter, start, end = max(candidates, key=lambda item: item[2])
    return ResolvedPeriod(
        kind="calendar_quarter",
        label=f"Q{quarter} {cycle_year}",
        start_date=start,
        end_date_exclusive=end,
    )


def normalize_reporting_period(
    period: str | None,
    calendar: CalendarConfig,
    reference_date: date,
) -> ResolvedPeriod | None:
    """Resolve a supported period into a start-inclusive, end-exclusive range."""
    requested_period = (
        period if period is not None else calendar.default_reporting_period
    )
    if requested_period is None:
        return None

    value = requested_period.strip()
    if re.fullmatch(r"(?:last|previous|prior)\s+quarter", value, re.IGNORECASE):
        return _resolve_last_quarter(calendar, reference_date)

    quarter_match = re.fullmatch(
        r"(?:calendar\s+)?q([1-4])(?:\s+(\d{4}))?",
        value,
        re.IGNORECASE,
    )
    if quarter_match:
        quarter = int(quarter_match.group(1))
        cycle_year = int(quarter_match.group(2) or reference_date.year)
        start, end = _quarter_bounds(calendar, quarter, cycle_year)
        return ResolvedPeriod(
            kind="calendar_quarter",
            label=f"Q{quarter} {cycle_year}",
            start_date=start,
            end_date_exclusive=end,
        )

    fiscal_year_match = re.fullmatch(
        r"(?:fy|fiscal(?:\s+year)?)\s*(\d{4})",
        value,
        re.IGNORECASE,
    )
    if fiscal_year_match:
        label_year = int(fiscal_year_match.group(1))
        fiscal_start = calendar.fiscal_year.start
        if calendar.fiscal_year.label_year == "end" and (
            fiscal_start.month,
            fiscal_start.day,
        ) != (1, 1):
            start_year = label_year - 1
        else:
            start_year = label_year
        start = date(start_year, fiscal_start.month, fiscal_start.day)
        end = date(start_year + 1, fiscal_start.month, fiscal_start.day)
        return ResolvedPeriod(
            kind="fiscal_year",
            label=f"FY{label_year}",
            start_date=start,
            end_date_exclusive=end,
        )

    raise PeriodResolutionError(f"Unsupported reporting period: {requested_period!r}.")
