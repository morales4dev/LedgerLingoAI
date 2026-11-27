import asyncio
from unittest.mock import AsyncMock

import pytest
from openai import OpenAIError

from ledgerlingo.client import ModelProviderError, complete_model
from ledgerlingo.config import Settings


def test_complete_model_uses_configured_provider_and_model() -> None:
    settings = Settings(model_name="openai/gpt-4o-mini")
    messages = [{"role": "user", "content": "What is the answer?"}]
    response = object()
    completion = AsyncMock(return_value=response)

    result = asyncio.run(
        complete_model(settings, messages, completion=completion)
    )

    completion.assert_awaited_once_with(
        model="openai/gpt-4o-mini",
        messages=messages,
    )
    assert result is response


def test_complete_model_redacts_provider_error_details() -> None:
    completion = AsyncMock(side_effect=OpenAIError("provider-secret-detail"))

    with pytest.raises(
        ModelProviderError,
        match="The configured model provider request failed.",
    ) as error:
        asyncio.run(
            complete_model(
                Settings(model_name="openai/gpt-4o-mini"),
                [{"role": "user", "content": "Question?"}],
                completion=completion,
            )
        )

    assert "provider-secret-detail" not in str(error.value)
