# Design

## Context

See [proposal.md](./proposal.md) for the motivation and scope. The current backend is a small Python app with a demo entry point, while the repository already keeps its Python environment and source under `backend/`. The agentic workflow is not yet a product API or client.

## Goals / Non-Goals

**Goals:**

- Keep the agentic core importable and independently runnable from a Python script.
- Keep provider routing outside the core workflow, behind an OpenAI-compatible LiteLLM Proxy.
- Make config loading and model/tool boundaries typed and testable.
- Preserve a simple local development path with one locked Python environment.

**Non-Goals:**

- Add a web API, user interface, hosted proxy, or multi-user runtime.
- Add an agent orchestration framework or provider-specific logic to the workflow.
- Define the accounting tools, prompts, metrics, or catalog behavior in this stack change.

## Decisions

### Use an explicit Python orchestration loop

The application owns the sequence of model requests, tool-call dispatch, tool results, and final response using explicit Python control flow and the OpenAI SDK. Keep this core in an importable async module; a small script is only its current entry point. The OpenAI Agents SDK provides tool definitions and invocation, but its Runner does not own the workflow. This leaves a stable use-case boundary for a later API or client adapter.

An eventual framework can be evaluated only if concrete requirements such as durable state, branching workflows, human approval, or operational tracing justify its added abstraction.

### Put LiteLLM Proxy between the app and model providers

The app constructs an OpenAI SDK client pointed at the proxy's OpenAI-compatible endpoint. The app does not import LiteLLM or use a second model-client abstraction. Keep proxy configuration and provider credentials on the proxy side; the app reads its endpoint, proxy key, and selected model from environment-backed settings.

For local development, the proxy runs as a separate process. Keep its `litellm` package available through a dedicated optional dependency group in the backend project, so the app's runtime dependency set remains limited to the OpenAI SDK and the libraries it directly uses. This preserves a single lockfile without making the orchestration module depend on the proxy implementation.

### Use `pyproject.toml` and uv in `backend/`

Declare direct application dependencies and Python metadata in `backend/pyproject.toml`; commit `backend/uv.lock` for reproducible resolution. Keep the environment at `backend/.venv`, matching the existing source layout. `uv sync` is the canonical create-and-sync operation; it creates the environment when absent, so a separate `uv venv` step is optional rather than a second source of dependency state.

Keep test tools in a development dependency group. Remove the old runtime and development requirements-file workflow when the new project metadata is verified.

### Validate YAML at the application boundary

Load declarative YAML with PyYAML's safe loader, then validate the resulting data with Pydantic models before the orchestration code consumes it. Keep environment-specific values in environment variables; YAML files describe structured project configuration rather than secrets.

### Keep model calls and tests isolated

Use `AsyncOpenAI` for the script-first workflow. The CLI starts the event loop once, invokes the async core, and closes the client before the loop shuts down. Async allows non-blocking I/O and avoids a sync/async bridge for SDK tool invocation; it does not make an individual sequential model request faster. Unit tests exercise orchestration and tool dispatch with deterministic model responses or a mocked HTTP transport; ordinary tests do not require a live model or proxy. A separately invoked local smoke run may test the configured proxy and provider.

### Register tools with the Agents SDK

Declare tools as typed Python functions using `@function_tool` from the OpenAI Agents SDK. Use the resulting name, description, and generated argument schema when advertising tools through the OpenAI SDK client. Keep an explicit allowlist in the application-owned loop; validate the complete set of requested calls before dispatch, enforce the existing tool-call limit, and await each registered tool's SDK invocation with the required tool context and JSON arguments.

Adapt SDK tool output to the model's tool-result message format and configure failure handling so errors remain explicit rather than silently becoming success-shaped results. Do not assume Runner-specific features such as Runner-managed guardrails, approvals, or tracing apply to direct invocation; implement or explicitly exclude such behavior when it becomes a requirement. Keep provider routing in LiteLLM Proxy and do not use the Agents SDK Runner.

### Remove the legacy demo and module references

Remove the old CrewAI sample workflows from `backend/src/` rather than adapting them into the new core. Do not carry over the greeting sample, training/replay/test commands, or trigger-payload pathway from `backend/src/main.py` and `backend/src/app.py`. Remove greeting-module references from active project documentation and agent guidance, including the stale module-map entry and local-rules pointer. The new script entry point invokes only the importable workflow described above.

## Risks / Trade-offs

- **OpenAI-compatible APIs do not guarantee identical model features** -> Verify the selected proxy route supports the tool-call and structured-response features used by the workflow; fail explicitly when the response shape is unsupported.
- **Async lifecycle and SDK tool integration add complexity** -> Close the async client explicitly, keep the event-loop boundary in the CLI, and test adapter behavior and failures offline against the locked SDK version.
- **A separate proxy adds local startup and configuration** -> Keep the app endpoint configurable and document one reproducible local proxy setup in the implementation change.
- **YAML configuration can be malformed or incomplete** -> Parse safely and validate immediately with Pydantic, returning actionable configuration errors before making a model request.
- **The old demo and the new script have different entry points** -> Remove the legacy sample pathways and make the script call the same importable core used by future adapters; do not retain a parallel legacy runtime path.
- **The existing repository guidance still describes the former stack** -> Update active guidance and OpenSpec context as part of implementation; leave archived change records unchanged.

## Migration Plan

1. Establish the uv-managed backend project and create/synchronize `backend/.venv`.
2. Add the importable workflow boundary, validated configuration, and script entry point.
3. Configure the local LiteLLM Proxy and point the OpenAI SDK client at it.
4. Replace the old demo-specific runtime/dependency setup and align active documentation and agent guidance.
5. Verify offline unit tests, dependency lock/environment reproducibility, and a separately run proxy smoke test.

Rollback consists of reverting only the implementation change's active files and restoring the previous dependency metadata if needed. Archived OpenSpec records remain unchanged in either direction.

## Open Questions

- Which initial provider and model should the local proxy route to? This can be selected in configuration without changing the architecture.
