# Proposal

## Why

The README currently describes analytical capabilities beyond the intended MVP, making it unclear which questions LedgerLingoAI should answer in its first governed analytics release. This change establishes a focused boundary that includes useful derived metrics while clearly identifying deferred analysis.

## What Changes

- Define the user-facing MVP metric catalog as all 20 entries in the existing `metrics.yaml`, including `untagged_pnl_check` as a control metric, with their required base-concept dependencies. Allow time-series grouping, but defer calculated period-over-period changes.
- Preserve tag-based filters in the logical base-concept dependencies using stable tag IDs; the interpreter emits logical metric IDs, not physical tag or schema details.
- Add physical-model-independent logical catalog and configurable calendar resources. Restrict query dimensions to physical-model fields explicitly marked `dimension` or `time_dimension`; keep physical bindings outside the catalog.
- Give the query interpreter read-only tools to discover catalog definitions, resolve dimension values from approved data, and normalize periods from the configured calendar. If a question omits its company, use the only company in the ledger when exactly one exists; otherwise clarify. Use a configured default period when available; otherwise clarify. Define agent instructions and typed query, clarification, and unsupported outcomes.
- Add a developer-only interpretation command that accepts a natural-language question and prints its typed structured outcome as JSON without running validation, calculation, or reporting.
- Validate the interpretation contract with offline mocked tests and a curated natural-language-to-structured-query golden set; keep live-provider evaluation optional.
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
- Physical tag tables and tag assignments are separate prerequisites for later metric execution: DDL belongs to `tags-in-physical-data-model`, and population DML belongs to a subsequent change. Neither is implemented here.
- This change stops at query interpretation. It does not execute analytical queries against journal data or calculate/report financial results. The developer-only inspection command does not change the normal one-question/one-English-response caller path.

## Non-goals

- Executing analytical queries against the ledger, calculating financial results, or generating caller-facing reports from ledger data.
- Exposing physical table/column mappings to the query interpreter.
- Adding ranking, driver decomposition, aging, customer/vendor analysis, or period-over-period comparison.
- Changing the one-question/one-response invocation contract.
- Settling currency semantics; currency is excluded from the initial dimension whitelist pending a separate decision.
