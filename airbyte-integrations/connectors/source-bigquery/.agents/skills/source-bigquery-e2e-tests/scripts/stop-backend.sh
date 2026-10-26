#!/usr/bin/env bash
set -euo pipefail

: "${REPRO_OUT:?REPRO_OUT must be set}"
: "${PROVEFIX_DATASET:?PROVEFIX_DATASET must be set}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OWNED_MARKER="$REPRO_OUT/.provefix-owned-$PROVEFIX_DATASET"
BIGQUERY_CONFIG_FILE="${BIGQUERY_CONFIG_FILE:-$REPRO_OUT/.bigquery-config.json}"

cleanup_credentials() {
  if [[ -f "$BIGQUERY_CONFIG_FILE.fetched" ]]; then
    rm -f "$BIGQUERY_CONFIG_FILE" "$BIGQUERY_CONFIG_FILE.fetched"
  fi
  if [[ -f "$REPRO_OUT/.bigquery-sa.json.fetched" ]]; then
    rm -f "$REPRO_OUT/.bigquery-sa.json" "$REPRO_OUT/.bigquery-sa.json.fetched"
  fi
  rm -rf "$REPRO_OUT/.gcloud"
}
trap cleanup_credentials EXIT

if [[ -f "$OWNED_MARKER" ]]; then
  # shellcheck source=./bq-auth.sh
  source "$SCRIPT_DIR/bq-auth.sh"
  if bigquery_dataset_exists "$PROVEFIX_DATASET"; then
    bigquery_drop_dataset "$PROVEFIX_DATASET"
  fi
  bigquery_verify_dataset_absent "$PROVEFIX_DATASET"
  rm -f "$OWNED_MARKER"
  echo "[stop-backend] dropped owned dataset $BIGQUERY_PROJECT:$PROVEFIX_DATASET" >&2
else
  echo "[stop-backend] no ownership marker for $PROVEFIX_DATASET; leaving any dataset untouched" >&2
fi
