# Spec Delta

## ADDED Requirements

### Requirement: Support the defined MVP analytics families
The query interpretation stage SHALL represent simple aggregates, ratios, and configured derived metrics in the MVP catalog, including EBITDA and working capital. Queries MAY request these metrics grouped by configured time periods, but SHALL NOT request calculated period-over-period deltas or comparisons.

#### Scenario: Request uses an MVP derived metric
- **WHEN** a caller asks for a configured MVP metric such as EBITDA or working capital
- **THEN** the interpreter represents that metric in a structured query for downstream processing

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

### Requirement: Keep interpretation independent of physical query syntax
The interpreter SHALL produce a structured query using approved logical catalog identifiers and SHALL NOT generate SQL or expose physical table and column references in its output.

#### Scenario: Produce a structured query
- **WHEN** a caller asks a supported analytical question
- **THEN** the interpreter returns a structured query containing logical metric, dimension, filter, and period selections without SQL

### Requirement: Reject deferred analytics families safely
The system SHALL NOT represent requests requiring ranking, driver analysis, receivables aging, customer/vendor financial breakdowns, or period-over-period comparisons as executable structured queries.

#### Scenario: Caller requests deferred analysis
- **WHEN** a caller asks for ranking, driver analysis, aging, customer/vendor financial breakdowns, or a period-over-period comparison
- **THEN** the system returns one English unsupported-outcome response without invoking validation or calculation
