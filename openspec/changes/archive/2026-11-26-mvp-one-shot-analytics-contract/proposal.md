# Proposal

## Why

The MVP needs a precise boundary between one user question and one system response, independent of how internal model and tool calls are orchestrated. Existing planning material describes a stateful interaction surface, which conflicts with the agreed script-first MVP.

## What Changes

- Define the MVP request contract as one English text question producing one English text response per invocation.
- Require each invocation to be independent, with no user-question history or interaction state carried between calls.
- Allow the agent and its tools to iterate internally while returning only one final response to the caller.
- Use the Python test script as the MVP caller; it supplies a question and prints or logs the returned response.
- Update active architecture, MVP, setup, and agent guidance to describe this one-shot contract; leave later caller and presentation choices undecided.

## Capabilities

### New Capabilities

- `one-shot-analytics-request`: Processes one independent English text question and returns one English text response for the MVP.

### Modified Capabilities

None.

## Impact

- New product behavior spec for one-shot analytics requests.
- The script-callable agent boundary and its invocation-scoped state.
- Acceptance tests for language, single-result behavior, and isolation between invocations.
- Active architecture/MVP documentation and agent guidance.

## Non-goals

- Adding an API or a user-facing application.
- Prescribing how a caller collects or presents text.
- Carrying state between invocations or supporting a multi-question interaction.
- Changing the analytics domain, metrics, catalog, or query-governance rules.
- Changing the selected Python/model stack, which is covered by `script-first-agent-stack`.
