# Design

## Context

See `proposal.md` for motivation and `specs/financial-query-processing/spec.md` for the behavior contract. The current interpreter accepts only one metric, an optional period, and string filters; it has no discovery tools. The existing accounting-semantics resource contains physical columns and SQL expressions, so it cannot be the agent-facing logical catalog.

## Goals / Non-Goals

**Goals:**

- Give the agent a versioned, physical-model-independent catalog for supported metrics, dimensions, aliases, and policies.
- Let the interpreter discover exact dimension members and normalize natural-language periods through controlled tools.
- Produce a typed structured query or a clarification/unsupported outcome, without exposing SQL or physical schema details to the model.
- Let developers inspect one natural-language interpretation as typed JSON without executing downstream stages.
- Make the README distinguish supported MVP requests from deferred analysis and show the approved dimension whitelist.

**Non-Goals:**

- Executing analytical queries against ledger data, calculating results, or generating caller-facing financial reports.
- Letting the model inspect physical table/column mappings or generate SQL.
- Settling currency filtering, conversion, or mixed-currency aggregation policy.
- Rewriting the README introduction or changing the broader product vision.

## Decisions

### Separate logical analytics definitions from physical bindings

Create an agent-facing `mvp-analytics-catalog.yaml` that defines the complete supported MVP metric set, aliases, supported dimensions, and interpretation policies using stable IDs. The metric set is all 20 entries in `metrics.yaml`, including `untagged_pnl_check` as a control metric, together with the base-concept dependencies those definitions require. The catalog must not contain physical table names, column names, or SQL expressions. Keep physical bindings inside a separate controlled adapter used by discovery tools; do not pass them to the interpreter. Keep `metrics.yaml` as the canonical source for derived-metric formula definitions. The logical catalog references those metric IDs rather than duplicating formula trees or introducing a second expression language; deterministic code resolves and applies the definitions, while the interpreter receives only the logical metadata it needs.

Tag-filtered base concepts retain their stable logical tag IDs as semantic dependencies. The interpreter emits the selected metric ID, not tag codes, SQL, or physical table details. Translating those tag references into physical reads is later query-execution work: the tag tables are defined by the separate `tags-in-physical-data-model` change, and their tag definitions and account assignments are populated by a subsequent DML change. Neither physical DDL nor populated tag data is required to produce an interpretation-only structured query, but both are prerequisites before those metrics can be executed against the ledger.

**Alternative considered:** expose the existing accounting-semantics YAML directly to the agent. Rejected because it mixes business meaning with physical columns and SQL.

### Whitelist dimensions from physical-model roles

The logical catalog includes only fields explicitly marked `dimension` or `time_dimension` in the current physical model: `company_code`, `cost_center`, `profit_center`, `tax_code`, `fiscal_year`, `fiscal_period`, `posting_date`, and `document_date`. It excludes attributes such as `country` and `currency`; currency policy remains unresolved. The model's existing rule that `document_date` is used only when explicitly requested remains in effect.

Dimension values are not copied into YAML because they can change with the data. A read-only lookup tool accepts only a logical dimension ID and a search term, then returns exact matching members through the controlled physical adapter. The adapter uses an explicit allowlist to map logical IDs to physical fields, parameterizes search values, and uses environment-backed read-only database credentials. The model cannot select arbitrary fields or submit SQL.

When a question names a company, resolve it against approved `company_code` members and clarify if the match is ambiguous or unavailable. When company scope is omitted, use a bounded cardinality lookup that stops after finding two distinct company codes: use the company only if exactly one exists; otherwise ask the caller to choose. Do not enumerate an unbounded member list or infer a company when multiple companies are present.

**Alternative considered:** maintain enumerated dimension values in YAML. Rejected because dynamic values would become stale and require manual synchronization.

### Configure reporting calendars as data

