from unittest.mock import AsyncMock, patch

import pytest

from ledgerlingo.agent import PROCESSING_FAILURE_RESPONSE
from ledgerlingo.cli import main
from ledgerlingo.config import SettingsError


def test_main_runs_question_invokes_core_once_and_prints_one_response(
    capsys: pytest.CaptureFixture[str],
) -> None:
    settings = object()
    client = AsyncMock()
    client.__aenter__.return_value = client

    with (
        patch("ledgerlingo.cli.load_settings", return_value=settings),
        patch("ledgerlingo.cli.create_client", return_value=client),
        patch(
            "ledgerlingo.cli.answer_question",
            new_callable=AsyncMock,
            return_value="The result is 42.",
        ) as answer_question,
    ):
        exit_code = main(["What is the result?"])

    assert exit_code == 0
    assert capsys.readouterr().out == "The result is 42.\n"
    answer_question.assert_awaited_once_with("What is the result?", settings, client)
    client.__aexit__.assert_awaited_once()


def test_main_prints_one_processing_failure_response_and_closes_client(
    capsys: pytest.CaptureFixture[str],
) -> None:
    client = AsyncMock()
    client.__aenter__.return_value = client

    with (
        patch("ledgerlingo.cli.load_settings", return_value=object()),
        patch("ledgerlingo.cli.create_client", return_value=client),
        patch(
            "ledgerlingo.cli.answer_question",
            new_callable=AsyncMock,
            return_value=PROCESSING_FAILURE_RESPONSE,
        ),
    ):
        exit_code = main(["What is EBITDA?"])

    assert exit_code == 0
    assert capsys.readouterr().out == f"{PROCESSING_FAILURE_RESPONSE}\n"
    client.__aexit__.assert_awaited_once()


def test_main_closes_client_when_settings_fail(
    capsys: pytest.CaptureFixture[str],
) -> None:
    client = AsyncMock()
    client.__aenter__.return_value = client
    with (
        patch(
            "ledgerlingo.cli.load_settings",
            side_effect=SettingsError(
                "Invalid settings; check required values: MODEL_NAME."
            ),
        ),
        pytest.raises(SystemExit) as error,
    ):
        main(["Question?"])

    assert error.value.code == 1
    assert "MODEL_NAME" in capsys.readouterr().err
    client.__aenter__.assert_not_awaited()


def test_main_requires_a_question(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as error:
        main([])

    assert error.value.code == 2
    assert "question" in capsys.readouterr().err

