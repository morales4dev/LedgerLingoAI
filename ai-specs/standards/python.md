# Python

## Layer 1 — generic small Python

- Type hints on new and changed public functions.
- Use Pydantic at non-LLM Python boundaries such as configuration objects and parsed JSON. Declare Pydantic dependencies directly in `backend/pyproject.toml` when application code requires them.
- Do not invent APIs, SDK methods, or library behavior. If it is not in the pin or Context7, do not guess.
- SOLID, DRY, PEP 8.
- Named errors; do not swallow with bare `except`.
- Validate input at boundaries.
- Structured logs (event + fields), not ad-hoc print for new operational logging.
- Early return; keep the happy path unindented.
- Secrets stay in env (`.env` gitignored). Names only in `.env.example`. Never commit secrets.

## Layer 2 — LedgerLingoAI stack

- Layout: importable core under `backend/src/ledgerlingo/`, tests under `backend/tests/unit/`, environment at `backend/.venv`.
- Declare direct dependencies and supported Python versions in `backend/pyproject.toml`; keep `backend/uv.lock` committed and use `uv sync --locked`.
- Supported Python range is `>=3.12,<3.14`.
- Use LiteLLM's async Python SDK directly for model calls, with a provider/model identifier in runtime configuration and provider credentials in environment variables. The CLI starts the event loop once; no separate proxy client lifecycle is required.
- Use `pydantic-settings` and `python-dotenv` for environment-backed settings; use PyYAML's safe loader before Pydantic validation.
- Keep orchestration explicit in Python, without the Agents SDK Runner. Define typed tools with the Agents SDK's `@function_tool`, dispatch only registered tools, and bound model/tool iterations. Validate each batch before dispatch and propagate tool failures from `run_agent`. The MVP caller uses `answer_question` so one English question yields one English result, including clarification, unsupported, and processing-failure outcomes.
- Runner-managed approvals, guardrails, dynamic enablement, timeouts, and deferred loading are not supported by the current tool adapter.
- Store secrets in environment variables (`.env` is gitignored); `.env.example` contains names and non-secret placeholders only.