Create a separate versioned `mvp-calendar.yaml` resource. Its initial configuration defines calendar quarters as Q1 Jan-Mar, Q2 Apr-Jun, Q3 Jul-Sep, Q4 Oct-Dec and the fiscal year as Jan 1-Dec 31; the format must allow another company to configure different boundaries without changing interpreter code. Represent normalized date ranges as start-inclusive/end-exclusive. Preserve each metric's configured time behavior when applying a normalized period: flow metrics use activity within the date window, while point-in-time metrics use the balance at the end-exclusive cutoff rather than summing activity across the window. Resolve “last quarter” as the most recently completed calendar quarter relative to a reference date supplied by the application.

The calendar may define a default reporting period. If a question omits its period, use that configured default; if no default is configured, return a clarification instead of guessing.

**Alternative considered:** hard-code quarter and fiscal-year rules in the agent prompt. Rejected because company-specific calendars must be configurable and deterministically testable.

### Keep interpretation outputs typed and bounded

Extend the structured query to represent one or more logical metrics, approved dimensions and filters, and normalized time periods. The interpretation outcome must distinguish a ready query, a clarification, and an unsupported request. Agent instructions require catalog/tool use for resolution, prohibit SQL and physical identifiers, and require clarification instead of guessing. Grouped time series are allowed; period-over-period delta/comparison fields are not.

**Alternative considered:** let the model return arbitrary JSON and validate only downstream. Rejected because the interpreter boundary needs a stable contract for orchestration and safe failure handling.

### Expose interpretation for developer inspection

Add a developer-only `interpret` CLI command that accepts one natural-language question, invokes the query interpreter, and prints the typed query, clarification, or unsupported outcome as JSON. It must call the interpretation stage directly and must not invoke validation, calculation, or reporting. The normal CLI invocation and its one-question/one-English-response behavior remain unchanged.

**Alternative considered:** inspect model output through the normal answer command. Rejected because that path intentionally returns only the caller-facing response and continues through downstream stages.

### Separate offline contract tests from live model evaluation

Use offline tests with mocked completions for deterministic schema, tool, and orchestration behavior. Maintain a curated natural-language-to-expected-structured-outcome golden set for semantic evaluation; allow it to run against a configured live provider on demand, but do not make exact live-model wording or output a required CI assertion.

**Alternative considered:** require live provider calls in the unit suite. Rejected because credentials, network availability, cost, and model variability would make CI unreliable.

### Mark deferred examples and clauses precisely

Add `*` to the fully deferred customer receivables/aging, EBITDA-driver, largest-account-movement, and customer/vendor ranking examples. Split the EBITDA comparison and cash-flow-driver examples into supported and deferred parts, marking only the deferred parts. Place the legend `(*) out of scope of the MVP` after the examples. Document the approved dimension whitelist in a user-readable README section.

**Alternative considered:** mark every compound question with an out-of-scope part as wholly out of scope. Rejected because that would incorrectly label supported portions as unsupported.

## Risks / Trade-offs

- [The existing metrics catalog references base concepts from a physically coupled resource] → Move or adapt logical definitions without copying SQL or physical bindings into the agent-facing catalog.
- [Dimension lookup may reveal values not needed for a question] → Restrict lookups to whitelisted dimensions and read-only search operations with bounded results.
- [A golden natural-language evaluation may vary across model/provider versions] → Keep live evaluation optional and assert logical fields/outcomes rather than exact response wording.
- [Metric definitions reference tags before physical assignments are populated] → Keep interpretation independent of tag-table availability and require the separate DDL and DML prerequisites before metric execution is introduced.
- [Currency treatment remains undecided] → Do not include currency in the initial dimension whitelist or assert a mixed-currency policy in this change.
- [The README introduction still describes capabilities beyond this MVP boundary] → Keep this change limited to the requested example annotations and dimension list; revise the broader introduction only with separate approval.

## Migration Plan

No persisted data migration is required. Add the logical catalog and calendar resources, wire only interpretation discovery through the controlled tools, and update the typed query contract and agent instructions. Do not connect the interpretation change to ledger calculation or reporting. Update the README examples, legend, and dimension whitelist; validate the resource schemas and add offline tests for catalog/calendar resolution and query outcomes.

## Open Questions

- Currency filter/grouping and mixed-currency behavior remain undecided and require the user's follow-up before currency support is specified.
