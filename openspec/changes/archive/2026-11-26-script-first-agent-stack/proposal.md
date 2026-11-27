# Proposal

## Why

The current MVP architecture and repository guidance no longer match the intended development sequence: first prove the agentic workflow from a Python script, then consider an API and client in a later phase. A forward-looking stack baseline is needed so implementation and documentation agree without retaining superseded framework or UI decisions.

## What Changes

- Replace the MVP's current application and orchestration direction with a script-first, asynchronous Python agentic core, coordinated through explicit Python control flow and the OpenAI SDK.
- Register typed functions with the OpenAI Agents SDK's `@function_tool` decorator while retaining the application's explicit orchestration loop.
- Use a separate LiteLLM Proxy as the model-provider gateway, exposing an OpenAI-compatible endpoint to the script.
- Declare application dependencies in `pyproject.toml`, lock them with `uv.lock`, and use uv to create and synchronize the project `.venv`.
- Use Pydantic for typed boundaries, PyYAML for declarative YAML files, and `python-dotenv` for local environment loading.
- Remove the CrewAI runtime dependency, its sample/demo code under `backend/src/`, and references to the greeting module from active project material; replace the old entry points with the script-first workflow.
- Remove obsolete framework, UI, and greeting-demo references from active architecture, MVP, setup, agent-guidance, environment, dependency, and runtime files. Keep archived OpenSpec change records unchanged.
- Align the OpenSpec context and applicable repository guidance with the new stack.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. This change resets the implementation stack and local test harness; it does not change the intended governed analytics behavior. The change metadata will set `skip_specs: true`.

## Impact

- Architecture and MVP planning documentation.
- `openspec/config.yaml`, repository agent guidance (including the stale greeting-module map), and Python/testing standards.
- Python dependency and environment configuration, including removal of the CrewAI dependency and replacement of the current requirements-file workflow.
- The OpenAI Agents SDK as a tool-definition and invocation dependency; its Runner does not own application orchestration.
- Existing backend entry points and demo-specific runtime files under `backend/src/`; the core workflow will be exercised from a Python script.
- Local model configuration for the LiteLLM Proxy and OpenAI-compatible client.

## Non-goals

- Implementing the analytics workflow or its tools.
- Adding a web API, user interface, or production hosting for the proxy.
- Choosing or implementing a future client.
- Rewriting archived OpenSpec records.
- Using an agent framework's Runner or delegating orchestration to a framework.
