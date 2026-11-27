# Tasks

## 1. Establish the uv-managed backend project

- [x] 1.1 Add `backend/pyproject.toml` with the supported Python version, direct app dependencies, test tools, and a separate local-proxy dependency group; remove CrewAI from the runtime dependencies, generate `backend/uv.lock`, and verify `uv sync --locked` succeeds with no CrewAI package in the resolved project environment.
- [x] 1.2 Make `backend/.venv` the documented environment and update setup instructions to create/sync it through uv; verify the documented commands work from a clean backend environment.

## 2. Add validated configuration and local model gateway

- [x] 2.1 Add Pydantic settings for the proxy endpoint, proxy credential, and selected model, loaded from environment variables with `python-dotenv`; unit-test valid settings, missing required values, and safe error messages.
- [x] 2.2 Add a safe YAML loader and Pydantic validation for declarative configuration; unit-test valid input, malformed YAML, and schema-invalid data.
- [x] 2.3 Add local LiteLLM Proxy configuration and startup guidance without committing provider secrets; verify the configured proxy starts and exposes the endpoint expected by the app.

## 3. Implement the script-callable agentic core

- [x] 3.1 Add an OpenAI SDK client factory configured for the LiteLLM Proxy and selected model; unit-test that endpoint and credentials are passed to the client without importing the proxy package in app code.
- [x] 3.2 Implement explicit Python orchestration for model requests, tool dispatch, tool results, and final output, with a bounded call loop and explicit errors; test successful calls, tool results, invalid responses, and the loop limit using a mocked model transport.

## 4. Make the Python script the current entry point

- [x] 4.1 Add a runnable script that accepts a question and invokes the importable core; test its argument handling and output with a mocked model client, without requiring network access.
- [x] 4.2 Remove the CrewAI sample code from `backend/src/main.py` and `backend/src/app.py`, including greeting-module imports/calls, training/replay/test commands, and trigger-payload handling; keep the new script as the only current app entry point and verify imports plus the focused backend test suite pass.

## 5. Align active project guidance

- [x] 5.1 Rewrite the active architecture proposal and MVP sequence around the script-first workflow, proxy boundary, and deferred client/API phase; remove greeting-demo phases, examples, and acceptance text, then verify the docs describe one consistent current stack without a regret narrative.
- [x] 5.2 Update the README, `.env.example`, agent constitution, Python/testing standards, and OpenSpec context/rules to match the new environment, dependencies, and script workflow; remove the stale greeting-module map and local-rules pointer, then verify setup instructions and examples match the lockfile.
- [x] 5.3 Search active source (including `backend/src/`), runtime dependencies, configuration, and current project documentation for references to the retired framework, UI, or greeting sample/module; verify none remain outside archived OpenSpec records and this change's cleanup plan, which remain unchanged.

## 6. Verify the integrated change

- [x] 6.1 Run the complete offline backend test suite, verify `uv sync --locked` succeeds, and validate this OpenSpec change; run a real proxy/model smoke test only when local credentials and a provider route are configured.

## 7. Adopt async and SDK tool definitions

- [x] 7.1 Add the OpenAI Agents SDK as a direct application dependency, regenerate the uv lockfile, and verify `uv sync --locked` succeeds without introducing framework-managed orchestration.
- [x] 7.2 Replace the synchronous OpenAI client and orchestration core with `AsyncOpenAI` and async functions; keep a synchronous CLI that starts the event loop once, closes the client, and produces the existing output. Test client configuration, cleanup, CLI behavior, and mocked model calls offline.
- [x] 7.3 Register tools with `@function_tool` and adapt the explicit bounded loop to advertise generated schemas and await SDK tool invocation with the required context. Test valid calls and outputs, invalid arguments, unknown tools, error handling, multiple-call validation before dispatch, and the loop limit offline; do not use the SDK Runner.
- [x] 7.4 Update the README, architecture and MVP guidance, Python/testing standards, and OpenSpec context/rules to describe the async client and SDK tool-definition boundary; verify they agree with the implemented workflow and dependency lock.
- [x] 7.5 Run the complete offline backend test suite, verify `uv sync --locked`, and validate this OpenSpec change.
