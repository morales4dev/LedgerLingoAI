# Proposal

## Why

The current implementation treats LiteLLM as a separately run proxy, but the intended architecture is to use LiteLLM's Python library in the application as the abstraction over model providers. Correcting this now avoids building local setup, configuration, and application boundaries around an unnecessary service.

## What Changes

- Replace the OpenAI SDK client pointed at a LiteLLM Proxy with direct asynchronous calls through the LiteLLM Python SDK, preserving the existing one-shot workflow and tool behavior.
- Remove the separate proxy process, proxy-only configuration and dependency group, and proxy-specific environment variables; configure the selected provider, model, and credentials for use by the application.
- Update active operator and architecture documentation, tests, and agent/OpenSpec guidance to describe the in-process SDK integration. Keep archived change records as historical documentation.
- **BREAKING**: Replace `LITELLM_PROXY_URL` and `LITELLM_PROXY_API_KEY` configuration with direct provider/model configuration.

## Non-goals

- Changing the caller-facing one-question/one-response contract or financial query, validation, calculation, and reporting behavior.
- Adding a hosted service, web API, or another model gateway.
- Changing the orchestration loop or moving it to the Agents SDK Runner.

## Capabilities

### New Capabilities

- `llm-provider-integration`: Invoke configured LLM providers through LiteLLM's in-process Python SDK, without requiring a separate LiteLLM Proxy.

### Modified Capabilities

- None. Existing caller-facing and financial-processing requirements remain unchanged.

## Impact

- Application client and settings in `backend/src/ledgerlingo/`.
- Backend dependencies and lockfile in `backend/pyproject.toml` and `backend/uv.lock`.
- Proxy configuration, root `.env.example`, operator runbook, and client/configuration unit tests.
- Active architecture docs (`docs/architecture-proposal.md`, `docs/mvp-sequence.md`), guidance (`ai-specs/standards/`, `openspec/config.yaml`), and the backend operator runbook; archived change artifacts remain historical.
