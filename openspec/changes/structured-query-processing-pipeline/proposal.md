# Proposal

## Why

The backend currently returns model-composed text directly and does not yet register analytics tools. A typed, explicit processing pipeline will separate query interpretation from deterministic validation, calculation, and reporting while preserving the one-question/one-response contract.

## What Changes

- Introduce a Pydantic `StructuredQuery` and a typed query-interpretation outcome that represents either a structured query or a clarification; keep both internal from the caller-facing response.
- Add an application orchestrator between the CLI and query interpretation. It owns the processing sequence, returns a clarification directly when needed, and otherwise returns the final response string.
- Add a typed validation result and deterministic validator called by the orchestrator. The initial validator is a stub that returns `VALID`.
- Add a deterministic calculator accepting `StructuredQuery` and returning a typed financial response. Its initial implementation returns a fixed amount of 68.
- Add a result reporter that converts the calculator response into the caller-facing English string.
- Preserve the one-shot clarification behavior by short-circuiting before validation and calculation when interpretation requests clarification.
- Keep the agent's use of the validator as a self-correction tool, real validation rules, ledger access, and real financial calculations out of this change.

## Capabilities

### New Capabilities

- `financial-query-processing`: Process one natural-language financial question through a structured query, validation, deterministic calculation, and response reporting pipeline.

### Modified Capabilities

None. The existing one-shot request and response contract remains unchanged.

## Impact

- `backend/src/ledgerlingo/`: add the structured query and result types, validator, calculator, reporter, and application orchestration boundary; adapt query interpretation to produce the structured type.
- `backend/src/ledgerlingo/cli.py`: route requests through the orchestrator while continuing to return/print one English string.
- `backend/tests/unit/`: add offline tests for pipeline ordering, typed boundaries, and the initial fixed validator/calculator/reporter behavior.
- No new dependencies or journal-data access are required.

## Non-goals

- Giving the query agent access to journal data or calculation results.
- Integrating the validator as an agent tool for self-correction; that belongs in a later change.
- Implementing production validation rules, ledger access, or real financial calculations.
- Changing the public one-question/one-English-response contract.
