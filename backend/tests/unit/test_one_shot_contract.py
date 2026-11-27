import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

from agents import function_tool

from ledgerlingo.agent import PROCESSING_FAILURE_RESPONSE, answer_question, run_agent


def _response(content: str | None = None, tool_calls: tuple = ()) -> SimpleNamespace:
    message = SimpleNamespace(content=content, tool_calls=list(tool_calls) or None)
    return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def _model_client(*responses: SimpleNamespace) -> Mock:
    client = Mock()
    client.chat.completions.create = AsyncMock(side_effect=responses)
    return client


def test_invocation_sends_english_instruction_and_returns_english_fixture() -> None:
    question = "What is the current accounts receivable balance?"
    fixture = "The current accounts receivable balance is 1,200,000 dollars."
    client = _model_client(_response(fixture))
    settings = SimpleNamespace(model_name="test-model")

    answer = asyncio.run(run_agent(question, settings, client))

    assert answer == fixture
    messages = client.chat.completions.create.call_args.kwargs["messages"]
    assert messages[0]["role"] == "system"
    assert "English" in messages[0]["content"]
    assert messages[1] == {"role": "user", "content": question}
    assert client.chat.completions.create.await_count == 1


def _tool_call(
    call_id: str, name: str, arguments: str
) -> SimpleNamespace:
    return SimpleNamespace(
        id=call_id,
        function=SimpleNamespace(name=name, arguments=arguments),
    )


@function_tool
async def lookup_metric(name: str) -> str:
    """Look up a metric value by name."""
    return f"{name}=10"


@function_tool
async def lookup_period(label: str) -> str:
    """Look up a reporting period by label."""
    return f"{label}=2024"


def test_multiple_internal_tool_steps_return_one_caller_result() -> None:
    fixture = "EBITDA is 10 for the 2024 period."
    responses = [
        _response(
            tool_calls=(
                _tool_call("call-1", "lookup_metric", '{"name": "EBITDA"}'),
            )
        ),
        _response(
            tool_calls=(
                _tool_call("call-2", "lookup_period", '{"label": "current"}'),
            )
        ),
        _response(fixture),
    ]
    captured_messages = []
    client = Mock()

    async def create(**kwargs):
        captured_messages.append(list(kwargs["messages"]))
        return responses[len(captured_messages) - 1]

    client.chat.completions.create = AsyncMock(side_effect=create)
    settings = SimpleNamespace(model_name="test-model")

    answer = asyncio.run(
        run_agent(
            "What is EBITDA for the current period?",
            settings,
            client,
            tools=(lookup_metric, lookup_period),
        )
    )

    assert answer == fixture
    assert isinstance(answer, str)
    assert len(captured_messages) == 3
    assert captured_messages[1][-1] == {
        "role": "tool",
        "tool_call_id": "call-1",
        "content": "EBITDA=10",
    }
    assert captured_messages[2][-1] == {
        "role": "tool",
        "tool_call_id": "call-2",
        "content": "current=2024",
    }
    assert answer not in str(captured_messages[1][-1])


def test_clarification_returns_one_english_response_without_waiting() -> None:
    question = "What is the receivables balance?"
    fixture = (
        "Please specify the reporting period so the receivables balance can be answered."
    )
    client = _model_client(_response(fixture))

    answer = asyncio.run(
        answer_question(question, SimpleNamespace(model_name="test-model"), client)
    )

    assert answer == fixture
    assert client.chat.completions.create.await_count == 1


def test_unsupported_question_returns_one_english_response_without_waiting() -> None:
    question = "Write a poem about the weather."
    fixture = (
        "This question is unsupported. LedgerLingoAI answers analytical "
        "questions about accounting data."
    )
    client = _model_client(_response(fixture))

    answer = asyncio.run(
        answer_question(question, SimpleNamespace(model_name="test-model"), client)
    )

    assert answer == fixture
    assert client.chat.completions.create.await_count == 1


def test_processing_failure_returns_english_outcome_not_unvalidated_answer() -> None:
    client = _model_client(SimpleNamespace(choices=[]))

    answer = asyncio.run(
        answer_question(
            "What is EBITDA?", SimpleNamespace(model_name="test-model"), client
        )
    )

    assert answer == PROCESSING_FAILURE_RESPONSE
    assert "EBITDA" not in answer
    assert client.chat.completions.create.await_count == 1


def test_consecutive_invocations_do_not_reuse_prior_question_or_response() -> None:
    first_question = "What is the current accounts receivable balance?"
    first_fixture = "The current accounts receivable balance is 1,200,000 dollars."
    second_question = "What is EBITDA for 2024?"
    second_fixture = "EBITDA for 2024 is 10."
    captured_messages = []
    responses = [_response(first_fixture), _response(second_fixture)]
    client = Mock()

    async def create(**kwargs):
        captured_messages.append(list(kwargs["messages"]))
        return responses[len(captured_messages) - 1]

    client.chat.completions.create = AsyncMock(side_effect=create)
    settings = SimpleNamespace(model_name="test-model")

    first_answer = asyncio.run(answer_question(first_question, settings, client))
    second_answer = asyncio.run(answer_question(second_question, settings, client))

    assert first_answer == first_fixture
    assert second_answer == second_fixture
    assert len(captured_messages) == 2
    second_payload = captured_messages[1]
    assert second_payload[1] == {"role": "user", "content": second_question}
    assert first_question not in str(second_payload)
    assert first_fixture not in str(second_payload)
    assert first_answer not in str(second_payload)
