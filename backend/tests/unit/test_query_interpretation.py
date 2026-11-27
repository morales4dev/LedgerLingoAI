import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from ledgerlingo.agent import InvalidModelResponseError, interpret_query
from ledgerlingo.models import (
    QueryInterpretation,
    StructuredQuery,
)


def _client(content: str) -> Mock:
    message = SimpleNamespace(content=content, tool_calls=None)
    completion = SimpleNamespace(choices=[SimpleNamespace(message=message)])
    client = Mock()
    client.chat.completions.create = AsyncMock(return_value=completion)
    return client


def test_interpret_query_returns_structured_query_from_model_json() -> None:
    question = "What was revenue in 2024?"
    client = _client(
        '{"kind":"query","query":{"metric":"revenue","period":"2024","filters":{}}}'
    )

    interpretation = asyncio.run(
        interpret_query(question, SimpleNamespace(model_name="test-model"), client)
    )

    assert interpretation == QueryInterpretation(
        kind="query",
        query=StructuredQuery(metric="revenue", period="2024"),
    )
    request = client.chat.completions.create.call_args.kwargs
    assert request["messages"][1] == {"role": "user", "content": question}
    assert "tools" not in request


def test_interpret_query_returns_clarification_outcome() -> None:
    client = _client(
        '{"kind":"clarification","clarification":"Which reporting period?"}'
    )

    interpretation = asyncio.run(
        interpret_query(
            "What is the revenue?", SimpleNamespace(model_name="test-model"), client
        )
    )

    assert interpretation.kind == "clarification"
    assert interpretation.clarification == "Which reporting period?"
    assert interpretation.query is None


@pytest.mark.parametrize(
    "content",
    (
        "not-json",
        '{"kind":"query","query":{"metric":"","period":null,"filters":{}}}',
        '{"kind":"unknown"}',
        '{"kind":"clarification","clarification":""}',
        '{"kind":"query","query":{"metric":"revenue"},"clarification":"Which period?"}',
    ),
)
def test_interpret_query_rejects_malformed_or_invalid_model_output(
    content: str,
) -> None:
    with pytest.raises(InvalidModelResponseError, match="invalid query interpretation"):
        asyncio.run(
            interpret_query(
                "Question?", SimpleNamespace(model_name="test-model"), _client(content)
            )
        )
