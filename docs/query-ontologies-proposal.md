# LedgerLingoAI — Query Ontology Proposal

## Query taxonomy

Each financial query is classified independently across three axes:

### 1. Processing / Reasoning Requirement

Defines the operation required to transform accounting data into an answer:

- **Direct retrieval** — retrieve an existing value.
- **Aggregation** — combine multiple records through sums, grouping, or similar operations.
- **Ranking / Top-N** — aggregate or retrieve values, compare them, and select the highest/lowest N.
- **Derived calculation** — calculate a financial quantity from one or more accounting values.
- **Ratio / metric calculation** — calculate a ratio or defined financial metric.
- **Reconciliation / bridge** — explain the movement between an opening and closing financial state.
- **Driver decomposition** — identify the components that explain a change or outcome.
- **Statistical / inferential analysis** — use statistical methods such as anomaly detection, correlation, or regression.
- **Forecast / scenario** — estimate a future or hypothetical result using assumptions.

### 2. Financial Subject

Defines the financial or accounting object being queried:

- **Assets** — cash, trade receivables, inventory, PP&E, intangibles, financial assets, etc.
- **Liabilities** — trade payables, debt, lease liabilities, provisions, tax liabilities, etc.
- **Equity** — share capital, retained earnings, reserves, other equity components, etc.
- **Revenue and income** — revenue, other operating income, financial income, gains, etc.
- **Expenses** — cost of sales, personnel expenses, operating expenses, depreciation, amortisation, impairment, financial expenses, tax expense, etc.
- **Profitability / performance** — gross profit, EBITDA, EBIT, operating profit, net income, margins, etc.
- **Liquidity / working capital** — working capital, current assets/liabilities, liquidity, receivables, payables, cash conversion, etc.
- **Cash flow** — operating, investing, and financing cash flows; cash generation and consumption.
- **Capital structure** — equity, debt, net debt, leverage, etc.
- **General ledger / accounting movements** — account balances, journal entries, debits, credits, adjustments, reclassifications, accruals, reversals, etc.

The financial-subject taxonomy is grounded in the IFRS Conceptual Framework and relevant IFRS/IAS reporting standards. IFRS distinguishes assets, liabilities, equity, income and expenses as fundamental elements of financial reporting.

### 3. Analytical Reference Frame

Defines the basis against which the financial information is interpreted:

- **Point-in-time / single-period** — one defined financial state or period, with no analytical comparison.
- **Time-series / trend** — evolution across multiple periods.
- **Period-over-period comparison** — explicit comparison between periods, e.g. MoM, QoQ, or YoY.
- **Cross-sectional comparison** — comparison among entities or members of a dimension for the same analytical period.
- **Ranking** — ordering members of a population by a financial measure.
- **Composition / contribution** — analysing components relative to a total or base.
- **Benchmark / target** — comparison against budget, forecast, target, or another predefined benchmark.
- **Reconciliation** — explaining the transition between two financial states through their intervening movements.
- **Scenario / hypothetical** — evaluating a hypothetical or assumed future state.

These analytical concepts are consistent with established financial-analysis techniques including ratio analysis, common-size analysis, time-series analysis, cross-sectional analysis, and driver analysis.

## Dimensions

Dimensions should be kept separate from the three primary axes. They specify **by whom, where, or along what organisational/business attribute** the financial subject is analysed.

Examples:

- Customer
- Vendor
- Business unit
- Legal entity
- Geography
- Product
- Cost centre
- Project
- Account
- Account group

For example:

> Which customers have the highest receivables?

- **Processing:** Ranking / Top-N
- **Financial subject:** Trade receivables
- **Analytical reference frame:** Ranking
- **Dimension:** Customer

This separation prevents business dimensions such as “customer” from being treated as financial subjects such as “revenue” or “receivables”.

## Example queries

