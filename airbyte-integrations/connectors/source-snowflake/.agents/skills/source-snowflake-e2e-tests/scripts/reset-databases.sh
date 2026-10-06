#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SF="$SCRIPT_DIR/sf.py"
"$SCRIPT_DIR/fetch-config.sh"
"$SF" drop-schema "$PROVEFIX_SCHEMA"
if [[ "$("$SF" schema-exists "$PROVEFIX_SCHEMA")" == true ]]; then
  echo "[reset-databases] $PROVEFIX_SCHEMA still exists after drop" >&2
  exit 1
fi
"$SF" create-schema "$PROVEFIX_SCHEMA"
umask 077
mkdir -p "$REPRO_OUT"
: > "$REPRO_OUT/.provefix-owned-$PROVEFIX_SCHEMA"
chmod 600 "$REPRO_OUT/.provefix-owned-$PROVEFIX_SCHEMA"
