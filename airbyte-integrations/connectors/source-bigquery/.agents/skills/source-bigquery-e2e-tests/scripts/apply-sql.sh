#!/usr/bin/env bash
set -euo pipefail

: "${REPRO_OUT:?REPRO_OUT must be set}"
: "${PROVEFIX_DATASET:?PROVEFIX_DATASET must be set}"
: "${BIGQUERY_PROJECT:?BIGQUERY_PROJECT must be set}"
: "${BIGQUERY_LOCATION:?BIGQUERY_LOCATION must be set}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIXTURE="${1:-${DEFAULT_FIXTURE:?DEFAULT_FIXTURE must be set}}"

if [[ ! -f "$FIXTURE" ]]; then
  echo "[apply-sql] fixture not found: $FIXTURE" >&2
  exit 2
fi

# shellcheck source=./bq-auth.sh
source "$SCRIPT_DIR/bq-auth.sh"
temporary_sql="$(mktemp "$REPRO_OUT/.bigquery-fixture.XXXXXX.sql")"
trap 'rm -f "$temporary_sql"' EXIT
sed \
  -e "s|\${PROVEFIX_DATASET}|$PROVEFIX_DATASET|g" \
  -e "s|\${BIGQUERY_PROJECT}|$BIGQUERY_PROJECT|g" \
  "$FIXTURE" > "$temporary_sql"
bq_cmd query \
  --use_legacy_sql=false \
  --location="$BIGQUERY_LOCATION" \
  --dataset_id="$BIGQUERY_PROJECT:$PROVEFIX_DATASET" < "$temporary_sql"
