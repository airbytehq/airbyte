#!/usr/bin/env bash
set -euo pipefail

: "${REPRO_OUT:?REPRO_OUT must be set}"
: "${PROVEFIX_DATASET:?PROVEFIX_DATASET must be set}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OWNED_MARKER="$REPRO_OUT/.provefix-owned-$PROVEFIX_DATASET"

if [[ ! -f "$OWNED_MARKER" ]]; then
  echo "[reset-databases] refusing to reset an unowned dataset: $PROVEFIX_DATASET" >&2
  exit 1
fi

# shellcheck source=./bq-auth.sh
source "$SCRIPT_DIR/bq-auth.sh"
bigquery_validate_dataset "$PROVEFIX_DATASET"
if bigquery_dataset_exists "$PROVEFIX_DATASET"; then
  bigquery_drop_dataset "$PROVEFIX_DATASET"
fi
bigquery_verify_dataset_absent "$PROVEFIX_DATASET"
bigquery_create_dataset "$PROVEFIX_DATASET"
echo "[reset-databases] recreated dataset $BIGQUERY_PROJECT:$PROVEFIX_DATASET" >&2
