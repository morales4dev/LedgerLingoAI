#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "${ROOT_DIR}"
docker compose up -d postgres

echo "Waiting for PostgreSQL healthcheck..."
for _ in {1..40}; do
  status="$(docker inspect --format='{{json .State.Health.Status}}' erp_mvp_postgres 2>/dev/null || true)"
  if [[ "${status}" == '"healthy"' ]]; then
    echo "PostgreSQL is healthy"
    exit 0
  fi
  sleep 2
done

echo "PostgreSQL did not become healthy in time"
exit 1
