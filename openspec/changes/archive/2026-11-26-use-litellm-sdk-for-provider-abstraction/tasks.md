# Tasks

## 1. Migrate dependencies and configuration

- [x] 1.1 Move LiteLLM into the backend runtime dependencies, remove the proxy-only dependency group, update `uv.lock`, and verify `uv sync --locked` succeeds.
- [x] 1.2 Replace proxy URL/key settings with provider/model configuration, update the root `.env.example`, and update configuration tests to verify required values and secret-safe errors.

## 2. Route model calls through the SDK

- [x] 2.1 Replace the `AsyncOpenAI` proxy client with an injectable async LiteLLM call boundary and verify unit tests route the configured provider/model without network access or a proxy.
- [x] 2.2 Update the agent loop, orchestration, and CLI to use the direct SDK response path; verify mocked tests cover text responses, tool-call continuations, malformed responses, and provider failures while preserving the bounded loop and safe failure outcome.

## 3. Remove proxy setup and align active guidance

- [x] 3.1 Remove proxy-only configuration and update `backend/README.md` and `docs/architecture-proposal.md` to document direct provider credentials and model selection; verify documented setup no longer starts or checks a proxy.
- [x] 3.2 Update `docs/mvp-sequence.md`, `ai-specs/standards/python.md`, `ai-specs/standards/testing.md`, and `openspec/config.yaml` to describe the in-process SDK architecture; verify active guidance no longer mandates the proxy and archived change records remain untouched.

## 4. Verify the completed change

- [x] 4.1 Run the full offline backend unit suite with `uv run --locked python -m pytest` from `backend/` and validate the change with `openspec validate use-litellm-sdk-for-provider-abstraction --type change`.
