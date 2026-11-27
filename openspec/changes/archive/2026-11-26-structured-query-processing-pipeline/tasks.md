# Tasks

## 1. Structured Query and Interpretation

- [x] 1.1 Add Pydantic domain contracts for `StructuredQuery`, `QueryValidation`, and `FinancialResult`; verify required fields, defaults, and exact decimal amounts with focused unit tests.
- [x] 1.2 Add tests for structured-query, clarification, and malformed model output, then expose query interpretation as a typed `QueryInterpretation` outcome; verify with agent unit tests using mocked model responses.

## 2. Deterministic Components

- [x] 2.1 Implement the deterministic validator returning a typed valid result; verify its contract with focused unit tests.
- [x] 2.2 Implement the calculator stub returning `FinancialResult` with amount 68 and no journal access; verify the fixed result and query input with unit tests.
- [x] 2.3 Implement the local English result reporter; verify that it formats the financial result amount as expected with unit tests.

## 3. Orchestration and CLI Integration

- [x] 3.1 Implement the application orchestrator to return clarification outcomes directly and otherwise validate, calculate only on valid results, and report; verify stage ordering, clarification short-circuit, invalid-query gating, and failure handling with mocked component tests.
- [x] 3.2 Route the CLI through the orchestrator and update the backend runbook to describe the new flow; verify the CLI still prints one English response and its offline unit tests pass.

## 4. Integration Verification

- [x] 4.1 Run the complete offline backend unit suite and validate this OpenSpec change; verify both commands pass.
