# Design

## Context

See [proposal.md](./proposal.md) and [specs/one-shot-analytics-request/spec.md](./specs/one-shot-analytics-request/spec.md) for the motivation and observable contract. The related `script-first-agent-stack` change establishes the Python caller and model stack; this change defines the MVP request boundary and its acceptance behavior.

## Goals / Non-Goals

**Goals:**

- Treat each invocation as an independent request with one English text input and one English text output.
- Keep all model reasoning and tool execution inside that invocation.
- Let the MVP test script act as caller and display or log only the final result.
- Preserve safe clarification, unsupported-request, and failure outcomes as single returned results.

**Non-Goals:**

- Define an external API or user-facing application.
- Retain question-specific state between invocations.
- Expose intermediate model or tool messages as separate user responses.
- Change the governed analytics workflow or its underlying model/tool choices.

## Decisions

### Separate the caller boundary from internal iteration

The script calls the agent with one question and receives one final text result. The orchestration may perform multiple model iterations and tool calls internally, but those iterations do not create additional caller inputs or outputs.

```text
Python test script
    | one English question
    v
one invocation
    | agent iterations
    |   tool calls/results as needed
    v
one English text result
    | print or log
    v
caller
```

The script is a test caller, not a product interface. Keep the invocation contract independent of any later caller or presentation layer.

### Scope all question-specific context to one invocation

Construct request context from the current question and approved system configuration. Do not retain or pass a prior question or response as implicit context. A subsequent question is a new invocation, even when submitted by the same caller.

### Return a result instead of waiting for another input

When the question is ambiguous, unsupported, or cannot be safely processed, return one English text result describing that outcome. Do not pause the invocation waiting for a follow-up question; a caller that wants to retry submits a separate request.

### Use English for the MVP text contract

The MVP test inputs are English text questions and the returned text is English. Prompting and test fixtures should reflect that contract. Language detection or support for other languages is not part of this change.

### Keep traces invocation-scoped

If a technical trace is recorded, associate it with the individual request/run and its internal model/tool activity. Do not model a longer interaction identifier or combine multiple user questions into one trace.

## Risks / Trade-offs

- **Internal iterations may accidentally leak as multiple outputs** -> Keep script output at the invocation boundary and test that tool activity produces only one final result.
- **State may leak through reused process objects or message buffers** -> Construct or clear request-specific state per invocation and test consecutive requests with distinct inputs.
- **A clarification result may be mistaken for an invitation to continue in the same run** -> Return it as a completed result; require a fresh invocation for any retry.
- **A model may return non-English text despite the MVP prompt** -> Add English response assertions to deterministic tests and evaluate live-provider behavior separately when configured.

## Migration Plan

1. Apply the script-first stack change to establish the Python caller and importable agent boundary.
2. Add invocation-scoped input, context, internal loops, and one final text result.
3. Add deterministic tests for success, clarification, unsupported/failure outcomes, and state isolation across calls.
4. Align active architecture and MVP documentation with the spec; keep later caller and presentation choices undecided.
5. Verify the offline test suite and a separately configured model smoke test.

No persistent data migration is required. Rollback reverts the behavior and documentation changes while leaving the script-first stack change intact.
