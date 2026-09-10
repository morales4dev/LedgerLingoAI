# LedgerLingoAI
Conversational AI assistant answering financial and accounting queries using NLP.

## Introduction

LedgerLingoAI is a Conversational NLP AI driven assistant project designed to bridge the gap between complex financial data and human language. The system processes financial terminology, tracks core finance entities, and provides structured, text-based answers to user queries.

## Stack

Python 3.12.12. Pins are in `backend/requirements.txt` (runtime) and `backend/requirements-dev.txt` (pytest, Playwright). Do not copy pin lists into this README by hand after that.

App entry: `backend/src/app.py` (`gr.ChatInterface`, MiniMax-M2.5 via the OpenAI-compatible client).

## Setup

Package installs use `uv pip install --python backend/.venv/bin/python` (from repo root) or `uv pip install --python .venv/bin/python` (from `backend/`). Do not use bare `pip install`.

```bash
cd backend
uv venv .venv --python 3.13.3
uv pip install --python .venv/bin/python -r requirements.txt
uv pip install --python .venv/bin/python -r requirements-dev.txt
```

Copy `.env.example` to `.env` at the **repo root** and fill values. `.env` is gitignored.

## Run

From `backend/`:

```bash
.venv/bin/python src/app.py
```

VS Code launch config `Twin backend` uses `${workspaceFolder}/backend` and loads `${workspaceFolder}/.env`.

## Test

From `backend/`:

```bash
.venv/bin/python -m pytest
```

Units: `backend/tests/unit/`. Playwright E2E against Gradio chat is a later slot under `backend/tests/e2e/` (not a live MiniMax suite in v1).

## Agent OS vs product specs

- Agent constitution: `ai-specs/AGENTS.md`. Standards under `ai-specs/standards/` are coding rules plus pins, not pins only.
- Product specs: `openspec/specs/`.