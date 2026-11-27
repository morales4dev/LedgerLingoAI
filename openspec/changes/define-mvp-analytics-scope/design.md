# Design

## Context

See `proposal.md` for motivation and `specs/financial-query-processing/spec.md` for the behavior contract. The current interpreter accepts only one metric, an optional period, and string filters; it has no discovery tools. The existing accounting-semantics resource contains physical columns and SQL expressions, so it cannot be the agent-facing logical catalog.

## Goals / Non-Goals

**Goals:**

- Give the agent a versioned, physical-model-independent catalog for supported metrics, dimensions, aliases, and policies.
- Let the interpreter discover exact dimension members and normalize natural-language periods through controlled tools.
- Produce a typed structured query or a clarification/unsupported outcome, without exposing SQL or physical schema details to the model.
- Make the README distinguish supported MVP requests from deferred analysis and show the approved dimension whitelist.

**Non-Goals:**

- Executing analytical queries against ledger data, calculating results, or generating caller-facing financial reports.
- Letting the model inspect physical table/column mappings or generate SQL.
- Settling currency filtering, conversion, or mixed-currency aggregation policy.
- Rewriting the README introduction or changing the broader product vision.

## Decisions

### Separate logical analytics definitions from physical bindings

Create an agent-facing `mvp-analytics-catalog.yaml` that defines concepts, ratios, derived metrics, supported dimensions, synonyms, and interpretation policies using stable IDs. It must not contain physical table names, column names, or SQL expressions. Keep physical bindings inside a separate controlled adapter used by discovery tools; do not pass them to the interpreter. Define EBITDA and working capital as governed derived metrics referencing logical base concepts, reusing the existing metrics catalog where its definitions fit.

**Alternative considered:** expose the existing accounting-semantics YAML directly to the agent. Rejected because it mixes business meaning with physical columns and SQL.

### Whitelist dimensions from physical-model roles

The logical catalog includes only fields explicitly marked `dimension` or `time_dimension` in the current physical model: `company_code`, `cost_center`, `profit_center`, `tax_code`, `fiscal_year`, `fiscal_period`, `posting_date`, and `document_date`. It excludes attributes such as `country` and `currency`; currency policy remains unresolved. The model's existing rule that `document_date` is used only when explicitly requested remains in effect.

Dimension values are not copied into YAML because they can change with the data. A read-only lookup tool accepts only a logical dimension ID and a search term, then returns exact matching members through the controlled physical adapter. The adapter uses an explicit allowlist to map logical IDs to physical fields, parameterizes search values, and uses environment-backed read-only database credentials. The model cannot select arbitrary fields or submit SQL.

**Alternative considered:** maintain enumerated dimension values in YAML. Rejected because dynamic values would become stale and require manual synchronization.

### Configure reporting calendars as data

Create a separate versioned `mvp-calendar.yaml` resource. Its initial configuration defines calendar quarters as Q1 Jan-Mar, Q2 Apr-Jun, Q3 Jul-Sep, Q4 Oct-Dec and the fiscal year as Jan 1-Dec 31; the format must allow another company to configure different boundaries without changing interpreter code. Represent normalized date ranges as start-inclusive/end-exclusive. Resolve “last quarter” as the most recently completed calendar quarter relative to a reference date supplied by the application.

**Alternative considered:** hard-code quarter and fiscal-year rules in the agent prompt. Rejected because company-specific calendars must be configurable and deterministically testable.

### Keep interpretation outputs typed and bounded

Extend the structured query to represent one or more logical metrics, approved dimensions and filters, and normalized time periods. The interpretation outcome must distinguish a ready query, a clarification, and an unsupported request. Agent instructions require catalog/tool use for resolution, prohibit SQL and physical identifiers, and require clarification instead of guessing. Grouped time series are allowed; period-over-period delta/comparison fields are not.

**Alternative considered:** let the model return arbitrary JSON and validate only downstream. Rejected because the interpreter boundary needs a stable contract for orchestration and safe failure handling.

### Mark deferred examples and clauses precisely

Add `*` to the fully deferred customer receivables/aging, EBITDA-driver, largest-account-movement, and customer/vendor ranking examples. Split the EBITDA comparison and cash-flow-driver examples into supported and deferred parts, marking only the deferred parts. Place the legend `(*) out of scope of the MVP` after the examples. Document the approved dimension whitelist in a user-readable README section.

**Alternative considered:** mark every compound question with an out-of-scope part as wholly out of scope. Rejected because that would incorrectly label supported portions as unsupported.

## Risks / Trade-offs

- [The existing metrics catalog references base concepts from a physically coupled resource] → Move or adapt logical definitions without copying SQL or physical bindings into the agent-facing catalog.
- [Dimension lookup may reveal values not needed for a question] → Restrict lookups to whitelisted dimensions and read-only search operations with bounded results.
- [Currency treatment remains undecided] → Do not include currency in the initial dimension whitelist or assert a mixed-currency policy in this change.
- [The README introduction still describes capabilities beyond this MVP boundary] → Keep this change limited to the requested example annotations and dimension list; revise the broader introduction only with separate approval.

## Migration Plan

No persisted data migration is required. Add the logical catalog and calendar resources, wire only interpretation discovery through the controlled tools, and update the typed query contract and agent instructions. Do not connect the interpretation change to ledger calculation or reporting. Update the README examples, legend, and dimension whitelist; validate the resource schemas and add offline tests for catalog/calendar resolution and query outcomes.

## Open Questions

- Currency filter/grouping and mixed-currency behavior remain undecided and require the user's follow-up before currency support is specified.
