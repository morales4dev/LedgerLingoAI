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

Copy `.env.example` to `.env` at the **repo root** (one directory above this file). Set `MODEL_NAME` to a LiteLLM provider/model identifier and set that provider's API key, such as `OPENAI_API_KEY`. For dimension discovery, also set `LEDGERLINGO_READONLY_DATABASE_URL` to a PostgreSQL connection URL whose database role has read-only access. The adapter limits its sessions to read-only transactions and only issues allowlisted, parameterized `SELECT` queries. `.env` is gitignored.

## Run

From this directory:

```bash
uv run --locked ledgerlingo "Ask one English question here"
```

The CLI is the MVP caller: one invocation submits one English question, calls the application orchestrator, and prints one English result. LiteLLM makes async model calls within that invocation without a separately managed client. The interpreter uses bounded discovery tools and returns a structured query, clarification, or unsupported outcome; the orchestrator returns clarification and unsupported messages directly, and otherwise validates the query, calls the deterministic calculator, and reports its result.

Developers can inspect the typed interpretation without running validation, calculation, or reporting:

```bash
uv run --locked ledgerlingo interpret "What was gross profit for ACME in Q1 2024?"
```

This command prints a JSON `query`, `clarification`, or `unsupported` outcome. Query JSON uses logical metric and dimension IDs and includes the normalized start-inclusive/end-exclusive period; the command does not produce a financial answer. The normal `ledgerlingo "question"` invocation remains the one-question/one-English-response path.

On handled provider or runtime failures, the normal command writes a concise diagnostic hint to stderr while keeping the user-facing response unchanged. Add `--debug` to either command to print the full exception traceback:

```bash
uv run --locked ledgerlingo --debug "Ask one English question here"
uv run --locked ledgerlingo interpret --debug "What was gross profit for ACME in Q1 2024?"
```

Tracebacks can contain provider or connection details; redact them before sharing.

The current validator is a stub that always returns valid, and the calculator is a stub that always returns `68`. These results are demonstrative and are not calculated from journal entries. The interpreter can use the logical catalog, normalized calendar, and bounded read-only dimension-member lookups, but it does not retrieve journal entries or calculation results. Clarification, unsupported, and safe processing-failure outcomes are returned without waiting for another input. The validator is not exposed as an agent tool.

The lower-level agent loop can still dispatch explicit `@function_tool`-decorated functions, validates their arguments, and bounds tool iterations. Runner-managed approvals, guardrails, dynamic enablement, tool timeouts, and deferred loading are not supported.

## Test

From this directory:

```bash
uv run --locked python -m pytest
```

Offline unit tests live in `tests/unit/` and mock model responses; they do not require provider credentials or network access. They cover configured provider routing, the one-shot English contract, clarification, unsupported and failure outcomes, internal tool iteration, and isolation across consecutive invocations. A live provider smoke test is optional and requires provider credentials.

An optional interpretation evaluation compares live provider outputs with the logical fields in the golden set without asserting exact wording. Enable it explicitly with configured provider credentials:

```bash
LEDGERLINGO_RUN_LIVE_INTERPRETATION_EVAL=1 uv run --locked python -m pytest tests/integration/test_live_interpretation.py
```
