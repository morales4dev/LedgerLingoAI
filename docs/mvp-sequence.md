# LedgerLingoAI MVP Sequence

This sequence keeps the first MVP caller small and testable: one Python script submits one independent text question and prints one text response. The architecture boundary is described in [architecture-proposal.md](./architecture-proposal.md).

## 1. Establish the script-first runtime

Create the uv-managed backend environment, validated settings and YAML boundaries, local LiteLLM Proxy configuration, async OpenAI SDK client, and importable async Python orchestrator. Define registered tools with the Agents SDK's `@function_tool` but keep orchestration in the application's bounded loop. Test it with mocked model responses. The CLI remains the only current caller.

Tracked by `script-first-agent-stack`.

## 2. Define the one-shot request contract

Treat each CLI invocation as an independent request with one question and one final response. Internal model and tool iterations stay within the invocation. Do not retain earlier questions, responses, or conversation history.

Tracked by `mvp-one-shot-analytics-contract`.

## 3. Add governed analytics capabilities

Introduce analytics behavior through separate product changes. Keep business definitions and approved physical assets declarative, expose only approved tools to the orchestrator, and enforce query safety outside the model. The script remains the caller while the analytics path is established.

## 4. Verify the MVP workflow

Use offline tests for configuration, orchestration, tool dispatch, failure outcomes, and request isolation. Add deterministic analytics fixtures when the relevant product contracts and tools are implemented. A provider smoke test is optional and requires local credentials and a configured route.

## 5. Consider a future caller

After the script workflow and governed analytics behavior are validated, decide whether another caller is needed. An API, UI, and client adapter are deferred; this sequence does not choose their design or commit to a delivery date.

## MVP Boundary

- One text question and one text response per invocation.
- No request-history state or multi-question interaction.
- No web UI, API, hosted runtime, or user-level access control.
- No framework-managed orchestration or direct provider-specific logic in the orchestrator.
- No analytics behavior outside separately approved product contracts.
