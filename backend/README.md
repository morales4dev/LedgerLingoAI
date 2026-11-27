# LedgerLingoAI backend

Operator runbook for the Python agent core.

## Stack

Python 3.12-3.13. Dependencies and supported Python versions are declared in `pyproject.toml`, with exact resolutions in `uv.lock`. The local environment is `.venv`.

The importable async agent core and CLI live under `src/ledgerlingo/`. The application uses LiteLLM's async Python SDK to call the configured provider directly. Tools are defined with the OpenAI Agents SDK's `@function_tool`; an explicit Python loop dispatches them without the SDK Runner.

## Setup

The backend environment lives at `.venv` and is managed by uv. From this directory (`backend/`):

```bash
uv sync --locked
```

Copy `.env.example` to `.env` at the **repo root** (one directory above this file). Set `MODEL_NAME` to a LiteLLM provider/model identifier and set that provider's API key, such as `OPENAI_API_KEY`. `.env` is gitignored.

## Run

From this directory:

```bash
uv run --locked ledgerlingo "Ask one English question here"
```

The CLI is the MVP caller: one invocation submits one English question, calls the application orchestrator, and prints one English result. LiteLLM makes async model calls within that invocation without a separately managed client. The query interpreter returns either a structured query or a clarification; the orchestrator returns clarifications directly and otherwise validates the query, calls the deterministic calculator, and reports its result.

The current validator is a stub that always returns valid, and the calculator is a stub that always returns `68`. These results are demonstrative and are not calculated from journal data. The query interpreter receives the question but no journal data or calculator result; the natural-language question is sent to the configured model. Clarification and safe processing-failure outcomes are returned without waiting for another input. The validator is not yet exposed as an agent tool.

The lower-level agent loop can still dispatch explicit `@function_tool`-decorated functions, validates their arguments, and bounds tool iterations. Runner-managed approvals, guardrails, dynamic enablement, tool timeouts, and deferred loading are not supported.

## Test

From this directory:

```bash
uv run --locked python -m pytest
```

Offline unit tests live in `tests/unit/` and mock model responses; they do not require provider credentials or network access. They cover configured provider routing, the one-shot English contract, clarification, unsupported and failure outcomes, internal tool iteration, and isolation across consecutive invocations. A live provider smoke test is optional and requires provider credentials.
