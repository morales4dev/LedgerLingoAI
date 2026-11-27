import asyncio
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from agents import ToolOutputText, function_tool
from agents.tool_context import ToolContext
from pydantic import BaseModel, field_validator

from ledgerlingo.agent import (
    AgentConfigurationError,
    AgentLoopLimitError,
    InvalidModelResponseError,
    run_agent,
)


def _tool_call(
    call_id: str = "call-1",
    name: str = "lookup",
    arguments: str = '{"key": "value"}',
) -> SimpleNamespace:
    return SimpleNamespace(
        id=call_id,
        function=SimpleNamespace(name=name, arguments=arguments),
    )


def _response(content: str | None = None, tool_calls: tuple = ()) -> SimpleNamespace:
    message = SimpleNamespace(content=content, tool_calls=list(tool_calls) or None)
    return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def _model_client(*responses: SimpleNamespace) -> Mock:
    client = Mock()
    client.chat.completions.create = AsyncMock(side_effect=responses)
    return client


@function_tool
async def lookup(key: str) -> str:
    """Look up a value by key."""
    return f"found {key}"


def test_run_agent_returns_final_model_output() -> None:
    client = _model_client(_response("The answer is 42."))
    settings = SimpleNamespace(model_name="test-model")

    answer = asyncio.run(run_agent("What is the answer?", settings, client))

    assert answer == "The answer is 42."
    client.chat.completions.create.assert_awaited_once()


def test_run_agent_dispatches_decorated_tool_and_sends_result() -> None:
    client = _model_client(_response(tool_calls=(_tool_call(),)), _response("Found it."))
    settings = SimpleNamespace(model_name="test-model")

    answer = asyncio.run(run_agent("Find this value.", settings, client, tools=(lookup,)))

    assert answer == "Found it."
    calls = client.chat.completions.create.call_args_list
    advertised = calls[0].kwargs["tools"][0]["function"]
    assert advertised["name"] == "lookup"
    assert advertised["description"] == lookup.description
    assert advertised["parameters"] == lookup.params_json_schema
    assert calls[1].kwargs["messages"][-1] == {
        "role": "tool", "tool_call_id": "call-1", "content": "found value",
    }


def test_run_agent_converts_structured_text_tool_output() -> None:
    @function_tool
    async def text_tool(key: str) -> ToolOutputText:
        """Return text output."""
        return ToolOutputText(text=key)

    client = _model_client(
        _response(tool_calls=(_tool_call(name="text_tool"),)), _response("done")
    )
    asyncio.run(
        run_agent("Question?", SimpleNamespace(model_name="test-model"), client, tools=(text_tool,))
    )

    assert client.chat.completions.create.call_args_list[1].kwargs["messages"][-1]["content"] == "value"


def test_run_agent_passes_sdk_tool_context_and_serializes_dict() -> None:
    @function_tool
    async def contextual(ctx: ToolContext[None], key: str) -> dict[str, str]:
        """Return the input and call identifier."""
        return {"key": key, "call_id": ctx.tool_call_id}

    client = _model_client(
        _response(tool_calls=(_tool_call(name="contextual"),)), _response("done")
    )
    asyncio.run(
        run_agent("Question?", SimpleNamespace(model_name="test-model"), client, tools=(contextual,))
    )
    result = client.chat.completions.create.call_args_list[1].kwargs["messages"][-1]["content"]
    assert json.loads(result) == {"key": "value", "call_id": "call-1"}


def test_run_agent_rejects_invalid_model_responses() -> None:
    client = _model_client(SimpleNamespace(choices=[]))

    with pytest.raises(InvalidModelResponseError, match="no choices"):
        asyncio.run(run_agent("Question?", SimpleNamespace(model_name="test-model"), client))


@pytest.mark.parametrize("arguments", ['not-json', '{"key": 42}', "{}"])
def test_run_agent_validates_all_tool_calls_before_dispatching(arguments: str) -> None:
    handler = Mock()

    @function_tool
    async def tracked(key: str) -> str:
        """Track calls."""
        handler(key)
        return "ok"

    client = _model_client(
        _response(tool_calls=(
            _tool_call(name="tracked"),
            _tool_call(call_id="call-2", name="tracked", arguments=arguments),
        ))
    )

    with pytest.raises(InvalidModelResponseError):
        asyncio.run(
            run_agent("Question?", SimpleNamespace(model_name="test-model"), client, tools=(tracked,))
        )

    handler.assert_not_called()


def test_run_agent_checks_custom_pydantic_validation_before_any_dispatch() -> None:
    class Input(BaseModel):
        key: str

        @field_validator("key")
        @classmethod
        def must_be_valid(cls, value: str) -> str:
            if value != "valid":
                raise ValueError("invalid key")
            return value

    handler = Mock()

    @function_tool
    async def tracked(input: Input) -> str:
        """Track calls with validated inputs."""
        handler(input)
        return "ok"

    client = _model_client(
        _response(tool_calls=(
            _tool_call(name="tracked", arguments='{"input":{"key":"valid"}}'),
            _tool_call(
                call_id="call-2", name="tracked",
                arguments='{"input":{"key":"invalid"}}',
            ),
        ))
    )
    with pytest.raises(InvalidModelResponseError, match="invalid"):
        asyncio.run(
            run_agent("Question?", SimpleNamespace(model_name="test-model"), client, tools=(tracked,))
        )
    handler.assert_not_called()


def test_run_agent_rejects_unknown_tool() -> None:
    client = _model_client(_response(tool_calls=(_tool_call(name="unknown"),)))

    with pytest.raises(InvalidModelResponseError, match="unknown tool"):
        asyncio.run(
            run_agent("Question?", SimpleNamespace(model_name="test-model"), client, tools=(lookup,))
        )


def test_tool_failure_is_raised_not_returned_as_model_result() -> None:
    @function_tool
    async def broken(key: str) -> str:
        """Always fail."""
        raise RuntimeError("tool failed")

    client = _model_client(_response(tool_calls=(_tool_call(name="broken"),)))

    with pytest.raises(RuntimeError, match="tool failed"):
        asyncio.run(
            run_agent("Question?", SimpleNamespace(model_name="test-model"), client, tools=(broken,))
        )
    client.chat.completions.create.assert_awaited_once()


def test_run_agent_rejects_unsupported_runner_features() -> None:
    @function_tool(needs_approval=True)
    async def approval_tool(key: str) -> str:
        """Requires approval."""
        return key

    with pytest.raises(AgentConfigurationError, match="approval"):
        asyncio.run(
            run_agent(
                "Question?", SimpleNamespace(model_name="test-model"), _model_client(),
                tools=(approval_tool,),
            )
        )


def test_run_agent_enforces_tool_call_limit() -> None:
    client = _model_client(
        _response(tool_calls=(_tool_call(),)),
        _response(tool_calls=(_tool_call(call_id="call-2"),)),
    )

    with pytest.raises(AgentLoopLimitError, match="tool call limit"):
        asyncio.run(
            run_agent(
                "Question?", SimpleNamespace(model_name="test-model"),
                client, tools=(lookup,), max_tool_calls=1,
            )
        )
