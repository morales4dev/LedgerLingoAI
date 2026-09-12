# LedgerLingoAI MVP Sequence

This document records the proposed implementation sequence for the MVP described in `docs/architecture-proposal.md`. It is a backlog and refinement reference, not an implementation plan for v1 or v2.

The MVP proves a governed conversational analytics workflow over the approved `core` schema of a fixed PostgreSQL database.

## MVP Change Sequence

### 1. `formalize-core-analytics-model`

#### User outcome

The project has an explicit, reviewable description of the physical data model that the MVP analytics workflow is allowed to use.

#### In scope

- Document the approved `core` tables, columns, data types, relationships, join keys, aliases, and time fields.
- Define the database and schema identifiers used by the analytical catalog.
- Identify approved tables and views, including their user-facing descriptions.
- Identify time dimensions and period semantics needed by the supported questions.
- Mark the `core` assets as the MVP analytical source of truth.
- Explicitly exclude `raw`, `stg`, and `audit` from agent access and analytical query generation.

#### Non-goals

- Do not expose ingestion, staging, reject, or audit tables to the agent.
- Do not add OpenMetadata or runtime metadata introspection.
- Do not expand the physical model beyond the existing sandbox PostgreSQL data.
- Do not define business metrics; those belong to the semantic-layer change.

#### Dependencies

None. The existing PostgreSQL sandbox and its schema scripts provide the initial physical context.

#### Acceptance scenarios

- Given the MVP catalog, when an approved asset is requested, then its schema, table, columns, types, description, and relationships are available to the planner.
- Given a catalog lookup for an ingestion or validation asset, when the asset belongs to `raw`, `stg`, or `audit`, then it is unavailable as an analytical source.
- Given a relationship used by a supported query, when the planner resolves the relationship, then the join keys and cardinality assumptions are explicit.

#### Verification strategy

- Validate the catalog against the existing `core` schema definitions.
- Test that every approved asset exists and every excluded schema is rejected.
- Review the initial catalog against the fixed MVP question suite before dependent changes begin.

### 2. `define-mvp-accounting-semantics`

#### User outcome

The MVP has explicit, versioned definitions for the accounting concepts that the agent may use when interpreting supported questions.

#### In scope

- Define initial metrics such as revenue, cost, and gross margin.
- Define metric formulas, aggregation behavior, and applicable source fields.
- Define fiscal year, fiscal period, posting date, and period-filter behavior.
- Define currency assumptions and any conversion limitations.
- Define supported dimensions and their meanings, including how a country filter is resolved.
- Define the relationship between business concepts and approved `core` assets.
- Define the initial fixed question suite used to prove the semantics.

#### Non-goals

- Do not hide business definitions in prompts or agent instructions.
- Do not define unrestricted natural-language text-to-SQL behavior.
- Do not add v1 or v2 metrics, catalog capabilities, or cross-database semantics.
- Do not assume that a dimension exists merely because a similarly named physical column exists.

#### Dependencies

Depends on `formalize-core-analytics-model` for the approved physical assets and relationships.

#### Acceptance scenarios

- Given a supported metric name, when the semantic layer resolves it, then the formula, aggregation, and source fields are explicit.
- Given a supported fiscal-period question, when the period is resolved, then the applicable fiscal fields and filter rules are explicit.
- Given a country filter, when it is resolved, then the semantic definition identifies the precise business meaning and `core` field used.
- Given an unsupported or ambiguous metric or dimension, when it is requested, then the system can identify that clarification or rejection is required.

#### Verification strategy

- Unit-test metric and period definitions against expected logical plans.
- Review every semantic definition against the physical catalog.
- Use representative questions, including ambiguous-dimension cases, as semantic regression fixtures.

### 3. `add-governed-core-query-service`

#### User outcome

The system can execute validated analytical queries against PostgreSQL while enforcing the MVP governance boundary outside the language model.

#### In scope

