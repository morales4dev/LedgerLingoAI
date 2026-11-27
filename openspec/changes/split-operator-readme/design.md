# Design

## Context

See [proposal.md](./proposal.md) for motivation. Today the root `README.md` holds product copy plus Stack / Setup / Run / Test, and `ai-specs/AGENTS.md` names that file as operator onboarding. There is no `backend/README.md`. `.env.example` stays at the repo root; setup commands already run from `backend/` and load `../.env`. `mvp-one-shot-analytics-contract` is a separate open change whose README task must not reintroduce a runbook into the root file.

## Goals / Non-Goals

**Goals:**

- Give operators one backend-local runbook whose commands match the current uv / proxy / CLI / pytest workflow.
- Keep the GitHub landing page as product copy plus one setup link.
- Point Agent OS onboarding at `backend/README.md` so later stack edits do not thicken the root README.

**Non-Goals:**

- Change how settings, the proxy, or the CLI work.
- Rewrite architecture or MVP sequence beyond any sentence that currently treats the root README as the runbook (today that pointer lives in the constitution).

## Decisions

### Split by audience, not freeze the root file

Keep introduction and example questions in the root README. Replace operational sections with a short "Developer setup" link to [`backend/README.md`](../../../backend/README.md). Leaving the root file byte-for-byte unchanged would leave a stale GitHub landing page and contradict the constitution update.

Alternative considered: root README untouched, all new text only under `backend/`. Rejected because GitHub shows the root file and it already contains the runbook.

### Operator runbook lives next to the Python project

`backend/README.md` documents `uv sync --locked`, the optional `proxy` group, copying repo-root `.env.example` to repo-root `.env`, starting LiteLLM from `backend/`, `uv run --locked ledgerlingo "…"`, and `uv run --locked python -m pytest`. Commands stay relative to `backend/`, matching [architecture-proposal.md](../../../docs/architecture-proposal.md).

Alternative considered: move `.env.example` into `backend/`. Rejected as out of scope; the runbook will say the env file stays at the repo root.

### Constitution owns the onboarding pointer

Change "Operator onboarding: root `README.md`" in `ai-specs/AGENTS.md` to `backend/README.md`. Do not copy the constitution into either README. Do not add Agent OS vs OpenSpec sections to the product landing page.

### Do not edit the one-shot change in this work

This change does not rewrite `mvp-one-shot-analytics-contract`. Apply sequencing: after this lands, that change's README task may mention the English one-shot contract in the root README but must not restore Stack / Setup / Run / Test there.

## Risks / Trade-offs

- **Operators miss `backend/README.md`** → Keep a visible root link with the path in plain text.
- **Root README still drifts when the CLI changes** → Constitution forbids putting the runbook back at the root; later stack changes edit `backend/README.md` only.
- **One-shot apply fights this split** → Sequencing note above; do not merge runbook text into the root file in that change.
- **Docs-only change with no automated tests** → Verify by reading both READMEs and grepping active guidance for stale "root README" onboarding language.

## Migration Plan

1. Add `backend/README.md` with the current root runbook (Stack / Setup / Run / Test), adjusted so paths are correct from `backend/`.
2. Trim the root README and add the setup link.
3. Update the constitution pointer.
4. Grep active docs for leftover operator-onboarding claims about the root README.
5. Rollback is a revert of those files; no data or dependency migration.

No open questions that affect this approach.
