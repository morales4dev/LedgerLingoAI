# Proposal

## Why

The root README now mixes product story, operator runbook, and Agent OS pointers. That makes GitHub's landing page too operational, and it fights the preference to keep product copy stable while backend setup changes. Split those audiences before more analytics work lands more setup text in the wrong file.

## What Changes

- Keep the root `README.md` product-facing: what LedgerLingoAI is, who it is for, example questions, and a single link to backend setup.
- Add `backend/README.md` as the operator runbook: uv environment, `.env` at the repo root, LiteLLM Proxy, CLI run, and pytest.
- Move Stack / Setup / Run / Test (and the Agent OS vs product-specs pointer) out of the root README.
- Update `ai-specs/AGENTS.md` so operator onboarding is `backend/README.md`, not the root README.
- Point other active setup references (architecture/MVP docs, standards, OpenSpec context if they currently send operators to the root README) at `backend/README.md`.
- Leave `mvp-one-shot-analytics-contract` as the request-contract change; its README task must not reintroduce operator setup into the root file.

## Capabilities

### New Capabilities

None. This documentation/OS change declares `skip_specs: true`.

### Modified Capabilities

None. Product behavior and requirements remain unchanged.

## Impact

- Root `README.md` and new `backend/README.md`.
- Agent constitution (`ai-specs/AGENTS.md`) operator-onboarding pointer.
- Active setup/onboarding sentences in architecture, MVP, standards, or `openspec/config.yaml` only if they currently treat the root README as the runbook.
- No application code, dependencies, APIs, or product specs.

## Non-goals

- Freeze the root README completely (it still gets a short developer-setup link and loses operational sections).
- Move `.env` / `.env.example` into `backend/`.
- Change CLI, proxy, or test behavior.
- Implement analytics tools, catalogs, or the ideas-file intent loop.
- Apply or rewrite `mvp-one-shot-analytics-contract`.
- Add CI or thicken Agent OS policy beyond the onboarding path.
