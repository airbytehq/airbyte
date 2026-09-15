#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OLDER_THAN_HOURS=2
DRY_RUN=false
for arg in "$@"; do
  case "$arg" in
    --older-than-hours=*) OLDER_THAN_HOURS="${arg#*=}" ;;
    --dry-run) DRY_RUN=true ;;
    *) echo "usage: $(basename "$0") [--older-than-hours=N] [--dry-run]" >&2; exit 2 ;;
  esac
done

temporary_config=false
if [[ ! -f "$SNOWFLAKE_CONFIG_FILE" ]]; then
  "$SCRIPT_DIR/fetch-config.sh"
  temporary_config=true
fi
trap 'if [[ "$temporary_config" == true ]]; then rm -f "$SNOWFLAKE_CONFIG_FILE"; fi' EXIT

mapfile -t schemas < <("$SCRIPT_DIR/sf.py" list-schemas \
  --like 'PROVEFIX_%' --older-than-hours "$OLDER_THAN_HOURS")
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