- Define a logical query-plan and query-execution contract.
- Generate PostgreSQL queries from approved logical plans.
- Execute queries only against approved `core` assets.
- Reject references to `raw`, `stg`, and `audit` schemas.
- Enforce read-only SQL behavior.
- Reject mutation and schema-changing operations such as `INSERT`, `UPDATE`, `DELETE`, `CREATE`, and `ALTER`.
- Enforce required filters, row limits, and query timeouts where defined by policy.
- Return structured execution results and execution errors to the orchestration layer.

#### Non-goals

- Do not allow unrestricted SQL supplied by the language model.
- Do not support databases other than PostgreSQL.
- Do not add user-level access control.
- Do not expose raw records, staging records, or audit records as analytical results.

#### Dependencies

Depends on `formalize-core-analytics-model` and `define-mvp-accounting-semantics`.

#### Acceptance scenarios

- Given a valid logical plan using approved `core` assets, when it is executed, then PostgreSQL returns a structured result.
- Given SQL that references `raw`, `stg`, or `audit`, when it is validated, then execution is rejected.
- Given SQL containing a mutation or schema-changing operation, when it is validated, then execution is rejected.
- Given a plan missing a required filter or exceeding the configured row or timeout policy, when it is validated, then execution is rejected or constrained according to the policy.
- Given a database error or timeout, when execution fails, then the caller receives a structured failure without exposing secrets.

#### Verification strategy

- Unit-test SQL validation with allowed and forbidden statements.
- Test approved and excluded schema references.
- Run integration tests against the sandbox PostgreSQL database.
- Verify row-limit and timeout behavior with deterministic fixtures.

### 4. `add-accounting-question-orchestration`

#### User outcome

An accounting professional can ask a supported question in natural language and receive an answer produced from a governed query rather than from unsupported model-only reasoning.

#### In scope

- Use CrewAI as the MVP orchestration framework.
- Convert natural-language questions into structured intent containing metrics, dimensions, filters, and time periods.
- Resolve semantic definitions from the declarative semantic layer.
- Resolve physical assets and relationships from the `core` catalog.
- Build a logical query plan.
- Call the governed query service.
- Produce a user-facing answer from the validated result.
- Request clarification or report unsupported questions when the intent cannot be resolved safely.

#### Non-goals

- Do not let the agent define business truth independently of the semantic layer.
- Do not let the agent bypass query validation or execute arbitrary SQL.
- Do not support open-ended database discovery or unrestricted text-to-SQL.
- Do not introduce LangGraph or change the selected agent framework during the MVP.

#### Dependencies

Depends on `formalize-core-analytics-model`, `define-mvp-accounting-semantics`, and `add-governed-core-query-service`.

#### Acceptance scenarios

- Given a supported question such as gross margin for a defined country and fiscal period, when it is submitted, then the system resolves the intent, selects approved definitions and assets, executes a validated query, and returns an answer.
- Given an ambiguous question, when the missing meaning affects correctness, then the system asks for clarification rather than guessing.
- Given an unsupported question, when no approved semantic or physical path exists, then the system reports that it is unsupported without querying unapproved data.
- Given a query-validation failure, when orchestration receives the failure, then no unvalidated result is presented as an answer.

#### Verification strategy

- Test intent resolution and logical-plan construction with fixed question fixtures.
- Test clarification and unsupported-question paths.
- Test end-to-end orchestration with a deterministic query service or sandbox database.
- Assert that every successful answer originated from a validated query result.

### 5. `add-mvp-answer-tracing`

#### User outcome

Each question-and-answer cycle leaves a detailed technical trace that supports evaluation, debugging, and auditability without exposing secrets or unnecessary sensitive data.

#### In scope

- Record request and conversation identifiers when available.
- Record the original question, parsed intent, selected semantic definitions, filters, and time period.
- Record source schemas, tables, columns, relationships, and the logical query plan.
- Record generated SQL, validation rules, validation status, execution status, timing, and errors.
- Record the result summary used to produce the answer and the final answer.
- Write one trace per question-and-answer cycle in an evaluation-friendly format and location.

