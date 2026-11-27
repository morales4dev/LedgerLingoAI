# Testing

## Layer 1

- TDD: failing test before production code when the work is testable.
- Tests use AAA (Arrange, Act, Assert). Keep unit, integration, and e2e categories separate.
- Mock I/O (network, filesystem, clocks) in units. Do not hit live services in unit tests.

## Layer 2 — LedgerLingoAI

- Pytest units live under `backend/tests/unit/`; run from `backend/` with `uv run --locked python -m pytest`.
- Keep unit tests offline. Mock model responses and external I/O; do not require a LiteLLM Proxy process or provider credentials.
- Test async client cleanup and `@function_tool` dispatch, argument validation, failures, and the bounded loop with mocked model calls.
- Keep tests and development dependencies in the `dev` group in `backend/pyproject.toml`; `backend/uv.lock` is the authoritative resolution.
- Test the one-shot caller contract: one question per invocation, internal tool iterations, one final response, and no request-history reuse.
- Use a local proxy health check for proxy configuration; live provider/model calls are optional smoke tests only when credentials and a route are configured.
