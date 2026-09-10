#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo ROOT_DIR=$ROOT_DIR
REPO_DIR="$(cd "${ROOT_DIR}/.." && pwd)"
echo REPO_DIR=$REPO_DIR

set -a
source "${ROOT_DIR}/.env"
set +a

command -v docker >/dev/null 2>&1 || { echo "docker is required"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "python3 is required"; exit 1; }
command -v git >/dev/null 2>&1 || { echo "git is required"; exit 1; }

if [[ ! -d "${REPO_DIR}/${DATASET_DIR}" ]]; then
  echo "Dataset directory not found: ${REPO_DIR}/${DATASET_DIR}"
  exit 1
fi

echo DATASET_DIR=${REPO_DIR}/${DATASET_DIR}

echo "Prerequisites OK"
