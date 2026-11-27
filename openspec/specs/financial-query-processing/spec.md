# financial-query-processing Specification

## Purpose

Processes one natural-language financial question through a structured query, deterministic validation and calculation, and a caller-facing report.

## Requirements

### Requirement: Represent interpreted questions as structured queries

For a supported question, the system SHALL represent the query agent's interpretation as a typed structured query for downstream validation and calculation, rather than exposing that internal structure as the caller's response.

#### Scenario: Supported question is interpreted
- **WHEN** a caller submits a supported financial question
- **THEN** the query interpretation stage produces a structured query for the orchestrator

### Requirement: Return clarification for ambiguous questions

The query interpretation stage SHALL return a typed clarification outcome when a question cannot be represented safely as a structured query.

#### Scenario: Question needs clarification
- **WHEN** a caller submits an ambiguous financial question
- **THEN** the orchestrator returns one English clarification response without invoking validation or calculation

### Requirement: Validate queries before calculation

The orchestrator SHALL validate each structured query before invoking the calculator and SHALL NOT calculate from a query whose validation result is not valid.

#### Scenario: Query passes validation
- **WHEN** the validator returns a valid result for a structured query
- **THEN** the orchestrator invokes the calculator with that query

#### Scenario: Query fails validation
- **WHEN** the validator returns a non-valid result for a structured query
- **THEN** the orchestrator does not invoke the calculator for that query

#### Scenario: Initial validator stub
- **WHEN** the initial scaffold validates a structured query
- **THEN** the validator returns a typed result indicating valid

### Requirement: Return a typed result from deterministic calculation

The calculator SHALL accept a validated structured query and return a typed financial result independently of natural-language answer generation.

#### Scenario: Initial calculator stub
- **WHEN** the initial scaffold calculates a validated structured query
- **THEN** it returns a typed financial result with an amount of 68

### Requirement: Report the calculation result to the caller

The result reporter SHALL convert the calculator's typed financial result into one English text response for the caller.

#### Scenario: Report the initial calculator result
- **WHEN** the reporter receives the initial scaffold's result with an amount of 68
- **THEN** it returns an English response that reports the amount as 68

### Requirement: Keep journal data and calculation results outside query interpretation

The query interpretation stage SHALL NOT receive journal data or calculator results. The natural-language question may be sent to the configured model during the MVP.

#### Scenario: Interpret a financial question
- **WHEN** the system sends a question for query interpretation
- **THEN** the interpretation input contains the question but not journal data or a calculator result
