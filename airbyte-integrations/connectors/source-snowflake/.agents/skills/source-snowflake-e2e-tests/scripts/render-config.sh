#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "usage: $(basename "$0") <template.json> <output.json>" >&2
  exit 2
fi
TEMPLATE="$1"
OUTPUT="$2"
if [[ ! -f "$TEMPLATE" ]]; then
  echo "[render-config] template not found: $TEMPLATE" >&2
  exit 2
fi

umask 077
mkdir -p "$(dirname "$OUTPUT")"
jq -s --arg s "$PROVEFIX_SCHEMA" '.[0] * .[1] | .schema = $s' \
  "$SNOWFLAKE_CONFIG_FILE" "$TEMPLATE" > "$OUTPUT"
echo "[render-config] rendered config for schema $PROVEFIX_SCHEMA" >&2
