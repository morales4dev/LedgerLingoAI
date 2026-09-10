#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_DIR="$(cd "${ROOT_DIR}/.." && pwd)"

set -a
source "${ROOT_DIR}/.env"
set +a

cd "${REPO_DIR}"

if [[ "${FETCH_LFS}" == "1" ]]; then
  if command -v git-lfs >/dev/null 2>&1; then
    echo "Fetching Git LFS objects in target repo..."
    # git lfs pull
    git lfs pull --include="financial-output/**"
  else
    echo "FETCH_LFS=1 but git-lfs is not installed"
    exit 1
  fi
else
  echo "Skipping git lfs pull (FETCH_LFS=${FETCH_LFS})"
fi

if [[ ! -f "${REPO_DIR}/${DATASET_DIR}/journal_entries.json" ]]; then
  echo "Expected file missing: ${REPO_DIR}/${DATASET_DIR}/journal_entries.json"
  echo "If this repo uses Git LFS, run with FETCH_LFS=1 and ensure git-lfs is installed."
  exit 1
fi

echo "Source data is ready"
