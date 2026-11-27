# Tasks

## 1. Logical analytics catalog and calendar

- [ ] 1.1 Create a validated, physical-model-independent `mvp-analytics-catalog.yaml` for supported aggregate concepts, ratios, derived metrics including EBITDA and working capital, aliases, and the approved dimension IDs; verify the loader accepts valid entries and rejects physical table/column references and SQL expressions.
- [ ] 1.2 Create a versioned `mvp-calendar.yaml` with the initial Jan-Dec fiscal year and calendar quarter boundaries, plus configurable alternate boundaries; implement period normalization and verify Q1-Q4, fiscal-year, leap-year, custom-calendar, and “last quarter” cases using an injected reference date.

## 2. Controlled discovery tools

- [ ] 2.1 Implement an environment-configured, read-only dimension-member lookup adapter restricted to the approved dimension allowlist; verify it parameterizes search terms, rejects unknown dimensions, and handles exact, ambiguous, and missing matches with offline tests.
- [ ] 2.2 Add bounded catalog-search and reporting-period-resolution tools over the logical catalog and calendar resource; verify returned values use logical IDs and normalized date ranges without exposing physical schema details.

## 3. Query interpretation contract

- [ ] 3.1 Extend the typed structured-query model to represent one or more metrics, approved dimensions, filters, period grouping, and query/clarification/unsupported outcomes; verify valid and invalid outcome shapes with focused model tests.
- [ ] 3.2 Update query-agent instructions and tool registration so the agent uses catalog and discovery results, emits only logical structured queries, never generates SQL, and clarifies ambiguity; verify supported, ambiguous, and unsupported interpretations with mocked model responses.
- [ ] 3.3 Route unsupported outcomes through the orchestrator without validation or calculation while preserving the one-English-response contract; verify the short-circuit and existing clarification behavior with orchestrator tests.

## 4. Document the MVP boundary

- [ ] 4.1 Update the README examples: mark customer receivables/aging, EBITDA drivers, largest account movements, and customer/vendor ranking as out of scope; split the EBITDA comparison and cash-flow-driver examples so only deferred parts carry `*`; add the exact legend `(*) out of scope of the MVP` after the examples and list the approved dimensions/time dimensions, noting currency treatment remains unresolved; verify the examples and legend are unambiguous.

## 5. Verify the interpretation change

- [ ] 5.1 Run the offline backend unit suite and validate this OpenSpec change; verify resource loading, calendar resolution, tool resolution, supported/clarification/unsupported outcomes, and the orchestrator short-circuit all pass without a live provider or database.
