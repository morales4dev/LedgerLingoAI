# LedgerLingoAI
Conversational AI for turning accounting and general ledger data into actionable financial answers and insights.

## Introduction

LedgerLingoAI is a conversational AI assistant designed for senior finance professionals, including accounting managers and CFOs.

It bridges complex accounting and general ledger data with natural-language interaction, enabling finance professionals to ask questions about their financial data and receive directly usable answers and insights.

It supports financial data retrieval, period-over-period analysis, financial metric calculation, variance and driver analysis, aging analysis, and dimensional analysis across customers, vendors, business units, and general ledger accounts.

## What LedgerLingoAI Can Answer
LedgerLingoAI is designed to answer questions such as:

1. **Accounts Receivable**
   - What is the current accounts receivable balance, and how has it changed over time?

2. **Customer Receivables**
   - Which customers have the highest outstanding receivables, and what is the aging of those balances?

3. **Balance Sheet**
   - What are the company’s total assets, liabilities, and equity, and how have they evolved over the past few years?

4. **EBITDA**
   - What is the company’s EBITDA, and how has EBITDA changed compared with previous periods?

5. **EBITDA Drivers**
   - What are the main drivers of the change in EBITDA between two periods?

6. **Cash Flow**
   - What are the company’s operating, investing, and financing cash flows, and what are the main drivers of change?

7. **General Ledger Movements**
   - Which general ledger accounts have experienced the largest increases or decreases during the current period?

8. **Revenue and Expenses**
   - What are the company’s total revenue and operating expenses by month, quarter, or business unit?

9. **Customer, Vendor, and Business Unit Analysis**
   - Which customers, vendors, or business units account for the largest share of revenue or expenses?

10. **Financial Indicators**
    - What are the company’s key financial indicators — such as working capital, current ratio, debt-to-equity, gross margin, and EBITDA margin — based on the accounting data?

## Stack

Python 3.13.3. Pins are in `backend/requirements.txt` (runtime) and `backend/requirements-dev.txt` (pytest, Playwright). Do not copy pin lists into this README by hand after that.

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