#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MARKER="$REPRO_OUT/.provefix-owned-$PROVEFIX_SCHEMA"
if [[ -f "$SNOWFLAKE_CONFIG_FILE" ]]; then
  "$SCRIPT_DIR/sf.py" drop-schema "$PROVEFIX_SCHEMA" || true
  echo "[stop-backend] dropped $PROVEFIX_SCHEMA" >&2
else
  echo "[stop-backend] config missing; skipped dropping $PROVEFIX_SCHEMA" >&2
fi
rm -f "$MARKER"
rm -f "$SNOWFLAKE_CONFIG_FILE"
