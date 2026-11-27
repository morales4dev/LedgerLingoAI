from unittest.mock import AsyncMock, patch

import pytest

from ledgerlingo.agent import PROCESSING_FAILURE_RESPONSE
from ledgerlingo.cli import main
from ledgerlingo.config import SettingsError


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
    process_question.assert_awaited_once_with("What is the result?", settings)


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

