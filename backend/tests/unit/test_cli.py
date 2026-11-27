from unittest.mock import AsyncMock, patch

import pytest

from ledgerlingo.cli import main


def test_main_runs_question_and_prints_answer(capsys: pytest.CaptureFixture[str]) -> None:
    settings = object()
    client = AsyncMock()
    client.__aenter__.return_value = client

    with (
        patch("ledgerlingo.cli.load_settings", return_value=settings),
        patch("ledgerlingo.cli.create_client", return_value=client),
        patch(
            "ledgerlingo.cli.run_agent",
            new_callable=AsyncMock,
            return_value="Answer text.",
        ) as run_agent,
    ):
        exit_code = main(["What is the result?"])

    assert exit_code == 0
    assert capsys.readouterr().out == "Answer text.\n"
    run_agent.assert_awaited_once_with("What is the result?", settings, client)
    client.__aexit__.assert_awaited_once()


def test_main_closes_client_when_agent_fails(capsys: pytest.CaptureFixture[str]) -> None:
    from ledgerlingo.agent import InvalidModelResponseError

    client = AsyncMock()
    client.__aenter__.return_value = client
    with (
        patch("ledgerlingo.cli.load_settings", return_value=object()),
        patch("ledgerlingo.cli.create_client", return_value=client),
        patch(
            "ledgerlingo.cli.run_agent",
            new_callable=AsyncMock,
            side_effect=InvalidModelResponseError("bad response"),
        ),
        pytest.raises(SystemExit) as error,
    ):
        main(["Question?"])

    assert error.value.code == 1
    assert "bad response" in capsys.readouterr().err
    client.__aexit__.assert_awaited_once()


def test_main_requires_a_question(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as error:
        main([])

    assert error.value.code == 2
    assert "question" in capsys.readouterr().err
