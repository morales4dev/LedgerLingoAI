from unittest.mock import AsyncMock, patch

import pytest

from ledgerlingo.agent import PROCESSING_FAILURE_RESPONSE
from ledgerlingo.cli import main
from ledgerlingo.calendar import ResolvedPeriod
from ledgerlingo.config import SettingsError
from ledgerlingo.dimension_lookup import DimensionLookupError
from ledgerlingo.models import QueryInterpretation, StructuredQuery


def test_main_runs_question_invokes_core_once_and_prints_one_response(
    capsys: pytest.CaptureFixture[str],
) -> None:
    settings = object()

    with (
        patch("ledgerlingo.cli.load_settings", return_value=settings),
        patch(
            "ledgerlingo.cli.process_question",
            new_callable=AsyncMock,
            return_value="The result is 42.",
        ) as process_question,
    ):
        exit_code = main(["What is the result?"])

    assert exit_code == 0
    assert capsys.readouterr().out == "The result is 42.\n"
    process_question.assert_awaited_once_with(
        "What is the result?",
        settings,
        debug=False,
    )


def test_main_prints_one_processing_failure_response(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with (
        patch("ledgerlingo.cli.load_settings", return_value=object()),
        patch(
            "ledgerlingo.cli.process_question",
            new_callable=AsyncMock,
            return_value=PROCESSING_FAILURE_RESPONSE,
        ),
    ):
        exit_code = main(["What is EBITDA?"])

    assert exit_code == 0
    assert capsys.readouterr().out == f"{PROCESSING_FAILURE_RESPONSE}\n"


def test_main_accepts_debug_flag_and_passes_it_to_orchestrator(
    capsys: pytest.CaptureFixture[str],
) -> None:
    settings = object()

    with (
        patch("ledgerlingo.cli.load_settings", return_value=settings),
        patch(
            "ledgerlingo.cli.process_question",
            new_callable=AsyncMock,
            return_value=PROCESSING_FAILURE_RESPONSE,
        ) as process_question,
    ):
        exit_code = main(["--debug", "What is gross profit?"])

    assert exit_code == 0
    assert capsys.readouterr().out == f"{PROCESSING_FAILURE_RESPONSE}\n"
    process_question.assert_awaited_once_with(
        "What is gross profit?",
        settings,
        debug=True,
    )


def test_main_reports_settings_failure_without_running_core(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with (
        patch(
            "ledgerlingo.cli.load_settings",
            side_effect=SettingsError(
                "Invalid settings; check required values: MODEL_NAME."
            ),
        ),
        patch(
            "ledgerlingo.cli.process_question",
            new_callable=AsyncMock,
        ) as process_question,
        pytest.raises(SystemExit) as error,
    ):
        main(["Question?"])

    assert error.value.code == 1
    assert "MODEL_NAME" in capsys.readouterr().err
    process_question.assert_not_awaited()


def test_main_requires_a_question(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as error:
        main([])

    assert error.value.code == 2
    assert "question" in capsys.readouterr().err


def test_interpret_command_prints_typed_json_without_running_normal_pipeline(
    capsys: pytest.CaptureFixture[str],
) -> None:
    settings = object()
    interpretation = QueryInterpretation(
        kind="query",
        query=StructuredQuery(
            metrics=["gross_profit"],
            period=ResolvedPeriod(
                kind="calendar_quarter",
                label="Q1 2024",
                start_date="2024-01-01",
                end_date_exclusive="2024-04-01",
            ),
            filters={"company_code": "ACME"},
        ),
    )

    with (
        patch("ledgerlingo.cli.load_settings", return_value=settings),
        patch(
            "ledgerlingo.cli.interpret_query",
            new_callable=AsyncMock,
            return_value=interpretation,
        ) as interpret,
        patch(
            "ledgerlingo.cli.process_question",
            new_callable=AsyncMock,
        ) as process_question,
    ):
        exit_code = main(["interpret", "What was gross profit in Q1 2024?"])

    assert exit_code == 0
    assert capsys.readouterr().out == interpretation.model_dump_json(indent=2) + "\n"
    interpret.assert_awaited_once_with(
        "What was gross profit in Q1 2024?",
        settings,
    )
    process_question.assert_not_awaited()


def test_interpret_command_requires_a_question(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as error:
        main(["interpret"])

    assert error.value.code == 2
    assert "question" in capsys.readouterr().err


def test_interpret_command_reports_dimension_lookup_failure(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with (
        patch("ledgerlingo.cli.load_settings", return_value=object()),
        patch(
            "ledgerlingo.cli.interpret_query",
            new_callable=AsyncMock,
            side_effect=DimensionLookupError(
                "Set LEDGERLINGO_READONLY_DATABASE_URL to a read-only PostgreSQL connection URL."
            ),
        ),
        pytest.raises(SystemExit) as error,
    ):
        main(["interpret", "What was gross profit?"])

    assert error.value.code == 1
    assert "LEDGERLINGO_READONLY_DATABASE_URL" in capsys.readouterr().err
