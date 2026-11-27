# Tasks

## 1. Logical analytics catalog and calendar

- [x] 1.1 Create a validated, physical-model-independent `mvp-analytics-catalog.yaml` covering all 20 metric IDs in the spec, including `untagged_pnl_check`, aliases, approved dimensions, and required base-concept dependencies with stable tag IDs; verify catalog completeness and dependency resolution without requiring populated physical tag tables, and reject physical table/column references or SQL expressions in agent-facing metadata.
- [x] 1.2 Create a versioned `mvp-calendar.yaml` with the initial Jan-Dec fiscal year and calendar-quarter boundaries, configurable alternate boundaries, and an optional default reporting period; implement normalization and verify Q1-Q4, fiscal-year, leap-year, custom-calendar, configured-default, no-default, and “last quarter” cases using an injected reference date.

## 2. Controlled discovery tools

- [x] 2.1 Implement an environment-configured, read-only dimension-member lookup adapter restricted to the approved dimension allowlist; verify parameterized searches, unknown-dimension rejection, exact/ambiguous/missing matches, and a bounded company-code cardinality check that distinguishes one from multiple companies with offline tests.
- [x] 2.2 Add bounded catalog-search and reporting-period-resolution tools over the logical catalog and calendar resource; verify returned values use logical IDs and normalized date ranges without exposing physical schema details.

## 3. Query interpretation contract

- [x] 3.1 Extend the typed structured-query model to represent one or more metrics, approved dimensions, filters, normalized periods, and query/clarification/unsupported outcomes; verify valid and invalid outcome shapes with focused model tests.
- [x] 3.2 Update query-agent instructions and tool registration so the agent uses catalog and discovery results, emits only logical structured queries, never generates SQL, and clarifies ambiguity; verify supported, ambiguous, and unsupported interpretations with mocked model responses.
- [x] 3.3 Create a curated natural-language-to-structured-outcome golden set covering all 20 metric IDs, aliases, company/period resolution, ambiguous dimensions, and deferred requests; verify expected logical fields with offline mocked tests and provide an optional live-provider evaluation that does not assert exact response wording.
- [x] 3.4 Route unsupported outcomes through the orchestrator without validation or calculation while preserving the one-English-response contract; verify the short-circuit and existing clarification behavior with orchestrator tests.
- [x] 3.5 Add a developer-only `ledgerlingo interpret "..."` command that prints the typed interpretation as JSON and skips validation, calculation, and reporting; verify its output and short-circuit with mocked model calls, and confirm the normal caller command is unchanged.

## 4. Document the MVP boundary

- [x] 4.1 Update the README examples: mark customer receivables/aging, EBITDA drivers, largest account movements, and customer/vendor ranking as out of scope; split the EBITDA comparison and cash-flow-driver examples so only deferred parts carry `*`; add the exact legend `(*) out of scope of the MVP` after the examples and list the approved dimensions/time dimensions, noting currency treatment remains unresolved; verify the examples and legend are unambiguous.
- [x] 4.2 Document the developer-only `ledgerlingo interpret` command and its JSON outcomes in `backend/README.md`; verify the documented invocation matches the CLI and clearly differs from the normal one-shot answer path.

## 5. Verify the interpretation change

- [x] 5.1 Run the offline backend unit suite and validate this OpenSpec change; verify catalog completeness, calendar defaults and resolution, company-scope handling, tool resolution, golden cases, typed outcomes, and the orchestrator short-circuit without a live provider or database.
