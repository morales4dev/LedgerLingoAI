# Tasks

## 1. Implement the one-shot response contract

- [x] 1.1 Make the agent invocation accept one English text question and return one English text response; verify with a deterministic mocked-model test that the request instruction and returned fixture are English.
- [x] 1.2 Keep agent iterations and any nested tool calls internal to one invocation; verify multiple internal tool steps still produce exactly one result for the caller.

## 2. Isolate requests and return terminal outcomes

- [x] 2.1 Return one final English response when a question needs clarification, is unsupported, or cannot be safely processed; test each outcome without waiting for another input.
- [x] 2.2 Scope question-specific context to each invocation; verify consecutive requests do not receive or reuse the preceding request's question or response.

## 3. Align the MVP caller and active guidance

- [x] 3.1 Integrate the contract with the Python test script from `script-first-agent-stack`; verify one script invocation submits one question, invokes the core once, and prints or logs one final response.
- [x] 3.2 Rewrite the architecture proposal and MVP sequence to describe English text input, one invocation, internal agent/tool iterations, and one English result; remove stateful interaction flows and request-history identifiers, then verify both documents agree with the spec.
- [x] 3.3 Update the README and relevant agent/testing guidance to describe the script caller and one-shot English text contract; verify no product-facing stateful interaction assumptions remain while preserving coding-assistant instructions.

## 4. Verify the MVP contract

- [x] 4.1 Run the offline backend tests and validate this OpenSpec change; verify the tests cover successful response, clarification, unsupported/failure outcomes, internal tool iteration, and isolation across consecutive invocations.
