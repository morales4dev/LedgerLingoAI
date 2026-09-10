#!/usr/bin/env bash
set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${ROOT_DIR}/.." && pwd)"
LOG_DIR="${ROOT_DIR}/logs"
mkdir -p "${LOG_DIR}"

if [[ ! -f "${ROOT_DIR}/.env" ]]; then
  echo "Missing .env in ${ROOT_DIR}. Copy .env.example to .env first."
  exit 1
fi

set -a
source "${ROOT_DIR}/.env"
set +a

run_step() {
  local step_name="$1"
  local command="$2"
  local log_file="${LOG_DIR}/${step_name}.log"

  echo "\n=== Running ${step_name} ==="
  if bash -c "${command}" >"${log_file}" 2>&1; then
    echo "${step_name}: OK"
    return 0
  fi

  echo "${step_name}: FAILED (see ${log_file})"
  return 1
}

# Hard stop steps (pipeline cannot continue without these)
run_step "01_prereqs" "${ROOT_DIR}/scripts/01_check_prereqs.sh" || exit 1
run_step "02_start_postgres" "${ROOT_DIR}/scripts/02_start_postgres.sh" || exit 1
run_step "03_prepare_source" "${ROOT_DIR}/scripts/03_prepare_source.sh" || exit 1
run_step "04_apply_schema" "${ROOT_DIR}/scripts/04_apply_schema.sh" || exit 1
run_step "05_load_raw" "${ROOT_DIR}/scripts/05_load_raw.sh" || exit 1

# Soft steps (continue on failure when feasible)
run_step "06_transform" "${ROOT_DIR}/scripts/06_transform.sh" || true
run_step "07_quality_reports" "${ROOT_DIR}/scripts/07_quality_reports.sh" || true

echo "\nPipeline completed. Check logs in ${LOG_DIR}."
