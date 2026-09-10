#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${ROOT_DIR}/logs"
mkdir -p "${LOG_DIR}"

set -a
source "${ROOT_DIR}/.env"
set +a

docker exec -i erp_mvp_postgres psql \
  -U "${POSTGRES_USER}" \
  -d "${POSTGRES_DB}" \
  -f - < "${ROOT_DIR}/sql/06_reports.sql" > "${LOG_DIR}/quality_report.txt"

echo "Quality report generated at ${LOG_DIR}/quality_report.txt"
