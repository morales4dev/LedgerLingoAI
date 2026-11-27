# LedgerLingoAI
An analytics assistant for turning accounting and general ledger data into actionable financial answers and insights.

## Introduction

LedgerLingoAI is an analytics assistant designed for senior finance professionals, including accounting managers and CFOs. The MVP Python script submits one English text question per invocation and prints one English text response. Internal agent and tool iterations stay inside that invocation; requests do not share question history or interaction state.

The MVP interpreter is limited to a configured catalog of 20 financial metrics, approved dimensions, and normalized reporting periods. It does not yet execute calculations against journal data.

## MVP analytics scope
The MVP is designed to interpret supported questions such as:

1. **Working capital and liquidity**
   - What are working capital, the current ratio, and the quick ratio for ACME in FY2024?

2. **Customer receivables**
   - (*) Which customers have the highest outstanding receivables, and what is the aging of those balances?

3. **Balance sheet**
   - What are net assets and net debt for ACME at the end of FY2024?

4. **EBITDA**
   - What is EBITDA for ACME in Q1 2024?
   - (*) How has EBITDA changed compared with previous periods?

5. **EBITDA Drivers**
   - (*) What are the main drivers of the change in EBITDA between two periods?

6. **Cash Flow**
   - What are the company’s operating, investing, and financing cash flows?
   - (*) What are the main drivers of change?

7. **General Ledger Movements**
   - (*) Which general ledger accounts have experienced the largest increases or decreases during the current period?

8. **Revenue and Expenses**
   - What are gross profit, operating profit, and EBITDA by month, quarter, or profit center?

9. **Customer, Vendor, and Business Unit Analysis**
   - (*) Which customers or vendors account for the largest share of revenue or expenses?

10. **Financial Indicators**
    - What are gross margin, operating margin, EBITDA margin, net profit margin, debt-to-equity, ROA, or ROE for ACME in FY2024?

11. **P&L reconciliation**
    - What is the untagged P&L reconciliation check for ACME in FY2024?

(*) out of scope of the MVP

Approved dimensions are `company_code`, `cost_center`, `profit_center`, `tax_code`, `fiscal_year`, `fiscal_period`, `posting_date`, and `document_date`. Currency is not an approved dimension; currency treatment remains unresolved.

## Developer setup

Setup, run, and test live in [`backend/README.md`](backend/README.md).

