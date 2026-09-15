#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SF="$SCRIPT_DIR/sf.py"
MARKER="$REPRO_OUT/.provefix-owned-$PROVEFIX_SCHEMA"
"$SCRIPT_DIR/fetch-config.sh"

if [[ "$("$SF" schema-exists "$PROVEFIX_SCHEMA")" == true ]]; then
  if [[ -f "$MARKER" ]]; then
    echo "[start-backend] reusing schema $PROVEFIX_SCHEMA from a previous phase" >&2
    exit 0
  fi
  echo "[start-backend] $PROVEFIX_SCHEMA already exists — leaked state from a previous run; refusing to run (sweep with scripts/sweep-orphans.sh)" >&2
  exit 1
fi
"$SF" create-schema "$PROVEFIX_SCHEMA"
umask 077
mkdir -p "$REPRO_OUT"
: > "$MARKER"
chmod 600 "$MARKER"