| # | Query | Processing | Financial subject | Analytical reference frame | Formula / calculation logic |
|---|---|---|---|---|---|
| 1 | What is our current accounts receivable balance? | Aggregation | Trade receivables | Point-in-time | **AR balance = Σ outstanding trade-receivable balances** at the selected reporting date. From GL movements: **AR balance = opening balance + Σ debits − Σ credits**, subject to the ledger's sign convention. |
| 2 | Which three customers have the largest outstanding receivables? | Ranking / Top-N | Trade receivables | Ranking | **Customer AR balance = Σ outstanding receivables for each customer**. Rank balances descending and return the top 3. |
| 3 | What was EBITDA last quarter? | Ratio / metric calculation | EBITDA / performance | Single-period | **EBITDA = EBIT + depreciation + amortisation**. Alternatively, where the configured methodology permits: **EBITDA = Revenue − operating expenses excluding D&A**. EBITDA is not an IFRS-defined subtotal, so its definition should be configurable. |
| 4 | How has revenue evolved over the last 24 months? | Aggregation | Revenue | Time-series / trend | **Revenueₜ = Σ recognised revenue amounts in period t**. Optional growth: **Growthₜ = (Revenueₜ / Revenueₜ₋₁ − 1) × 100**. |
| 5 | How much did operating expenses increase versus last year? | Derived calculation | Operating expenses | Period-over-period comparison | **Change = Opexₜ − Opexₜ₋₁**; **% change = (Opexₜ / Opexₜ₋₁ − 1) × 100**. |
| 6 | Which accounts contributed most to the decrease in EBITDA versus last year? | Driver decomposition | EBITDA / performance | Period-over-period comparison | For each account: **ΔAccount = Accountₜ − Accountₜ₋₁**. Map each movement to its EBITDA impact and rank the accounts by contribution to **ΔEBITDA = EBITDAₜ − EBITDAₜ₋₁**. |
| 7 | What percentage of revenue comes from each business unit? | Ratio / metric calculation | Revenue | Composition / contribution | **Business-unit revenue share = Business-unit revenue / Total revenue × 100** for the same reporting period. |
| 8 | What is our current ratio? | Ratio / metric calculation | Liquidity | Point-in-time | **Current ratio = Current assets / Current liabilities** at the selected reporting date. |
| 9 | What explains the movement in cash between the beginning and end of the quarter? | Reconciliation / bridge | Cash flow / cash | Reconciliation | **Ending cash = Beginning cash + CFO + CFI + CFF + effect of exchange-rate changes**, where applicable. The bridge decomposes the change into operating, investing, financing and other required movements. |
| 10 | Which business units are below their EBITDA margin target? | Ratio / metric calculation | EBITDA / profitability | Benchmark / target | **EBITDA margin = EBITDA / Revenue × 100**. For each business unit, calculate **margin − target margin**; a negative result means the unit is below target. |

## Formula conventions

The formulas describe the computational logic expected from the query layer; they are not, by themselves, mandatory IFRS presentation formulas. Underlying recognition and measurement should follow the applicable IFRS/IAS requirements. Management-defined metrics such as EBITDA should use an explicit, configurable definition.

## Accounting and analytical basis

The accounting ontology is grounded primarily in:

- **IFRS Conceptual Framework for Financial Reporting** — fundamental financial-statement elements and concepts.
- **IFRS 18 Presentation and Disclosure in Financial Statements** — presentation and disclosure of financial performance and management-defined performance measures; effective for annual periods beginning on or after 1 January 2027.
- **IAS 7 Statement of Cash Flows** — operating, investing, and financing cash flows.
- Relevant IFRS/IAS standards for the underlying financial subjects.

The analytical taxonomy is a product/query-design ontology rather than an IFRS-defined classification. It draws on established financial-analysis techniques such as ratio analysis, common-size analysis, time-series and cross-sectional analysis, comparison, and driver analysis.

### Key design principle

The three axes are **independent**:

> **Processing** = what must the system do?  
> **Financial subject** = what is it about?  
> **Reference frame** = relative to what is it interpreted?

A query should receive one classification on each axis, while optional dimensions specify the business or organisational breakdown.