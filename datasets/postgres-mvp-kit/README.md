# PostgreSQL MVP Kit (Laptop)

This folder is a self-contained script package to load ERP synthetic data into a local PostgreSQL Docker container.

## Design goals

- Reproducible on another computer without Copilot.
- Keep this repository machine LFS-free if needed.
- In target machine, fetch LFS objects before loading data.
- Continue on feasible row-level data errors using reject tables.

## What this kit creates

- Docker PostgreSQL container.
- Schemas: `raw`, `stg`, `core`, `audit`.
- Raw ingestion from JSON/CSV files under `financial-output`.
- Set-based transform and validation for key accounting entities.
- Reject logging for invalid records.
- Quality report file.

## Target machine prerequisites

- Docker (already installed and running).
- Git.
- Python 3.
- git-lfs installed if `FETCH_LFS=1`.

## Transfer workflow

1. Clone repository in target machine.
2. Unzip this folder inside the cloned repository root.
3. Configure `.env`.
4. Run `./run_all.sh`.

## Quick start

```bash
cd postgres-mvp-kit
cp .env.example .env
./run_all.sh
```

## Behavior notes

- Step `03_prepare_source.sh` runs `git lfs pull` only when `FETCH_LFS=1`.
- `run_all.sh` hard-stops on critical infra/setup failures.
- `run_all.sh` continues on transform/report failures when feasible.
- Row-level rejects are written to:
  - `audit.reject_journal_entry_header`
  - `audit.reject_journal_entry_line`

## Execution order

`run_all.sh` executes:

1. `scripts/01_check_prereqs.sh`
2. `scripts/02_start_postgres.sh`
3. `scripts/03_prepare_source.sh`
4. `scripts/04_apply_schema.sh`
5. `scripts/05_load_raw.sh`
6. `scripts/06_transform.sh`
7. `scripts/07_quality_reports.sh`

## Useful commands

Open psql shell:

```bash
docker exec -it erp_mvp_postgres psql -U erp_user -d erp_mvp
```

Stop container:

```bash
docker compose down
```

Stop container and remove volume:

```bash
docker compose down -v
```

## Current MVP scope

This MVP includes normalized loading for:

- Chart of accounts
- Journal entry headers and lines
- Vendors
- Customers

Other dataset files are still ingested into `raw.file_records` and are available for next transformation steps.
