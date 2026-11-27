# Design

## Context

See [proposal.md](./proposal.md) for the motivation and scope. The current model-call boundary constructs an `AsyncOpenAI` client for a proxy URL; the bounded agent loop sends OpenAI-format messages and tool schemas through that client. The app already has a model setting and an OpenAI provider key for the proxy route.

LiteLLM's Python SDK provides an asynchronous completion interface and a common chat-completion/tool-call format. The existing orchestration loop and Agents SDK tool definitions remain the owner of tool execution.

## Goals / Non-Goals

**Goals:**

- Make provider/model selection a runtime configuration concern while keeping the orchestration loop provider-neutral.
- Keep model calls asynchronous and preserve existing tool dispatch, response validation, and safe failure behavior.
- Keep unit tests offline by injecting or mocking the model-call boundary.

**Non-Goals:**

- Add provider-specific branching, fallback routing, or new retry policy to the application.
- Change tool ownership, tool authorization, or the Agents SDK Runner boundary.

## Decisions

### Call providers through LiteLLM's async SDK

Use LiteLLM's asynchronous completion interface as the model-call path, rather than constructing an OpenAI SDK client pointed at an OpenAI-compatible proxy. Keep a small injectable call boundary so tests can substitute deterministic responses without initializing a provider client or making network requests.

The existing OpenAI-format messages, tool schemas, and bounded Python loop remain in place. The response boundary must continue to expose choices, assistant content, and tool calls in the shape the loop validates. Keep the OpenAI SDK dependency while application code still imports its message parameter types; LiteLLM replaces the network-client role, not necessarily those type definitions.

**Alternative considered:** Continue using `AsyncOpenAI` with provider-specific base URLs. This would preserve the current transport abstraction but would make provider routing an application-managed endpoint concern rather than using the requested LiteLLM library abstraction.

### Put provider and model selection in runtime configuration

Use `MODEL_NAME` for LiteLLM's provider/model identifier (for example, `openai/gpt-4o-mini`). Let LiteLLM resolve provider credentials from the provider's standard environment variable, beginning with `OPENAI_API_KEY` for the current route. Do not retain proxy URL, proxy key, proxy config, or proxy startup as application requirements.

**Alternative considered:** Keep one generic proxy-style URL and key. That would preserve a gateway contract and require an intermediary service, which is outside the intended architecture.

### Preserve explicit failure and tool behavior

Keep the current allowlisted, bounded tool loop and validate the model response before dispatching tools. Convert LiteLLM call failures at the model-call boundary into the existing explicit agent failure path; do not log provider secrets or return a success-shaped response when a call or response fails. Test both a normal completion and a tool-call continuation against mocked LiteLLM responses.

**Alternative considered:** Delegate tool handling to LiteLLM or the Agents SDK Runner. This would change orchestration ownership and is not required for provider abstraction.

### Remove proxy lifecycle and refresh active guidance

Make LiteLLM a direct runtime dependency instead of an optional proxy dependency group. Remove the app's `AsyncOpenAI` proxy-client lifecycle and proxy-only startup/configuration files. Update the runbook, `.env.example`, architecture proposal, MVP sequence, tests, `openspec/config.yaml`, and the active Python and testing standards to describe direct SDK calls and application-side provider credentials. Leave archived change records unchanged.

**Alternative considered:** Retain proxy files as an optional development path. That would leave two supported architectures and keep the original misunderstanding operationally active.

## Risks / Trade-offs

- **Provider tool-call support and response details vary** -> Keep the current OpenAI route as the initial baseline, test the normalized response shape offline, and report unsupported or malformed responses through the existing explicit failure path.
- **Provider credentials move into the application process** -> Read secrets only from environment variables, keep `.env` gitignored, and never include credential values in logs or user-facing errors.
- **LiteLLM adds a runtime dependency and transitive packages** -> Pin through the existing uv lockfile and verify synchronization and the offline test suite.
- **Removing the proxy changes local setup and configuration** -> Update the runbook and sample environment together with the client/settings migration; keep rollback limited to restoring the previous proxy configuration and dependency group if needed.

## Migration Plan

1. Replace proxy-specific settings and the OpenAI proxy client with the LiteLLM async call boundary and provider/model configuration.
2. Move LiteLLM into the runtime dependency set; remove proxy configuration and proxy startup guidance; update the lockfile and sample environment.
3. Update offline tests for configured provider routing, completion parsing, tool-call continuation, failures, and async execution without a proxy.
4. Update active operator and agent guidance, then run the backend unit suite and OpenSpec validation.

Rollback restores the proxy settings, client, optional dependency group, and active setup guidance together. Archived OpenSpec records remain historical.
