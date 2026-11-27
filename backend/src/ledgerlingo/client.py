from collections.abc import Awaitable, Callable, Sequence

from litellm import acompletion
from litellm.types.utils import ModelResponse
from openai import OpenAIError
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam

from ledgerlingo.config import Settings

CompletionCall = Callable[..., Awaitable[ModelResponse]]

class ModelProviderError(RuntimeError):
    """Raised when the configured model provider cannot complete a request."""


async def complete_model(
    settings: Settings,
    messages: Sequence[ChatCompletionMessageParam],
    *,
    tools: Sequence[ChatCompletionToolParam] | None = None,
    tool_choice: str | None = None,
    completion: CompletionCall = acompletion,
) -> ModelResponse:
    """Call the configured provider through LiteLLM's async SDK."""
    request: dict[str, object] = {
        "model": settings.model_name,
        "messages": list(messages),
    }
    if tools is not None:
        request["tools"] = list(tools)
    if tool_choice is not None:
        request["tool_choice"] = tool_choice

    try:
        return await completion(**request)
    except OpenAIError as error:
        raise ModelProviderError(
            "The configured model provider request failed."
        ) from error
