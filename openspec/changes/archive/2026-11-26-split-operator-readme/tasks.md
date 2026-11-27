# Tasks

## 1. Operator runbook

- [x] 1.1 Add `backend/README.md` with Stack, Setup, Run, and Test from the current root README, keeping commands relative to `backend/` and `.env` at the repo root; verify the documented `uv sync`, proxy, CLI, and pytest commands match `backend/pyproject.toml` and `.env.example`.
- [x] 1.2 Omit Agent OS / OpenSpec constitution dumps from `backend/README.md`; verify that file does not quote `ai-specs/AGENTS.md` beyond a possible one-line pointer if needed for setup.

## 2. Product landing page

- [x] 2.1 Keep the root README introduction and example-question list; replace Stack / Setup / Run / Test and the Agent OS vs product-specs section with a short Developer setup link to `backend/README.md`; verify the root file has no uv/proxy/pytest runbook and still names the product and sample questions.
- [x] 2.2 Confirm the root README link path is `backend/README.md` in plain text; verify a reader can find the runbook from GitHub's landing page without opening Agent OS files.

## 3. Agent OS pointer

- [x] 3.1 Change operator onboarding in `ai-specs/AGENTS.md` from root `README.md` to `backend/README.md`; verify that sentence is the only onboarding pointer and the constitution is not copied into either README.
- [x] 3.2 Search active guidance (`README.md`, `backend/README.md`, `ai-specs/`, `docs/`, `openspec/config.yaml`) for leftover claims that operator onboarding lives in the root README; verify none remain outside this change's records and archived OpenSpec history.

## 4. Validate the change

- [x] 4.1 Run `openspec validate split-operator-readme --type change` and confirm `skip_specs: true` still holds; verify no application code, lockfile, or `.env.example` location changed.

## Workflow follow-up

- Archive only after explicit user approval. Do not archive in apply.
- When applying `mvp-one-shot-analytics-contract`, do not restore Stack / Setup / Run / Test in the root README.
