#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export REPRO_OUT="${REPRO_OUT:-/tmp/source-snowflake-repro}"
export GSM_PROJECT="${GSM_PROJECT:-dataline-integration-testing}"
export SNOWFLAKE_SECRET_NAME="${SNOWFLAKE_SECRET_NAME:-SECRET_SOURCE-SNOWFLAKE_KEY_PAIR__CREDS}"
export SNOWFLAKE_CONFIG_FILE="${SNOWFLAKE_CONFIG_FILE:-$REPRO_OUT/.snowflake-config.json}"
OLDER_THAN_HOURS=4
DRY_RUN=false
for arg in "$@"; do
  case "$arg" in
    --older-than-hours=*) OLDER_THAN_HOURS="${arg#*=}" ;;
    --dry-run) DRY_RUN=true ;;
    *) echo "usage: $(basename "$0") [--older-than-hours=N] [--dry-run]" >&2; exit 2 ;;
  esac
done

if [[ ! "$OLDER_THAN_HOURS" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
  echo "older-than-hours must be a non-negative number" >&2
  exit 2
fi

temporary_config=false
if [[ ! -f "$SNOWFLAKE_CONFIG_FILE" ]]; then
  "$SCRIPT_DIR/fetch-config.sh"
  temporary_config=true
fi
trap 'if [[ "$temporary_config" == true ]]; then rm -f "$SNOWFLAKE_CONFIG_FILE" "$SNOWFLAKE_CONFIG_FILE.fetched"; fi' EXIT

if ! listing=$("$SCRIPT_DIR/sf.py" list-schemas \
  --like 'PROVEFIX_%' --older-than-hours "$OLDER_THAN_HOURS"); then
  echo "[sweep-orphans] listing failed" >&2
  exit 1
fi
mapfile -t schemas <<< "$listing"
count=0
for schema in "${schemas[@]}"; do
  [[ -n "$schema" ]] || continue
  count=$((count + 1))
  if [[ "$DRY_RUN" == true ]]; then
    echo "$schema"
  else
    "$SCRIPT_DIR/sf.py" drop-schema "$schema"
  fi
done
if [[ "$DRY_RUN" == true ]]; then
  echo "[sweep-orphans] would remove $count schema(s)" >&2
else
  echo "[sweep-orphans] removed $count schema(s)" >&2
fi
