# Design

## Context

See `proposal.md` for motivation and `specs/financial-query-processing/spec.md` for the behavior contract. The CLI currently calls `answer_question`, which delegates to a bounded model/tool loop and returns text. The backend has no registered analytics tools or ledger integration. The MVP accepts that the natural-language question is sent to the configured model, but journal data and calculation results must remain outside query interpretation.

## Goals / Non-Goals

**Goals:**

- Establish typed boundaries between interpretation, validation, calculation, and reporting.
- Keep orchestration explicit in application code and preserve the CLI's one-English-string contract.
- Make the initial validator, calculator, and reporter replaceable without changing the orchestration boundary.

**Non-Goals:**

- Integrating the validator as an agent tool in this change.
- Defining production accounting semantics, accessing a ledger, or calculating real financial values.
- Changing model hosting or the accepted MVP exposure of the natural-language question.

## Decisions

### Use typed domain contracts

Define `StructuredQuery`, `QueryValidation`, and `FinancialResult` as Pydantic models in a focused domain module. The initial query shape contains a metric, an optional period, and filters; it is a minimal contract for the scaffold, not a complete accounting query language. `QueryValidation` carries a validity outcome and validation feedback so the same validator can later be wrapped as an agent tool. `FinancialResult` carries an exact decimal amount; the stub returns `Decimal("68")`.

**Alternative considered:** pass unvalidated dictionaries between stages. Rejected because it weakens the boundaries this change is intended to establish.

### Separate query interpretation from the generic agent loop

Keep the bounded model/tool loop as lower-level agent machinery and add a domain operation such as `interpret_query(question) -> QueryInterpretation`. `QueryInterpretation` is a typed outcome discriminating between a `StructuredQuery` and a clarification request. Validate the model's structured output at this boundary. The query agent receives the question and its instructions only; the journal and calculator are not available to it. Do not add a validator tool to the agent in this change.

**Alternative considered:** change the generic loop's return type to `StructuredQuery`. Rejected because the loop itself should not own a financial-domain type.

### Put sequencing and the mandatory validation gate in the orchestrator

Add an application-level `process_question(...) -> str` operation. The CLI calls it; it invokes query interpretation and returns a clarification request directly as an English response, without invoking validation or calculation. For a structured query, it calls the validator and invokes calculation only for a valid result. It then delegates successful calculation results to the reporter. If interpretation or validation fails, it must not invoke the calculator and must return the existing safe processing-failure response.

**Alternative considered:** let the CLI sequence the components. Rejected because that would make the entry-point adapter responsible for application policy and complicate other callers.

### Make validation a reusable local service

Implement a deterministic `validate_query(StructuredQuery) -> QueryValidation` callable. The orchestrator calls it directly and always performs the final check. In a later change, an agent tool can wrap this same function to provide bounded self-correction feedback; that tool call will not replace the orchestrator's final validation.

The initial implementation always reports valid. This is a wiring stub, not a claim that arbitrary financial queries have passed meaningful business validation.

### Keep calculation and reporting local and simple

Implement the calculator as a deterministic operation accepting a validated `StructuredQuery` and returning `FinancialResult(amount=Decimal("68"))`. Implement reporting as a simple local English template that interpolates the amount. Neither operation calls the model or accesses journal data in this scaffold.

**Alternative considered:** use an LLM to write the final response. Rejected for this change because it adds no needed capability and would expose calculation results to the model.

### Preserve the existing invocation boundary

Keep the CLI's one-question/one-English-response interface and its client lifecycle. The new internal models and component results remain scoped to one invocation. No new dependency is required; unit tests remain offline and mock model responses.

## Risks / Trade-offs

- [The model may return malformed or semantically mistaken query data] -> Validate the output as `StructuredQuery`, fail safely on parse errors, and keep the mandatory deterministic validator before calculation. The initial validator stub does not detect semantic errors.
- [The fixed amount could be mistaken for a real financial result] -> Keep the calculator visibly documented and tested as a placeholder with no ledger access; replace it before presenting the scaffold as a real financial calculator.
- [The natural-language question may contain sensitive context] -> This exposure is accepted for the MVP. Do not include journal data or calculation results in model input.
- [A future agent tool could be mistaken for the final safety gate] -> Reuse the validator implementation, but retain orchestrator-side validation of the exact final query.

## Migration Plan

Route the CLI through the orchestrator while preserving its existing text output boundary and client lifecycle. Keep the existing safe processing-failure outcome for failures before reporting. No persisted data or external infrastructure changes are involved; rollback consists of restoring the CLI's previous call to `answer_question`.
