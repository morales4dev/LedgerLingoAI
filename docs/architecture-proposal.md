# LedgerLingoAI Architecture Proposal

## 1. Purpose

LedgerLingoAI is a conversational analytics assistant for accounting and finance professionals. It translates natural-language questions into governed, explainable answers over accounting and general-ledger data.

The product should keep business knowledge outside the language model. Metrics, dimensions, approved relationships, and queryable data assets must be explicit, reviewable, and testable.

The architecture evolves in three phases:

- **MVP:** prove the analytical workflow over a fixed sandbox PostgreSQL model.
- **v1:** provide a richer analytical user interface and introduce a catalog platform while retaining PostgreSQL.
- **v2:** add automated metadata ingestion, drift detection, and database abstraction through Trino.

Access control is out of scope until v3 or later.

## 2. Architectural Principles

1. **Business semantics are explicit.** Definitions such as revenue, EBITDA, gross margin, fiscal period, and variance must be represented in a declarative semantic layer rather than hidden in prompts.
2. **Physical metadata is explicit.** The catalog declares which schemas, tables, columns, and relationships are approved for analytical use.
3. **The agent orchestrates; it does not own business truth.** The agent may interpret a question and coordinate tools, but it must rely on the semantic layer and metadata catalog.
4. **Execution is governed.** Generated SQL is validated before execution. Read-only behavior, approved assets, row limits, and query timeouts are enforced outside the language model.
5. **The application is separated from execution technology.** PostgreSQL is the initial executor. A later Trino executor should be addable without redesigning the semantic layer or the user experience.
6. **Evidence is retained.** Each question-and-answer cycle produces a detailed technical trace for evaluation, debugging, and auditability.

## 3. Target Layer Model

```text
User Interface
      |
Agent / Orchestrator
      |
      +---------------------+
      |                     |
Semantic Layer       Metadata Catalog
business meaning     physical approved assets
      |                     |
      +----------+----------+
                 |
          Query Planner
          / SQL Generator
                 |
           SQL Validator
                 |
          Query Executor
                 |
       PostgreSQL or Trino
```

The semantic layer and metadata catalog are complementary:

- **Semantic layer:** what does a business concept mean?
- **Metadata catalog:** where are the approved physical assets needed to answer it?
- **Query planner:** how can the semantic request be mapped to those assets?
- **SQL validator:** is the generated query safe and within policy?
- **Query executor:** where is the validated query run?

## 4. Phase Plan

### 4.1 MVP: Governed Analytics over Sandbox PostgreSQL

```text
Gradio
  -> CrewAI agent
  -> Declarative semantic layer
       + declarative metadata catalog
  -> Query planner / SQL generator
  -> SQL validator
  -> PostgreSQL executor
  -> Sandbox PostgreSQL database
```

#### MVP technology and scope

- **User interface:** Gradio chat interface.
- **Agent framework:** CrewAI.
- **Semantic layer:** versioned, declarative files in Git.
- **Metadata catalog:** versioned, declarative files in Git.
- **Database:** sandbox PostgreSQL database.
- **Supported data model:** the sandbox PostgreSQL schema is the complete data model supported by the MVP.
- **Query executor:** PostgreSQL only.
- **SQL validation:** read-only and policy validation before execution.
- **Access control:** not included.
- **Metadata introspection:** not part of the MVP runtime. The declarative catalog is the source of truth, with future schema validation planned.

The MVP should be deliberately narrow. It is intended to prove reliable answers over a known accounting model, not general database connectivity or unrestricted text-to-SQL.

#### MVP catalog contents

The declarative catalog should contain the minimum physical information required by the query planner:

- database and schema identifiers
- approved tables and views
- approved columns and relevant data types
- descriptions and user-facing aliases
- approved relationships and join keys
- time dimensions and period semantics
- optional status such as trusted or deprecated

Business ownership, data quality, sensitivity tags, and freshness can be represented later as the catalog grows, but they are not required to prove the MVP workflow.

#### MVP question-answer flow

Example question:

> What was gross margin in Germany during Q2 2025?

1. Interpret the question into a structured intent: metric, dimensions, filters, and time period.
2. Resolve the business metric from the semantic layer: `gross_margin = revenue - cost`.
3. Resolve physical assets and approved relationships from the metadata catalog.
4. Build a logical query plan.
5. Generate PostgreSQL SQL.
6. Validate that the SQL is read-only, uses approved assets, applies required filters, and respects row and timeout limits.
7. Execute the query against the sandbox PostgreSQL database.
8. Generate the user-facing answer from the validated result.
9. Write a detailed technical trace for the complete cycle.

The chat displays the answer to the user. The technical trace is generated silently by the backend, one file per question-and-answer cycle. It should include, when available:

- request and conversation identifiers
- original user question
- parsed intent
- semantic definitions selected
- applied filters and time period
- source tables and columns
- selected relationships and joins
- logical query plan
- generated SQL
- validation rules and validation status
- execution status, timing, and errors
- result summary used to produce the answer
- final answer

The trace format and location should be designed for automated MVP evaluation and later observability, while avoiding secrets and unnecessary sensitive data.

#### MVP success criterion

The MVP succeeds when a fixed suite of accounting questions produces expected results from the sandbox PostgreSQL database. Evaluation should check both numerical correctness and important behavior such as selected source assets, applied filters, generated SQL safety, and validation outcomes.

### 4.2 v1: Richer Analytical UI and Catalog Platform

```text
Streamlit
  -> CrewAI agent
  -> Declarative semantic layer
       + OpenMetadata catalog capability
  -> Query planner / SQL generator
  -> SQL validator
  -> PostgreSQL executor
  -> Sandbox PostgreSQL database
```

