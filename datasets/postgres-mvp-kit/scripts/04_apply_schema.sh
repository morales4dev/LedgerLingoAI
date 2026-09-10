#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

set -a
source "${ROOT_DIR}/.env"
set +a

run_sql() {
  local file="$1"
  docker exec -i erp_mvp_postgres psql \
    -U "${POSTGRES_USER}" \
    -d "${POSTGRES_DB}" \
    -v ON_ERROR_STOP=1 \
    -f - < "${file}"
}

run_sql "${ROOT_DIR}/sql/01_schemas.sql"
run_sql "${ROOT_DIR}/sql/02_tables_raw.sql"
run_sql "${ROOT_DIR}/sql/03_tables_stg_core.sql"
run_sql "${ROOT_DIR}/sql/04_quality_objects.sql"

echo "Schema applied"
