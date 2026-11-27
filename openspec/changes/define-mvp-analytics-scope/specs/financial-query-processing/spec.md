# Spec Delta

## ADDED Requirements

### Requirement: Support the complete MVP metric catalog
The query interpreter SHALL represent every supported MVP metric using its stable logical ID.

#### Scenario: Resolve a metric from the complete MVP set
- **WHEN** a caller requests `gross_profit`, `total_operating_costs`, `operating_profit`, `ebitda`, `net_finance_result`, `profit_before_tax`, `net_income`, `net_assets`, `working_capital`, `net_debt`, `gross_margin_pct`, `operating_margin_pct`, `ebitda_margin_pct`, `net_profit_margin_pct`, `current_ratio`, `quick_ratio`, `debt_to_equity`, `roa_pct`, `roe_pct`, or `untagged_pnl_check`
- **THEN** the interpreter uses the requested metric's stable logical ID in the structured query

#### Scenario: Request uses an MVP derived metric
- **WHEN** a caller asks for a configured MVP metric such as EBITDA or working capital
- **THEN** the interpreter represents that metric in a structured query for downstream processing

#### Scenario: Request uses the P&L reconciliation control
- **WHEN** a caller asks for the untagged P&L reconciliation check
- **THEN** the interpreter represents it using the `untagged_pnl_check` metric ID

#### Scenario: Request asks for a grouped time series
- **WHEN** a caller asks for a supported aggregate or metric across months, quarters, or years
- **THEN** the structured query requests grouping by those configured periods without requesting period-over-period changes

### Requirement: Restrict query dimensions to approved physical-model dimension roles
The interpreter SHALL expose only physical-model fields marked `dimension` or `time_dimension` as query dimensions. It SHALL NOT promote other physical attributes into dimensions.

#### Scenario: Caller requests an approved dimension
- **WHEN** a caller asks to filter or group by company code, cost center, profit center, tax code, fiscal year, fiscal period, posting date, or document date
- **THEN** the interpreter uses that approved dimension in the structured query

#### Scenario: Caller requests an attribute not approved as a dimension
- **WHEN** a caller asks to group by country or currency
- **THEN** the interpreter does not represent that attribute as an approved dimension

### Requirement: Resolve dimension members through controlled discovery
The interpreter SHALL resolve requested dimension members through a read-only lookup restricted to approved dimension identifiers and SHALL use returned values rather than inventing physical identifiers or SQL.

#### Scenario: A dimension member matches uniquely
- **WHEN** a caller uses a business term that matches one member of an approved dimension
- **THEN** the structured query uses the exact member value returned by the lookup

#### Scenario: A dimension member is ambiguous or unavailable
- **WHEN** a caller's term matches multiple members or no member of an approved dimension
- **THEN** the interpreter returns a clarification outcome rather than guessing a value

### Requirement: Resolve reporting periods using configured calendar rules
The interpreter SHALL normalize calendar quarters and fiscal years using versioned, configurable calendar rules and SHALL resolve “last quarter” as the most recently completed calendar quarter.

#### Scenario: Resolve an initial calendar quarter
- **WHEN** a caller requests Q1, Q2, Q3, or Q4 under the initial calendar configuration
- **THEN** the period resolves to Jan-Mar, Apr-Jun, Jul-Sep, or Oct-Dec respectively

#### Scenario: Resolve an initial fiscal year
- **WHEN** a caller requests a fiscal year under the initial calendar configuration
- **THEN** the period resolves from Jan 1 through Dec 31 of that year

#### Scenario: Resolve last quarter
- **WHEN** a caller asks for “last quarter”
- **THEN** the period resolves to the most recently completed calendar quarter relative to the request's reference date

#### Scenario: Use a configured default reporting period
- **WHEN** a caller omits the reporting period and a default is configured
- **THEN** the structured query uses that default period and its normalized date range

#### Scenario: Clarify when no reporting period default exists
- **WHEN** a caller omits the reporting period and no default is configured
- **THEN** the interpreter returns a clarification instead of guessing a period

### Requirement: Preserve metric-specific time behavior
The system SHALL apply normalized reporting periods according to each configured metric's time behavior. Flow metrics SHALL aggregate activity within the start-inclusive, end-exclusive date window. Point-in-time metrics SHALL use the balance at the end-exclusive cutoff and SHALL NOT sum activity across that window.

#### Scenario: Calculate a flow metric for a reporting period
- **WHEN** a caller requests EBITDA for a fiscal year
- **THEN** the structured query uses the configured flow metric over that year's start-inclusive, end-exclusive date window

#### Scenario: Calculate a point-in-time metric at period end
- **WHEN** a caller requests working capital at the end of a fiscal year
- **THEN** the structured query uses the point-in-time balance at that fiscal year's end-exclusive cutoff rather than summing changes during the year

### Requirement: Resolve omitted company scope safely
The interpreter SHALL use an explicitly requested company when it resolves uniquely. If company scope is omitted, it SHALL use the sole company available in the ledger only when exactly one exists; otherwise it SHALL return a clarification.

#### Scenario: Omitted company with a single ledger company
- **WHEN** a caller omits company scope and the ledger contains exactly one company
- **THEN** the structured query uses that company's approved logical dimension value

#### Scenario: Omitted company with multiple ledger companies
- **WHEN** a caller omits company scope and the ledger contains more than one company
- **THEN** the interpreter asks which company to use and does not return an executable query

### Requirement: Keep interpretation independent of physical query syntax
The interpreter SHALL produce a structured query using approved logical catalog identifiers and SHALL NOT generate SQL or expose physical table and column references in its output.

#### Scenario: Produce a structured query
- **WHEN** a caller asks a supported analytical question
- **THEN** the interpreter returns a structured query containing logical metric, dimension, filter, and period selections without SQL

### Requirement: Inspect interpretation output without downstream execution
The developer CLI SHALL provide an interpretation-only command that prints the typed query, clarification, or unsupported outcome as JSON without invoking validation, calculation, or reporting. The normal caller command SHALL retain its one-question/one-English-response behavior.

#### Scenario: Inspect a natural-language question
- **WHEN** a developer runs `ledgerlingo interpret` with one natural-language question
- **THEN** the CLI prints the typed interpretation outcome as JSON and does not invoke downstream stages

### Requirement: Reject deferred analytics families safely
The system SHALL NOT represent requests requiring ranking, driver analysis, receivables aging, customer/vendor financial breakdowns, or period-over-period comparisons as executable structured queries.

#### Scenario: Caller requests deferred analysis
- **WHEN** a caller asks for ranking, driver analysis, aging, customer/vendor financial breakdowns, or a period-over-period comparison
- **THEN** the system returns one English unsupported-outcome response without invoking validation or calculation
