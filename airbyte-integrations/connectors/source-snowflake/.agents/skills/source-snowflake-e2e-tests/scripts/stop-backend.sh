#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MARKER="$REPRO_OUT/.provefix-owned-$PROVEFIX_SCHEMA"
if [[ -f "$MARKER" ]]; then
  if ! "$SCRIPT_DIR/sf.py" drop-schema "$PROVEFIX_SCHEMA"; then
    echo "[stop-backend] failed to drop $PROVEFIX_SCHEMA" >&2
    exit 1
  fi
  echo "[stop-backend] dropped $PROVEFIX_SCHEMA" >&2
  rm -f "$MARKER"
else
  echo "[stop-backend] no ownership marker for $PROVEFIX_SCHEMA; leaving it for sweep-orphans.sh" >&2
fi
if [[ -f "$SNOWFLAKE_CONFIG_FILE.fetched" ]]; then
  rm -f "$SNOWFLAKE_CONFIG_FILE" "$SNOWFLAKE_CONFIG_FILE.fetched"
fi
