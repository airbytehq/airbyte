#!/usr/bin/env bash
set -euo pipefail

OLDER_THAN_HOURS=4
DRY_RUN=false
for arg in "$@"; do
  case "$arg" in
    --older-than-hours=*)
      OLDER_THAN_HOURS="${arg#*=}"
      ;;
    --dry-run)
      DRY_RUN=true
      ;;
    *)
      echo "usage: $(basename "$0") [--older-than-hours=N] [--dry-run]" >&2
      exit 2
      ;;
  esac
done
if [[ ! "$OLDER_THAN_HOURS" =~ ^[0-9]+$ ]]; then
  echo "[sweep-orphans] --older-than-hours must be a non-negative integer" >&2
  exit 2
fi

REPRO_OUT="${REPRO_OUT:-/tmp/source-bigquery-repro}"
GSM_PROJECT="${GSM_PROJECT:-dataline-integration-testing}"
BIGQUERY_PROJECT="${BIGQUERY_PROJECT:-dataline-integration-testing}"
BIGQUERY_LOCATION="${BIGQUERY_LOCATION:-US}"
BIGQUERY_SECRET_NAME="${BIGQUERY_SECRET_NAME:-SECRET_SOURCE-BIGQUERY_CREDENTIALS__CREDS}"
BIGQUERY_CONFIG_FILE="${BIGQUERY_CONFIG_FILE:-$REPRO_OUT/.bigquery-config.json}"
export REPRO_OUT GSM_PROJECT BIGQUERY_PROJECT BIGQUERY_LOCATION BIGQUERY_SECRET_NAME BIGQUERY_CONFIG_FILE
if [[ ! "$BIGQUERY_LOCATION" =~ ^[A-Za-z0-9_-]+$ ]]; then
  echo "[sweep-orphans] invalid BigQuery location: $BIGQUERY_LOCATION" >&2
  exit 2
fi
REGION="${BIGQUERY_LOCATION,,}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cleanup_credentials() {
  BIGQUERY_CONFIG_FILE="${BIGQUERY_CONFIG_FILE:-$REPRO_OUT/.bigquery-config.json}"
  if [[ -f "$BIGQUERY_CONFIG_FILE.fetched" ]]; then
    rm -f "$BIGQUERY_CONFIG_FILE" "$BIGQUERY_CONFIG_FILE.fetched"
  fi
  if [[ -f "$REPRO_OUT/.bigquery-sa.json.fetched" ]]; then
    rm -f "$REPRO_OUT/.bigquery-sa.json" "$REPRO_OUT/.bigquery-sa.json.fetched"
  fi
  rm -rf "$REPRO_OUT/.gcloud"
}
trap cleanup_credentials EXIT

# shellcheck source=./bq-auth.sh
source "$SCRIPT_DIR/bq-auth.sh"
query="SELECT schema_name FROM \`$BIGQUERY_PROJECT\`.\`region-$REGION\`.INFORMATION_SCHEMA.SCHEMATA WHERE STARTS_WITH(schema_name, 'PROVEFIX_') AND creation_time < TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL $OLDER_THAN_HOURS HOUR)"
result="$(bq_cmd query \
  --use_legacy_sql=false \
  --location="$BIGQUERY_LOCATION" \
  --format=csv \
  --quiet \
  "$query")"
mapfile -t candidates < <(printf '%s\n' "$result" | tail -n +2)

if [[ ${#candidates[@]} -eq 0 || ( ${#candidates[@]} -eq 1 && -z "${candidates[0]}" ) ]]; then
  echo "[sweep-orphans] no orphan datasets older than ${OLDER_THAN_HOURS} hours" >&2
  exit 0
fi

for dataset in "${candidates[@]}"; do
  [[ -n "$dataset" ]] || continue
  if [[ ! "$dataset" =~ ^PROVEFIX_[A-Za-z0-9_]+$ ]]; then
    echo "[sweep-orphans] refusing unexpected dataset name: $dataset" >&2
    exit 1
  fi
  if [[ "$DRY_RUN" == true ]]; then
    echo "[sweep-orphans] candidate: $BIGQUERY_PROJECT:$dataset"
  else
    if [[ ! "$dataset" =~ ^PROVEFIX_ ]]; then
      echo "[sweep-orphans] refusing deletion outside PROVEFIX_: $dataset" >&2
      exit 1
    fi
    echo "[sweep-orphans] deleting $BIGQUERY_PROJECT:$dataset" >&2
    bigquery_drop_dataset "$dataset"
    bigquery_verify_dataset_absent "$dataset"
  fi
done
