#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export REPRO_OUT="${REPRO_OUT:-/tmp/source-snowflake-repro}"
export PROVEFIX_RUN_ID="${PROVEFIX_RUN_ID:-$(date +%Y%m%d%H%M%S)_$$}"
export PROVEFIX_SCHEMA="PROVEFIX_${PROVEFIX_RUN_ID}"
TARGET="${1:-1.1.1}"
CONTROL="${2:-1.1.0}"
BASE_FIXTURE="$SKILL_DIR/fixtures/sql/00-cursor-canary-base.sql"
BOUNDARY_FIXTURE="$SKILL_DIR/fixtures/sql/01-cursor-canary-boundary-row.sql"
EXTRACT_STATE="$SKILL_DIR/../../../../../db-harness-lib/scripts/extract-state.py"
CANARY_CONFIG_TEMPLATE="${CANARY_CONFIG_TEMPLATE:-$SKILL_DIR/fixtures/configs/base.template.json}"

if "$SKILL_DIR/scripts/run.sh" \
  --command=read \
  --test-version="$CONTROL" \
  --sync-mode=incremental \
  --cursor-field=UPDATED_AT \
  --streams=CURSOR_CANARY \
  --config-template="$CANARY_CONFIG_TEMPLATE" \
  --min-records=2 \
  --keep-backend \
  --step-name=canary-initial; then
  :
else
  rc=$?
  echo "[cursor-upper-bound] initial harness failed with exit $rc" >&2
  if [[ -f "$REPRO_OUT/canary-initial/read/stderr.txt" ]]; then
    tail -40 "$REPRO_OUT/canary-initial/read/stderr.txt" >&2
  fi
  exit "$rc"
fi

python3 "$EXTRACT_STATE" "$REPRO_OUT/canary-initial/read/stdout.txt" \
  > "$REPRO_OUT/canary-state.json"

if "$SKILL_DIR/scripts/run.sh" \
  --command=read \
  --test-version="$TARGET" \
  --control-version="$CONTROL" \
  --reset=fixture \
  --fixture="$BASE_FIXTURE" \
  --fixture="$BOUNDARY_FIXTURE" \
  --state="$REPRO_OUT/canary-state.json" \
  --sync-mode=incremental \
  --cursor-field=UPDATED_AT \
  --streams=CURSOR_CANARY \
  --config-template="$CANARY_CONFIG_TEMPLATE" \
  --step-name=canary-incremental \
  --expect-match='stdout:"NAME":\s*"boundary"'; then
  :
else
  rc=$?
  echo "[cursor-upper-bound] incremental harness failed with exit $rc" >&2
  exit "$rc"
fi

count_boundary() {
  local output="$1"
  [[ -f "$output" ]] || { echo 0; return; }
  grep -cE '"NAME":\s*"boundary"' "$output" 2>/dev/null || true
}

control_boundary="$(count_boundary "$REPRO_OUT/canary-incremental/control/read/stdout.txt")"
target_boundary="$(count_boundary "$REPRO_OUT/canary-incremental/target/read/stdout.txt")"
if [[ "$control_boundary" != 0 ]]; then
  echo "[cursor-upper-bound] control emitted boundary row: $control_boundary" >&2
  echo "[cursor-upper-bound] initial control STATE lines:" >&2
  grep -E '"type"[[:space:]]*:[[:space:]]*"STATE"' \
    "$REPRO_OUT/canary-initial/read/stdout.txt" >&2 || true
  echo "[cursor-upper-bound] extracted state:" >&2
  cat "$REPRO_OUT/canary-state.json" >&2
  echo "[cursor-upper-bound] control incremental logs:" >&2
  grep -iE 'initial|incremental|state' \
    "$REPRO_OUT/canary-incremental/control/read/stderr.txt" >&2 || true
  exit 1
fi
if [[ "$target_boundary" -lt 1 ]]; then
  echo "[cursor-upper-bound] target did not emit boundary row" >&2
  exit 1
fi

VERIFY_CONFIG="$REPRO_OUT/.verify-config-$$.json"
trap 'rm -f "$VERIFY_CONFIG"' EXIT
SNOWFLAKE_CONFIG_FILE="$VERIFY_CONFIG" \
  REPRO_OUT="$REPRO_OUT" \
  "$SKILL_DIR/scripts/fetch-config.sh"
if [[ "$(SNOWFLAKE_CONFIG_FILE="$VERIFY_CONFIG" "$SKILL_DIR/scripts/sf.py" schema-exists "$PROVEFIX_SCHEMA")" != false ]]; then
  echo "[cursor-upper-bound] $PROVEFIX_SCHEMA still exists after harness teardown" >&2
  exit 1
fi

printf 'control boundary rows: %s\ntarget boundary rows: %s\nschema absent: true\n' \
  "$control_boundary" "$target_boundary"
