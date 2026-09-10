# PostgreSQL MVP Kit - How To

This guide explains how to reproduce the full local MVP pipeline on another computer.

## What this kit does

- Starts a local PostgreSQL container with Docker.
- Creates database schemas and tables.
- Loads ERP data from JSON/CSV into `raw` tables.
- Transforms data to normalized `core` tables.
- Logs row-level rejects and keeps processing when feasible.
- Produces a quality report.

## Prerequisites on target computer

- Docker installed and running.
- Git installed.
- Python 3 installed.
- `git-lfs` installed if you want to fetch LFS-managed files automatically.

## Transfer and setup flow

1. Clone repository:

```bash
git clone https://github.com/meghahonna/erp_data_sample.git
cd erp_data_sample
```

2. Unzip `postgres-mvp-kit` into repository root.

Expected path after unzip:

- `erp_data_sample/postgres-mvp-kit`

3. Configure environment:

```bash
cd postgres-mvp-kit
cp .env.example .env
```

4. Edit `.env` values as needed:

- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_PORT`
- `DATASET_DIR` (default: `financial-output`)
- `FETCH_LFS`:
  - `1` = run `git lfs pull` before loading
  - `0` = skip LFS pull

Example `.env` values:

```bash
POSTGRES_DB=erp_mvp
POSTGRES_USER=erp_user
POSTGRES_PASSWORD=erp_pass
POSTGRES_PORT=5433
```

## Run everything

From `postgres-mvp-kit`:

```bash
./run_all.sh
```

## Execution order

`run_all.sh` runs these scripts in order:

1. `scripts/01_check_prereqs.sh`
2. `scripts/02_start_postgres.sh`
3. `scripts/03_prepare_source.sh`
4. `scripts/04_apply_schema.sh`
5. `scripts/05_load_raw.sh`
6. `scripts/06_transform.sh`
7. `scripts/07_quality_reports.sh`

## Error handling behavior

- Critical setup failures stop execution.
- Feasible later-step failures are logged and pipeline continues.
- Invalid rows are captured in reject tables:
  - `audit.reject_journal_entry_header`
  - `audit.reject_journal_entry_line`

## Output and logs

- Step logs are written under `postgres-mvp-kit/logs/`.
- Quality report is written to:
  - `postgres-mvp-kit/logs/quality_report.txt`

## Useful operational commands

Open SQL shell:

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

## What is included in MVP scope

Current normalized transformations include:

- Chart of accounts
- Journal entry headers and lines
- Vendors
- Customers

Other files are still loaded into `raw.file_records` and can be transformed in next iterations.

## Troubleshooting

### Step 01: Prerequisites check fails

**"docker is required"**
- Docker is not installed or not in PATH.
- Fix: Install Docker. Ensure it is in your `$PATH` and running.
- Verify: `docker --version` and `docker ps`

**"python3 is required"**
- Python 3 is not installed or not in PATH.
- Fix: Install Python 3.8 or later.
- Verify: `python3 --version`

**"git is required"**
- Git is not installed or not in PATH.
- Fix: Install Git.
- Verify: `git --version`

**"Dataset directory not found"**
- `financial-output/` folder is missing or `DATASET_DIR` in `.env` points to wrong location.
- Fix: Verify `.env` has correct `DATASET_DIR` path (default: `financial-output`).
- Verify: `ls -la ../financial-output/` shows JSON/CSV files.

### Step 02: PostgreSQL container fails to start

**"Cannot connect to Docker daemon"**
- Docker is not running.
- Fix: Start Docker Desktop or Docker daemon.
- Verify: `docker ps` should work without errors.

**"Port X is already allocated"**
- Another service is already using `POSTGRES_PORT` (default: 5433).
- Fix: Either stop the conflicting service or change `POSTGRES_PORT` in `.env` to an unused port.
- Verify: `netstat -tlnp | grep 5433` (Linux/Mac) or `netstat -ano | findstr :5433` (Windows).
- Rerun: `./run_all.sh`

**Container exits immediately**
- Check logs: `docker logs erp_mvp_postgres`
- Common cause: Invalid environment variables or insufficient memory.
- Fix: Verify `.env` values. Ensure Docker has at least 2GB RAM available.

### Step 03: Data preparation fails

**"FETCH_LFS=1 but git-lfs is not installed"**
- Git LFS is required to download large files, but not installed.
- Fix option A: Install git-lfs.
  - Ubuntu/Debian: `sudo apt-get install git-lfs`
  - MacOS: `brew install git-lfs`
  - Windows: `choco install git-lfs` or download from https://git-lfs.github.com
  - Then: `git lfs install && git lfs pull` (in repo root)
  - Rerun: `./run_all.sh`
- Fix option B: If data files are already downloaded locally, set `FETCH_LFS=0` in `.env` and rerun.

**"Expected file missing: .../journal_entries.json"**
- File exists but is a Git LFS pointer (small text file, ~100 bytes), not actual content.
- Cause: Repository was cloned before `git-lfs` was installed, or `git lfs pull` was not run.
- Fix:
  ```bash
  cd erp_data_sample  # (repo root, not postgres-mvp-kit)
  git lfs install
  git lfs pull
  cd postgres-mvp-kit
  ./run_all.sh
  ```

**"File content validation error"**
- LFS pointer file detected when expecting JSON/CSV content.
- Cause: Same as above (Git LFS not properly pulled).
- Fix: Run `git lfs pull` in repo root, then rerun pipeline.

### Step 04-05: Schema/data load fails

**"psycopg[binary] installation fails"**
- Python dependencies failed to install.
- Cause: Corrupted venv or missing system libraries.
- Fix:
  ```bash
  rm -rf .venv/
  python3 -m venv .venv
  source .venv/bin/activate  # (or .venv\Scripts\activate on Windows)
  pip install --upgrade pip
  pip install psycopg[binary]
  ```
  Then rerun: `./run_all.sh`

**"Connection refused" or "Cannot connect to database"**
- PostgreSQL container is not running or not ready.
- Fix: Check container status: `docker ps | grep erp_mvp_postgres`
- If not running: `docker compose up -d` from `postgres-mvp-kit/`
- If running but not responding: Wait 10-20 seconds for healthcheck to pass, then retry.

**"Disk full" or "No space left on device"**
- Docker volume or disk is full.
- Cause: Journal entries are large (~154MB JSON, ~33MB CSV).
- Fix:
  ```bash
  docker compose down -v  # Remove volume
  df -h  # Check disk space
  ./run_all.sh
  ```

**"Invalid JSON" or "CSV parse error" in load_raw.py**
- Individual records failed to parse or insert.
- Behavior: Pipeline logs rejects and continues (this is by design).
- Verify: Rejects are in database tables:
  ```sql
  SELECT * FROM audit.reject_journal_entry_header LIMIT 5;
  SELECT * FROM audit.reject_journal_entry_line LIMIT 5;
  ```
- These are expected and logged. Check `logs/05_load_raw.log` for details.

### Step 06: Transform fails

**Transform queries fail or complete with warnings**
- Cause: Data quality issues or schema mismatches.
- Behavior: Pipeline logs errors and continues (soft fail).
- Fix: Inspect logs and query reject tables.
  ```bash
  cat logs/06_transform.log
  # Then in psql:
  SELECT COUNT(*) FROM audit.reject_journal_entry_header;
  SELECT * FROM audit.pipeline_events WHERE stage = 'transform';
  ```
- Non-critical transforms can fail; raw data is still loaded.

**"Table or column does not exist"**
- Schema was not created or is incomplete.
- Fix:
  ```bash
  docker compose down -v
  ./run_all.sh
  ```

### Step 07: Quality report generation fails

**Report not generated or empty**
- Cause: Transform step had too many failures or schema issues.
- Behavior: Pipeline continues; report may be partial.
- Verify: `cat logs/quality_report.txt`
- Inspect: Query audit tables for event logs.
  ```sql
  SELECT * FROM audit.pipeline_events ORDER BY event_time DESC;
  ```

### General debugging steps

**Check all step logs:**
```bash
ls -lah logs/
cat logs/01_*.log    # Check each step
```

**Open database shell:**
```bash
docker exec -it erp_mvp_postgres psql -U erp_user -d erp_mvp
# Then run SQL to inspect data
\dt raw.*          # List raw tables
SELECT COUNT(*) FROM raw.file_records;
SELECT COUNT(*) FROM core.coa_accounts;
SELECT COUNT(*) FROM audit.reject_journal_entry_header;
```

**Full restart from scratch:**
```bash
docker compose down -v       # Stop and remove volume
rm -rf .venv/                # Clear venv
./run_all.sh                 # Fresh run
```

**Verify prerequisites before running:**
```bash
docker --version
python3 --version
git --version
ls -la ../financial-output/journal_entries.json
```

## Clean rerun

To rerun from scratch with a clean database volume:

```bash
docker compose down -v
./run_all.sh
```
