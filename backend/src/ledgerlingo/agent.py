import json
from collections.abc import Sequence
from copy import copy

from agents import FunctionTool, ToolOutputText
from agents.function_schema import function_schema
from agents.tool import set_function_tool_failure_error_function
from agents.tool_context import ToolContext
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from openai import AsyncOpenAI
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageFunctionToolCallParam,
    ChatCompletionMessageParam,
    ChatCompletionToolParam,
)
from pydantic import ValidationError

from ledgerlingo.config import Settings


class AgentError(RuntimeError):
    """Base error for explicit orchestration failures."""


class AgentConfigurationError(AgentError):
    """Raised when the workflow or its tool registry is invalid."""


class InvalidModelResponseError(AgentError):
    """Raised when the model response does not follow the expected protocol."""


class InvalidToolResultError(AgentError):
    """Raised when a tool result cannot be sent back to the model."""


class AgentLoopLimitError(AgentError):
    """Raised when the model exceeds the configured tool-call limit."""


async def run_agent(
    question: str,
    settings: Settings,
    client: AsyncOpenAI,
    tools: Sequence[FunctionTool] = (),
    *,
    system_prompt: str = "Answer clearly and use the provided tools when appropriate.",
    max_tool_calls: int = 5,
) -> str:
    """Run a bounded model/tool conversation and return its final text."""
    if not question.strip():
        raise AgentConfigurationError("The question must not be empty.")
    if max_tool_calls < 0:
        raise AgentConfigurationError("The tool-call limit must not be negative.")

    tools_by_name = {tool.name: tool for tool in tools}
    if len(tools_by_name) != len(tools):
        raise AgentConfigurationError("Tool names must be unique.")

    validators = {}
    tool_models = {}
    for tool in tools:
        if tool.needs_approval is not False:
            raise AgentConfigurationError("Tool approval is not supported.")
        if (
            tool.is_enabled is not True
            or tool.tool_input_guardrails
            or tool.tool_output_guardrails
            or tool.timeout_seconds is not None
            or tool.defer_loading
        ):
            raise AgentConfigurationError(
                f"Tool '{tool.name}' requires unsupported Runner features."
            )
        try:
            wrapped = tool.__wrapped__
        except AttributeError:
            raise AgentConfigurationError(
                f"Tool '{tool.name}' must be created with @function_tool."
            ) from None
        try:
            Draft202012Validator.check_schema(tool.params_json_schema)
        except SchemaError:
            raise AgentConfigurationError(
                f"Tool '{tool.name}' has an invalid argument schema."
            ) from None
        validators[tool.name] = Draft202012Validator(tool.params_json_schema)
        tool_models[tool.name] = function_schema(
            wrapped, strict_json_schema=tool.strict_json_schema
        ).params_pydantic_model

    tools_by_name = {
        tool.name: set_function_tool_failure_error_function(copy(tool), None)
        for tool in tools
    }

    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]
    calls_used = 0

    for turn in range(max_tool_calls + 1):
        if tools:
            advertised_tools: list[ChatCompletionToolParam] = [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.params_json_schema,
                        "strict": tool.strict_json_schema,
                    },
                }
                for tool in tools
            ]
            completion = await client.chat.completions.create(
                model=settings.model_name,
                messages=messages,
                tools=advertised_tools,
                tool_choice="auto",
            )
        else:
            completion = await client.chat.completions.create(
                model=settings.model_name, messages=messages
            )
        choices = getattr(completion, "choices", None)
        if not choices:
            raise InvalidModelResponseError("The model response contained no choices.")

        message = getattr(choices[0], "message", None)
        if message is None:
            raise InvalidModelResponseError("The model response contained no message.")

        tool_calls = getattr(message, "tool_calls", None) or []
        if tool_calls:
            if not isinstance(tool_calls, list):
                raise InvalidModelResponseError(
                    "The model returned invalid tool calls."
                )
            if calls_used + len(tool_calls) > max_tool_calls:
                raise AgentLoopLimitError("The model exceeded the tool call limit.")

            assistant_message: ChatCompletionAssistantMessageParam = {"role": "assistant"}
            content = getattr(message, "content", None)
            if content is not None:
                if not isinstance(content, str):
                    raise InvalidModelResponseError(
                        "The model returned non-text message content."
                    )
                assistant_message["content"] = content

            validated_calls: list[tuple[str, str, str]] = []
            serialized_calls: list[ChatCompletionMessageFunctionToolCallParam] = []
            for call in tool_calls:
                call_id = getattr(call, "id", None)
                function = getattr(call, "function", None)
                name = getattr(function, "name", None)
                arguments_json = getattr(function, "arguments", None)
                if (
                    not isinstance(call_id, str)
                    or not call_id
                    or not isinstance(name, str)
                    or not name
                ):
                    raise InvalidModelResponseError(
                        "The model returned an invalid tool call."
                    )
                if not isinstance(arguments_json, str):
                    raise InvalidModelResponseError(
                        "The model returned invalid tool arguments."
                    )

                if name not in tools_by_name:
                    raise InvalidModelResponseError(
                        f"The model requested unknown tool '{name}'."
                    )
                try:
                    arguments = json.loads(arguments_json)
                except json.JSONDecodeError:
                    raise InvalidModelResponseError(
                        f"The model returned invalid JSON arguments "
                        f"for tool '{name}'."
                    ) from None
                if not isinstance(arguments, dict):
                    raise InvalidModelResponseError(
                        f"The model arguments for tool '{name}' "
                        "must be an object."
                    )

                if not validators[name].is_valid(arguments):
                    raise InvalidModelResponseError(
                        f"The model arguments for tool '{name}' do not match its schema."
                    )
                try:
                    tool_models[name].model_validate(arguments)
                except ValidationError:
                    raise InvalidModelResponseError(
                        f"The model arguments for tool '{name}' are invalid."
                    ) from None

                validated_calls.append((call_id, name, arguments_json))
                serialized_calls.append(
                    {
                        "id": call_id,
                        "type": "function",
                        "function": {"name": name, "arguments": arguments_json},
                    }
                )

            assistant_message["tool_calls"] = serialized_calls
            messages.append(assistant_message)
            calls_used += len(validated_calls)

            for call_id, name, arguments_json in validated_calls:
                tool = tools_by_name[name]
                context = ToolContext(
                    context=None,
                    tool_name=name,
                    tool_call_id=call_id,
                    tool_arguments=arguments_json,
                )
                output = await tool.on_invoke_tool(context, arguments_json)
                if isinstance(output, ToolOutputText):
                    output = output.text
                try:
                    result = (
                        output if isinstance(output, str)
                        else json.dumps(output, ensure_ascii=False)
                    )
                except (TypeError, ValueError) as error:
                    raise InvalidToolResultError(
                        f"Tool '{name}' returned a value that is not JSON "
                        "serializable."
                    ) from error
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call_id,
                        "content": result,
                    }
                )
            if turn == max_tool_calls:
                raise AgentLoopLimitError(
                    "The model did not return a final response before "
                    "the tool call limit."
                )
            continue

        content = getattr(message, "content", None)
        if isinstance(content, str) and content.strip():
            return content
        raise InvalidModelResponseError(
            "The model response contained neither text nor tool calls."
        )

    raise AgentLoopLimitError(
        "The model did not return a final response before the tool call limit."
    )
