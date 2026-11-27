# LedgerLingoAI Architecture Proposal

## Purpose

LedgerLingoAI is a governed analytics assistant for accounting and finance professionals. The MVP first proves the request-to-answer workflow from a local Python script. It accepts one English text question per invocation and returns one English text response; internal model and tool iterations remain within that invocation.

The analytics contract, approved data assets, and business definitions remain explicit and independently reviewable. The model coordinates the workflow but does not define business truth or bypass validation.

## MVP Architecture

```text
One English text question
      |
Python script / CLI
      |
One independent invocation
      |  agent iterations
      |  tool calls/results as needed
      |
Importable async Python orchestrator
      |
      +--> Agents SDK function tools (approved tools only)
      |
Async OpenAI SDK client
      |
LiteLLM Proxy (OpenAI-compatible endpoint)
      |
Configured model provider
      |
One English text result
```

The script is the only current caller. Each invocation is independent: it does not receive a prior question, prior response, or request-history identifier. The proxy is a separate local process and keeps provider routing outside the application.

## Component Responsibilities

- **CLI script:** accepts one English question, starts one invocation, closes the client, and prints or logs one English result.
- **Python orchestrator:** owns model requests, tool dispatch, tool-result messages, and the bounded request loop. Internal iterations are not additional caller inputs or outputs. The MVP invocation returns one English result, including clarification, unsupported, and processing-failure outcomes.
- **Tool boundary:** exposes only explicitly registered `@function_tool` functions. The Agents SDK generates schemas and invokes functions; the application validates each batch before dispatch. Analytics tools and their governance are added through separate product changes.
- **Configuration boundary:** loads environment-backed settings and safely parses YAML before validating it with Pydantic.
- **OpenAI SDK client:** `AsyncOpenAI` communicates with the proxy through its OpenAI-compatible API. Application modules do not import LiteLLM.
- **LiteLLM Proxy:** routes requests to the configured provider and owns provider credentials.

## Runtime Stack

- Python 3.12 and 3.13, managed with uv in `backend/.venv`.
- Direct application dependencies and development tools in `backend/pyproject.toml`, locked in `backend/uv.lock`.
- Pydantic and `python-dotenv` for validated environment settings; PyYAML's safe loader for declarative YAML.
- The async OpenAI SDK client for model requests and the OpenAI Agents SDK for function tool definitions and invocation.
- JSON Schema and Pydantic validation of tool arguments before dispatch.
- LiteLLM Proxy in a separate optional uv dependency group for local development.
- Pytest unit tests that mock model transport and do not require a live provider.

## Request Lifecycle

1. The script validates that one English question was supplied.
2. The application loads proxy URL, proxy credential, and model name from the environment.
3. The orchestrator sends the current question and registered tool definitions to the selected model through the proxy.
4. The orchestrator validates the full batch of tool requests, awaits each registered SDK tool, and appends its result to the same invocation.
5. The bounded loop ends with one English text result. If the question needs clarification, is unsupported, or cannot be processed safely, that outcome is the returned result; the invocation does not wait for another input.
6. The script prints that result and exits. A later question is a new invocation and does not reuse the previous question or response.

## Governance and Security

The model may interpret a question and request registered tools, but approved analytics assets, definitions, and query safety remain governed outside the model. Credentials are environment-only: the application uses a proxy key, while provider keys remain on the proxy side. Example configuration files contain variable names and non-secret local placeholders only.

The orchestration loop has a finite tool-call limit. Invalid responses, malformed tool arguments, unknown tools, tool failures, and non-serializable tool results are not presented as unvalidated answers; the caller receives one English description of the failed outcome. The SDK Runner is not used: its approvals, guardrails, dynamic enablement, timeouts, and deferred tool loading are not supported by this adapter.

## Deferred Scope

The MVP does not add a web UI, API, hosted service, stateful chat, or multi-user runtime. A client or API adapter may be considered only after the one-shot script workflow and governed analytics behavior are validated. Its form and timing remain undecided.

This architecture change establishes the execution boundary; it does not add analytics metrics, database access, or product-facing behavior.
