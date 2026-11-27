# Proposal

## Why

The README currently describes analytical capabilities beyond the intended MVP, making it unclear which questions LedgerLingoAI should answer in its first governed analytics release. This change establishes a focused boundary that includes useful derived metrics while clearly identifying deferred analysis.

## What Changes

- Define the interpretation-layer MVP as simple aggregates, ratios, and configured derived metrics, including EBITDA and working capital. Allow time-series grouping, but defer calculated period-over-period changes.
- Add physical-model-independent logical catalog and configurable calendar resources. Restrict query dimensions to physical-model fields explicitly marked `dimension` or `time_dimension`; keep physical bindings outside the catalog.
- Give the query interpreter read-only tools to discover catalog definitions, resolve dimension values from approved data, and normalize periods from the configured calendar. Define agent instructions and a typed structured-query outcome, including clarification and unsupported outcomes.
- Explicitly defer ranking, driver analysis, receivables aging, and customer/vendor financial breakdowns.
- Clarify the README examples with asterisks and the legend `(*) out of scope of the MVP`; split mixed examples so supported requests are not incorrectly marked out of scope, and document the supported dimension policy.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `financial-query-processing`: Define supported MVP analytics, temporal grouping boundaries, and safe handling of deferred query families.

## Impact

- Product contract: `openspec/specs/financial-query-processing/spec.md`.
- Documentation: `README.md`.
- Agent instructions, typed interpretation contracts, read-only discovery tools, and declarative resources under `backend/src/resources/`.
- This change stops at query interpretation. It does not execute analytical queries against journal data or calculate/report financial results.

## Non-goals

- Executing analytical queries against the ledger, calculating financial results, or generating caller-facing reports from ledger data.
- Exposing physical table/column mappings to the query interpreter.
- Adding ranking, driver decomposition, aging, customer/vendor analysis, or period-over-period comparison.
- Changing the one-question/one-response invocation contract.
- Settling currency semantics; currency is excluded from the initial dimension whitelist pending a separate decision.
