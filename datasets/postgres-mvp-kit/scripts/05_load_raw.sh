#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

set -a
source "${ROOT_DIR}/.env"
set +a

VENV_DIR="${ROOT_DIR}/.venv"
if [[ ! -d "${VENV_DIR}" ]]; then
  python3 -m venv "${VENV_DIR}"
fi

source "${VENV_DIR}/bin/activate"
pip install --quiet --upgrade pip
pip install --quiet psycopg[binary]

python "${ROOT_DIR}/python/load_raw.py" \
  --repo-root "${ROOT_DIR}/.." \
  --dataset-dir "${DATASET_DIR}" \
  --db-host "127.0.0.1" \
  --db-port "${POSTGRES_PORT}" \
  --db-name "${POSTGRES_DB}" \
  --db-user "${POSTGRES_USER}" \
  --db-password "${POSTGRES_PASSWORD}"

echo "Raw load finished"