#### v1 objectives and scope

- Replace the MVP chat-only interface with Streamlit to support a richer analytical workspace.
- Add UI elements such as result tables, charts, filters, query details, and other analytical views as justified by user needs.
- Keep CrewAI as the agent framework.
- Keep the PostgreSQL executor.
- Introduce OpenMetadata as the catalog platform or catalog integration.
- Add catalog/schema consistency validation.
- Expand the accounting and financial scope beyond the fixed MVP question suite.
- Do not introduce database abstraction or Trino yet.
- Do not introduce access control yet.

The exact Streamlit features should be driven by the analytical workflow, not by a framework change alone. The purpose of the switch is to support a richer interface than a chat-only Gradio application.

#### CrewAI and LangGraph

Switching frameworks is not a v1 objective. CrewAI remains the selected framework unless implementation evidence demonstrates that it prevents required UI or workflow capabilities.

The CrewAI-versus-LangGraph question remains an open v1 engineering decision, not a commitment to migrate. If evaluated, the comparison should use concrete requirements such as structured state, retries, human approval, tool orchestration, deterministic SQL validation, testing, tracing, and operational complexity.

#### Catalog authority in v1

The recommended authority boundary is:

- **Git declarative semantic layer:** authoritative for business definitions and approved analytical relationships.
- **OpenMetadata:** catalog platform for technical metadata, discovery, documentation, ownership, governance, and future lineage and quality metadata.
- **PostgreSQL:** runtime data store.

During v1, OpenMetadata may be populated or updated through controlled publication rather than automatic database introspection. Automated ingestion is planned for v2.

#### v1 success criterion

The v1 succeeds when users can ask open-ended questions across a broader accounting and financial scope and receive useful, correct, and understandable responses. The fixed MVP suite remains a regression suite, but v1 evaluation expands to conversational usefulness, appropriate clarification, relevant data selection, and useful analytical presentation.

### 4.3 v2: Ingestion, Drift Detection, and Database Abstraction

```text
Data sources
  -> metadata ingestion
  -> OpenMetadata
  -> catalog/schema consistency checks

Streamlit
  -> CrewAI agent
  -> Semantic layer + OpenMetadata catalog
  -> Query planner / SQL generator
  -> SQL validator
  -> PostgreSQL executor or Trino executor
  -> PostgreSQL and additional supported databases
```

#### v2 objectives and scope

- Add controlled metadata ingestion from PostgreSQL and additional data sources.
- Detect schema and metadata drift between declared models, catalog metadata, and runtime sources.
- Keep business semantics and approved analytical relationships explicitly governed.
- Add a Trino query executor behind the executor boundary.
- Demonstrate the same logical query plan against PostgreSQL and at least one additional database through Trino.
- Expand database support incrementally rather than claiming automatic support for every Trino connector.

Trino is an execution and connectivity abstraction. It does not remove the need to handle connector permissions, data types, SQL behavior, performance, pushdown, and source-specific limitations.

#### v2 success criterion

The v2 succeeds when metadata is kept current through controlled ingestion and drift checks, and a supported logical query can execute through either the PostgreSQL executor or the Trino executor without changing business definitions or the user-facing workflow.

## 5. Authority and Change Flow

```text
Git semantic definitions and approved contracts
                    |
                    v
          Query planning and validation
                    ^
                    |
OpenMetadata technical catalog <--- controlled publication or ingestion
                    ^
                    |
             Runtime data sources
```

In the early phases, explicit Git-managed definitions are preferred because they are reviewable, reproducible, and aligned with the known sandbox model. Introspection is introduced later as a validation and synchronization mechanism, not as a replacement for deliberate business modeling.

A catalog or schema change should be reviewable and should identify its impact on metrics, relationships, queries, tests, and user-facing answers.

## 6. Security and Governance Boundaries

Before v3, the system has no user-level access control. This is an explicit scope decision, not an implied capability.

Even without authentication and authorization, the query path must enforce technical safety:

- only approved read operations
- approved tables, views, and columns
- no `INSERT`, `UPDATE`, `DELETE`, `CREATE`, `ALTER`, or equivalent mutation
- required filters where defined by the semantic model
- row limits where appropriate
- query timeouts
- validation before execution
- trace output that does not expose secrets

## 7. Risks and Open Questions

### Open for v1

- Whether OpenMetadata should remain an enrichment and governance layer over Git-managed definitions or become authoritative for some technical metadata.
- Which additional Streamlit views provide the most value: tables, charts, filters, query explanations, source details, or other controls.
- Whether CrewAI continues to meet workflow requirements compared with LangGraph. No migration is planned unless evidence requires it.
- How much of the accounting and financial domain should be included in the first open-ended v1 scope.
- Whether v1 should use controlled manual publication to OpenMetadata throughout, or introduce a limited ingestion path earlier.

### Planned for v2

- Which additional database should be supported first through Trino.
- Which metadata sources and ingestion schedules are required.
- Which drift checks block deployment versus produce warnings.
- How SQL dialect and data type differences are represented in the logical query and executor contracts.

## 8. Summary

```text
MVP: Gradio + CrewAI + Git declarative models + sandbox PostgreSQL
v1:  Streamlit + CrewAI + OpenMetadata + PostgreSQL
v2:  ingestion and drift detection + Trino + additional databases
```

The central design goal is to keep the semantic and planning contracts stable while infrastructure evolves around them. PostgreSQL is intentionally the first executor, OpenMetadata is introduced when catalog capabilities justify it, and Trino is deferred until multiple database sources create a concrete need.
