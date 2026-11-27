from datetime import date
from pathlib import Path

import yaml

from ledgerlingo.calendar import (
    load_calendar_config,
    normalize_reporting_period,
)

RESOURCE_DIR = Path(__file__).parents[2] / "src" / "resources"


def test_normalize_calendar_quarters_and_leap_year() -> None:
    calendar = load_calendar_config()

    expected_starts = [
        date(2024, 1, 1),
        date(2024, 4, 1),
        date(2024, 7, 1),
        date(2024, 10, 1),
    ]
    for quarter, expected_start in enumerate(expected_starts, start=1):
        resolved = normalize_reporting_period(
            f"Q{quarter} 2024",
            calendar,
            date(2024, 6, 15),
        )

        assert resolved is not None
        assert resolved.start_date == expected_start
        assert resolved.end_date_exclusive == (
            expected_starts[quarter] if quarter < 4 else date(2025, 1, 1)
        )
    q1 = normalize_reporting_period("Q1 2024", calendar, date(2024, 6, 15))
    assert q1 is not None
    assert (q1.end_date_exclusive - q1.start_date).days == 91


def test_normalize_fiscal_year_uses_configured_label_convention() -> None:
    calendar = load_calendar_config()

    resolved = normalize_reporting_period(
        "fiscal year 2024", calendar, date(2024, 6, 15)
    )

    assert resolved is not None
    assert resolved.start_date == date(2024, 1, 1)
    assert resolved.end_date_exclusive == date(2025, 1, 1)


def test_normalize_custom_calendar_boundaries(tmp_path: Path) -> None:
    resource_path = RESOURCE_DIR / "mvp-calendar.yaml"
    payload = yaml.safe_load(resource_path.read_text(encoding="utf-8"))
    payload["fiscal_year"] = {
        "start": {"month": 10, "day": 1},
        "label_year": "end",
    }
    payload["quarter_starts"] = [
        {"month": 10, "day": 1},
        {"month": 1, "day": 1},
        {"month": 4, "day": 1},
        {"month": 7, "day": 1},
    ]
    config_path = tmp_path / "custom-calendar.yaml"
    config_path.write_text(yaml.safe_dump(payload), encoding="utf-8")
    calendar = load_calendar_config(config_path)

    fiscal_year = normalize_reporting_period("FY2024", calendar, date(2024, 6, 15))
    quarter = normalize_reporting_period("Q2 2024", calendar, date(2024, 6, 15))

    assert fiscal_year is not None
    assert fiscal_year.start_date == date(2023, 10, 1)
    assert fiscal_year.end_date_exclusive == date(2024, 10, 1)
    assert quarter is not None
    assert quarter.label == "Q2 2024"
    assert quarter.start_date == date(2025, 1, 1)
    assert quarter.end_date_exclusive == date(2025, 4, 1)


def test_normalize_last_quarter_uses_injected_reference_date() -> None:
    calendar = load_calendar_config()

    resolved = normalize_reporting_period("last quarter", calendar, date(2024, 5, 3))

    assert resolved is not None
    assert resolved.label == "Q1 2024"
    assert resolved.start_date == date(2024, 1, 1)
    assert resolved.end_date_exclusive == date(2024, 4, 1)


def test_default_period_and_missing_default(tmp_path: Path) -> None:
    calendar = load_calendar_config()
    assert normalize_reporting_period(None, calendar, date(2024, 5, 3)) is None

    payload = yaml.safe_load(
        (RESOURCE_DIR / "mvp-calendar.yaml").read_text(encoding="utf-8")
    )
    payload["default_reporting_period"] = "Q4 2023"
    calendar_path = tmp_path / "calendar-with-default.yaml"
    calendar_path.write_text(yaml.safe_dump(payload), encoding="utf-8")
    calendar_with_default = load_calendar_config(calendar_path)
    resolved = normalize_reporting_period(
        None,
        calendar_with_default,
        date(2024, 5, 3),
    )

    assert resolved is not None
    assert resolved.start_date == date(2023, 10, 1)
    assert resolved.end_date_exclusive == date(2024, 1, 1)
