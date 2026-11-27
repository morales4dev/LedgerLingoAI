# LedgerLingoAI backend

Operator runbook for the Python agent core.

## Stack

Python 3.12-3.13. Dependencies and supported Python versions are declared in `pyproject.toml`, with exact resolutions in `uv.lock`. The local environment is `.venv`.

The importable async agent core and CLI live under `src/ledgerlingo/`. The async OpenAI SDK client connects to the separately run LiteLLM Proxy. Tools are defined with the OpenAI Agents SDK's `@function_tool`; an explicit Python loop dispatches them without the SDK Runner.

## Setup

The backend environment lives at `.venv` and is managed by uv. From this directory (`backend/`):

```bash
uv sync --locked
```

To run the local model proxy as well, sync its separate dependency group:

```bash
uv sync --locked --group proxy
```

Copy `.env.example` to `.env` at the **repo root** (one directory above this file) and set the provider key. `.env` is gitignored.

Start the LiteLLM Proxy from this directory:

```bash
uv run --locked --group proxy --env-file ../.env litellm --config litellm_config.yaml --port 4000
```

The example sets `LITELLM_PROXY_URL=http://localhost:4000/v1`, the OpenAI-compatible endpoint used by the app. Check that the proxy is live with `curl http://localhost:4000/health/liveliness`.

## Run

From this directory:

```bash
uv run --locked ledgerlingo "Ask one question here"
```

The CLI starts and closes the async client for each invocation. It does not register analytics tools yet. Python callers can pass an explicit sequence of `@function_tool`-decorated functions to `run_agent`; the loop validates arguments and propagates tool failures. Runner-managed approvals, guardrails, dynamic enablement, tool timeouts, and deferred loading are not supported.

## Test

From this directory:

```bash
uv run --locked python -m pytest
```

Offline unit tests live in `tests/unit/` and mock model responses; they do not require provider credentials or network access.