#### Non-goals

- Do not record secrets, credentials, or unnecessary sensitive raw data.
- Do not make traces a substitute for the semantic catalog or query governance.
- Do not build a v1 observability platform.

#### Dependencies

Depends on `add-accounting-question-orchestration` and the governed query service.

#### Acceptance scenarios

- Given a successful question-and-answer cycle, when processing completes, then a trace contains the required request, semantic, planning, validation, execution, result, and answer information.
- Given a validation or execution failure, when processing ends, then the trace records the failure and relevant timing without recording secrets.
- Given a trace, when an evaluator inspects it, then the selected assets can be compared with the approved `core` catalog.

#### Verification strategy

- Validate trace structure with schema or contract tests.
- Test successful, clarification, validation-failure, and execution-failure traces.
- Scan generated traces for credentials and prohibited raw or sensitive payloads.

### 6. `replace-greeting-chat-with-analytics-chat`

#### User outcome

The existing Gradio greeting demo is replaced by the MVP analytics chat experience, so users interact with the governed accounting workflow through the application entry point.

#### In scope

- Replace the greeting-specific chat callback and presentation with the analytics workflow.
- Keep Gradio as the MVP user interface.
- Submit user questions to the accounting orchestration layer.
- Display the resulting answer, clarification request, unsupported-question response, or safe error.
- Preserve the separation between the user-facing answer and the silent technical trace.
- Remove greeting-demo examples, title, and description that no longer represent the product.

#### Non-goals

- Do not introduce the richer Streamlit analytical workspace planned for v1.
- Do not display the full technical trace by default.
- Do not add charts, result exploration, catalog browsing, or user-level access control.
- Do not bypass orchestration, validation, or tracing from the UI.

#### Dependencies

Depends on `add-accounting-question-orchestration` and `add-mvp-answer-tracing`.

#### Acceptance scenarios

- Given a user submits a supported accounting question in Gradio, when processing completes, then the chat displays the governed answer.
- Given a question requires clarification, when it is submitted, then the chat displays the clarification request and does not present a guessed answer.
- Given a question is unsupported or execution fails, when it is submitted, then the chat displays a safe user-facing response while the technical details remain in the trace.
- Given the application starts, when the chat is displayed, then no greeting-demo wording or behavior remains.

#### Verification strategy

- Test the chat callback with deterministic orchestration fixtures.
- Run the existing Gradio end-to-end test path where available.
- Verify supported, clarification, unsupported, and failure responses in the rendered chat.

### 7. `add-mvp-evaluation-suite`

#### User outcome

The project can demonstrate that the fixed MVP question suite produces correct answers while respecting the physical and SQL governance boundaries.

#### In scope

- Define expected results for the fixed accounting question suite.
- Test numerical correctness and answer behavior.
- Test selected source assets, relationships, filters, generated SQL safety, and validation outcomes.
- Include negative cases proving that `raw`, `stg`, and `audit` cannot be queried by the analytics workflow.
- Include end-to-end checks through the Gradio analytics chat where practical.
- Keep the suite as a regression baseline for later product phases.

#### Non-goals

- Do not evaluate the open-ended v1 analytical workspace.
- Do not claim broad database or connector support.
- Do not use evaluation success to waive query validation or catalog requirements.

#### Dependencies

Depends on the preceding MVP changes, especially orchestration, tracing, and the governed query service.

#### Acceptance scenarios

- Given each fixed supported question, when the MVP workflow runs, then the numerical result matches the expected result.
- Given each fixed question, when its trace is inspected, then the selected definitions, `core` assets, filters, SQL safety status, and execution outcome are correct.
- Given an attempt to query a non-core schema, when the workflow runs, then it is rejected and the rejection is observable in the trace or test result.
- Given a mutation or unsafe query path, when validation runs, then it is rejected before execution.

