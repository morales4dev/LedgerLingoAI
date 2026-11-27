# LedgerLingoAI
Conversational AI for turning accounting and general ledger data into actionable financial answers and insights.

## Introduction

LedgerLingoAI is an analytics assistant designed for senior finance professionals, including accounting managers and CFOs. The MVP caller submits one text question per script invocation and receives one text response; requests do not share interaction history.

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

Python 3.12-3.13. Dependencies and supported Python versions are declared in `backend/pyproject.toml`, with exact resolutions in `backend/uv.lock`. The local environment is `backend/.venv`.

The importable async agent core and CLI live under `backend/src/ledgerlingo/`. The async OpenAI SDK client connects to the separately run LiteLLM Proxy. Tools are defined with the OpenAI Agents SDK's `@function_tool`; an explicit Python loop dispatches them without the SDK Runner.

## Setup

The backend environment lives at `backend/.venv` and is managed by uv. From the repository root:

```bash
cd backend
uv sync --locked
```

To run the local model proxy as well, sync its separate dependency group:

```bash
uv sync --locked --group proxy
```

Copy `.env.example` to `.env` at the **repo root** and set the provider key. `.env` is gitignored.

Start the LiteLLM Proxy from `backend/`:

```bash
uv run --locked --group proxy --env-file ../.env litellm --config litellm_config.yaml --port 4000
```

The example sets `LITELLM_PROXY_URL=http://localhost:4000/v1`, the OpenAI-compatible endpoint used by the app. Check that the proxy is live with `curl http://localhost:4000/health/liveliness`.

## Run

From `backend/`:

```bash
uv run --locked ledgerlingo "Ask one question here"
```

The CLI starts and closes the async client for each invocation. It does not register analytics tools yet. Python callers can pass an explicit sequence of `@function_tool`-decorated functions to `run_agent`; the loop validates arguments and propagates tool failures. Runner-managed approvals, guardrails, dynamic enablement, tool timeouts, and deferred loading are not supported.

## Test

From `backend/`:

```bash
uv run --locked python -m pytest
```

Offline unit tests live in `backend/tests/unit/` and mock model responses; they do not require provider credentials or network access.

## Agent OS vs product specs

- Agent constitution: `ai-specs/AGENTS.md`. Standards under `ai-specs/standards/` are coding rules plus pins, not pins only.
- Product specs: `openspec/specs/`.