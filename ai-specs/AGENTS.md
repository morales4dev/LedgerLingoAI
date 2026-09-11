# LedgerLingoAI agent constitution

Read this file first. Product specs live in `openspec/specs/`. Agent standards live under `ai-specs/standards/` (never `ai-specs/specs/`).

## Language

- Repo content (code, docs, issues, commits): English.
- Chat with the user: English.

## Canonical OS tree

- Constitution: this file.
- Agent standards: `ai-specs/standards/` (`python.md`, `testing.md`, `context7.md`). Never `ai-specs/specs/`.
- Project skills: `ai-specs/skills/`.
- OpenSpec CLI skills: `.github/skills/` (do not move them into `ai-specs`).
- Product specs: `openspec/specs/`.

### Project Architecture & Sub-Module Directory Map

This repository is split into specific micro-domains. When working inside these folders, respect their local architectures and internal rule files:

- `backend/src/` — Core Python backend entry points, API routes, and configuration wrappers.
- `backend/src/greeting/` — CrewAI Greeting Module. Contains the localized multi-agent workflows, task definitions, and UI interfaces.
	- Local rules pointer: Refer to [backend/src/greeting/AGENTS.md](../backend/src/greeting/AGENTS.md) before making edits or otherwise working in this module.

## Load skills

Load OpenSpec CLI skills from `.github/skills/` when proposing, applying, updating, syncing, or archiving a change. Load project skills from `ai-specs/skills/` when the user asks for that workflow (for example `adversarial-review` before archive).

## Stack and testing

See `ai-specs/standards/python.md` and `ai-specs/standards/testing.md`. See `ai-specs/standards/context7.md` for docs lookup.

## Process

### Small steps

Work in small diffs. One concern per change. Do not mix Agent OS edits with product behavior.

### TDD

Write or update a failing test before production code when the work is testable. Details: `ai-specs/standards/testing.md`.

### Do not change product behavior without an OpenSpec change

Do not edit visitor-facing Gradio chat or `backend/src/**` unless a product change (with artifacts) says so.

### Product docs vs OS docs

- Agent OS: `ai-specs/` (this file, `standards/`, `skills/`).
- Product specs: `openspec/specs/`.
- Operator onboarding: root `README.md`. Do not dump this constitution into README.

Update docs that the change makes stale.

### OS edits need a proposal plus explicit user yes

Agent OS and OpenSpec process edits need an OpenSpec change (proposal, design, tasks; `skip_specs: true` when there is no product behavior) and an explicit user yes before apply. Do not silently thicken constitution or standards.

### Artifacts then code then verify

Planning artifacts first, then implementation, then verify. Archive only after explicit user approval. Do not archive in apply.

### Branches, review, quality gate

Work on a feature branch. Local quality gate: pytest units from `backend/` (no network) and `openspec validate <change> --type change`. No new CI in OS-only work.

## OpenSpec

Schema stays `spec-driven`. Do not invent product specs for OS-only / tooling-only changes. Those changes set `skip_specs: true`.