#### Verification strategy

- Run the complete deterministic MVP regression suite against the sandbox PostgreSQL database.
- Combine unit, integration, and Gradio end-to-end tests according to the risk of each workflow.
- Require both numerical correctness and governance assertions for the MVP acceptance gate.

## Physical Sandbox PostgreSQL Boundary

The phrase “sandbox PostgreSQL database” refers to the PostgreSQL database that contains the full ingestion, transformation, validation, and analytical model. It does not mean that every schema in that database is available to the analytics agent.

The schemas have different responsibilities:

```text
raw  -->  stg  -->  validation  -->  core
                                  |
                                  +--> audit and quality reporting
```

- `raw` is the ingestion landing area for source records.
- `stg` contains staging representations used during transformation and validation.
- `audit` contains rejected-record information and quality-related evidence.
- `core` contains the normalized, approved physical data model used by the MVP analytics workflow.

Only `core` is part of the MVP analytical catalog and query surface. The agent, planner, SQL generator, validator, executor, and evaluation suite must treat `raw`, `stg`, and `audit` as inaccessible analytical sources, even though the ingestion and validation pipeline may use them operationally.

The MVP uses PostgreSQL only. It does not introduce Trino, OpenMetadata, automatic metadata ingestion, schema drift detection, or general database connectivity. The declarative catalog is the runtime planning source of truth; future phases may compare it with runtime schemas, but that introspection is outside the MVP.

The core model must make supported business questions physically answerable. In particular, dimensions such as country must have an explicit semantic meaning and an identified `core` field or relationship. A similarly named column is not sufficient evidence that a business dimension is correctly modeled. The example question “What was gross margin in Germany during Q2 2025?” can only be supported after the meaning of “Germany” is explicitly defined.

## MVP Invariant Requirements

These requirements must remain true while the individual changes are refined and implemented:

1. **The analytics workflow can query only the `core` schema.** The PostgreSQL database also contains `raw`, `stg`, and `audit` schemas for ingestion, transformation, validation, rejection, and quality reporting. Those schemas are operational infrastructure, not analytical sources available to the agent.

2. **Business semantics are declarative.** Definitions for metrics such as revenue, cost, and gross margin, together with fiscal periods, dates, currencies, dimensions, formulas, and aggregation behavior, must be versioned and reviewable outside the language model.

3. **Physical metadata is declarative.** Approved `core` tables, columns, data types, aliases, relationships, join keys, and time fields must be explicit and testable. The planner must not discover or assume arbitrary database assets at runtime.

4. **Query execution is governed outside the language model.** The workflow must build logical plans, generate PostgreSQL SQL, validate it before execution, allow only approved read operations, reject mutations and schema changes, and enforce required filters, row limits, and timeouts.

5. **CrewAI orchestrates but does not own business truth.** The agent may interpret questions and coordinate tools, but it must rely on the semantic layer, the `core` catalog, the logical planner, and the governed query service.

6. **Evidence is retained for every question-and-answer cycle.** The technical trace must capture the question, intent, definitions, filters, source assets, relationships, logical plan, SQL, validation, execution, result summary, errors when applicable, and final answer without exposing secrets or unnecessary sensitive data.

7. **The greeting demo is replaced by the governed analytics chat.** The MVP user-facing application remains a Gradio chat interface, but its entry point must submit accounting questions to the governed orchestration workflow rather than execute the greeting behavior.

8. **The MVP is evaluated as a fixed, governed workflow.** Acceptance requires both numerical correctness for the supported accounting questions and correct behavior for source selection, filters, SQL safety, validation outcomes, non-core-schema rejection, and user-facing failure or clarification paths.

9. **The MVP remains PostgreSQL-specific and deliberately narrow.** It does not claim unrestricted text-to-SQL, general database connectivity, OpenMetadata integration, Trino execution, automated metadata ingestion, drift detection, or user-level access control.