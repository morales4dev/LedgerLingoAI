import asyncio
import json
from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from ledgerlingo.agent import InvalidModelResponseError, interpret_query
from ledgerlingo.calendar import load_calendar_config
from ledgerlingo.discovery_tools import create_discovery_tools
from ledgerlingo.dimension_lookup import DimensionMemberResolution
from ledgerlingo.models import (
    QueryInterpretation,
)


def _client(content: str) -> AsyncMock:
    return AsyncMock(return_value=_completion(content=content))


def _completion(
    content: str | None = None,
    tool_calls: list[object] | None = None,
) -> object:
    message = SimpleNamespace(content=content, tool_calls=tool_calls)
    return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def _tool_call(name: str, arguments: dict[str, object], call_id: str) -> object:
    return SimpleNamespace(
        id=call_id,
        type="function",
        function=SimpleNamespace(name=name, arguments=json.dumps(arguments)),
    )


def _tool_completion(name: str, arguments: dict[str, object], call_id: str) -> object:
    message = SimpleNamespace(
        content=None,
        tool_calls=[_tool_call(name, arguments, call_id)],
    )
    return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def test_interpret_query_returns_structured_query_from_model_json() -> None:
    question = "What was revenue in 2024?"
    client = _client(
        '{"kind":"query","query":{"metrics":["gross_profit"],"period":'
        '{"kind":"fiscal_year","label":"FY2024","start_date":"2024-01-01",'
        '"end_date_exclusive":"2025-01-01"},"group_by":[],"filters":'
        '{"company_code":"ACME"},"time_grain":null}}'
    )

    interpretation = asyncio.run(
        interpret_query(question, SimpleNamespace(model_name="test-model"), client)
    )

    assert interpretation == QueryInterpretation(
        kind="query",
        query={
            "metrics": ["gross_profit"],
            "period": {
                "kind": "fiscal_year",
                "label": "FY2024",
                "start_date": "2024-01-01",
                "end_date_exclusive": "2025-01-01",
            },
            "group_by": [],
            "filters": {"company_code": "ACME"},
            "time_grain": None,
        },
    )
    request = client.call_args.kwargs
    assert request["messages"][1] == {"role": "user", "content": question}
    assert {tool["function"]["name"] for tool in request["tools"]} == {
        "search_analytics_catalog",
        "resolve_reporting_period",
        "resolve_dimension_member",
        "resolve_company_scope",
    }


def test_interpret_query_uses_discovery_tools_for_supported_query() -> None:
    dimension_lookup = Mock()
    dimension_lookup.company_code_candidates.return_value = ("ACME",)
    tools = create_discovery_tools(
        calendar=load_calendar_config(),
        reference_date_provider=lambda: date(2024, 5, 3),
        dimension_lookup=dimension_lookup,
    )
    client = AsyncMock(
        side_effect=[
            _tool_completion(
                "search_analytics_catalog",
                {"search_term": "gross profit"},
                "call-1",
            ),
            _tool_completion(
                "resolve_reporting_period",
                {"period": "Q1 2024"},
                "call-2",
            ),
            _tool_completion(
                "resolve_company_scope",
                {},
                "call-3",
            ),
            _completion(
                '{"kind":"query","query":{"metrics":["gross_profit"],'
                '"period":{"kind":"calendar_quarter","label":"Q1 2024",'
                '"start_date":"2024-01-01","end_date_exclusive":"2024-04-01"},'
                '"group_by":[],"filters":{"company_code":"ACME"},'
                '"time_grain":null}}'
            ),
        ]
    )

    interpretation = asyncio.run(
        interpret_query(
            "What was gross profit in Q1 2024?",
            SimpleNamespace(model_name="test-model"),
            client,
            tools,
        )
    )

    assert interpretation.kind == "query"
    assert interpretation.query is not None
    assert interpretation.query.metrics == ["gross_profit"]
    assert interpretation.query.filters == {"company_code": "ACME"}
    assert client.await_count == 4
    dimension_lookup.company_code_candidates.assert_called_once_with()


def test_interpret_query_clarifies_ambiguous_dimension_lookup() -> None:
    dimension_lookup = Mock()
    dimension_lookup.resolve_dimension_member.return_value = DimensionMemberResolution(
        dimension_id="cost_center",
        query="North",
        status="ambiguous",
        candidates=["NORTH-1", "NORTH-2"],
    )
    tools = create_discovery_tools(dimension_lookup=dimension_lookup)
    client = AsyncMock(
        side_effect=[
            _tool_completion(
                "resolve_dimension_member",
                {"dimension_id": "cost_center", "search_term": "North"},
                "call-1",
            ),
            _completion(
                '{"kind":"clarification",'
                '"clarification":"Which North cost center do you mean?"}'
            ),
        ]
    )

    interpretation = asyncio.run(
        interpret_query(
            "Show gross profit for North.",
            SimpleNamespace(model_name="test-model"),
            client,
            tools,
        )
    )

    assert interpretation.kind == "clarification"
    assert "Which North cost center" in interpretation.clarification
    dimension_lookup.resolve_dimension_member.assert_called_once_with(
        "cost_center",
        "North",
    )


def test_interpret_query_returns_unsupported_outcome() -> None:
    client = _client(
        '{"kind":"unsupported","unsupported":"Ranking is outside the MVP scope."}'
    )

    interpretation = asyncio.run(
        interpret_query(
            "Rank customers by revenue.",
            SimpleNamespace(model_name="test-model"),
            client,
        )
    )

    assert interpretation.kind == "unsupported"
    assert interpretation.unsupported == "Ranking is outside the MVP scope."


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
        '{"kind":"query","query":{"metrics":[],"period":null,"filters":{}}}',
        '{"kind":"unknown"}',
        '{"kind":"clarification","clarification":""}',
        '{"kind":"query","query":{"metrics":["gross_profit"],"period":null,'
        '"filters":{}},"clarification":"Which period?"}',
        '{"kind":"unsupported","unsupported":""}',
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
