#!/usr/bin/env bash
set -euo pipefail

: "${REPRO_OUT:?REPRO_OUT must be set}"
: "${BIGQUERY_PROJECT:?BIGQUERY_PROJECT must be set}"
SA_KEY_FILE="$REPRO_OUT/.bigquery-sa.json"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"$SCRIPT_DIR/fetch-config.sh"
export CLOUDSDK_CONFIG="$REPRO_OUT/.gcloud"
mkdir -p "$CLOUDSDK_CONFIG"
chmod 700 "$CLOUDSDK_CONFIG"
gcloud auth activate-service-account --key-file="$SA_KEY_FILE" --quiet >/dev/null

bq_cmd() {
  command bq --project_id="$BIGQUERY_PROJECT" "$@"
}

bigquery_dataset_exists() {
  bq_cmd show "$BIGQUERY_PROJECT:$1" >/dev/null 2>&1
}

bigquery_validate_dataset() {
  local dataset="$1"
  if [[ ! "$dataset" =~ ^PROVEFIX_[A-Za-z0-9_]+$ ]]; then
    echo "[bigquery] refusing unsafe dataset name: $dataset" >&2
    return 2
  fi
}

bigquery_create_dataset() {
  local dataset="$1"
  bigquery_validate_dataset "$dataset"
  bq_cmd mk \
    --dataset \
    --location="$BIGQUERY_LOCATION" \
    --label=provefix:true \
    --description="source-bigquery remote e2e run ${dataset#PROVEFIX_}" \
    "$BIGQUERY_PROJECT:$dataset"
}

bigquery_drop_dataset() {
  local dataset="$1"
  bigquery_validate_dataset "$dataset"
  bq_cmd rm -r -f -d "$BIGQUERY_PROJECT:$dataset"
}

bigquery_verify_dataset_absent() {
  local dataset="$1"
  local output
  if output="$(bq_cmd show "$BIGQUERY_PROJECT:$dataset" 2>&1)"; then
    echo "[bigquery] dataset still exists after cleanup: $BIGQUERY_PROJECT:$dataset" >&2
    return 1
  fi
  if [[ "${output,,}" == *"not found"* || "${output,,}" == *"does not exist"* ]]; then
    echo "[bigquery] bq show confirmed dataset absent: $BIGQUERY_PROJECT:$dataset" >&2
    return 0
  fi
  echo "[bigquery] could not verify dataset absence: $output" >&2
  return 1
}
