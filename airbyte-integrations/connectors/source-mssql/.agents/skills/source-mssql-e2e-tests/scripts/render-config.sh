#!/usr/bin/env bash
# Substitute the e2e backend's bridge IP into a config template.
#
# Usage:  render-config.sh <template.json> <output.json>
#
# The connector container launched by `airbyte-ops` is on the default
# `bridge` network and cannot resolve a user-defined network's container
# names. Until airbytehq/airbyte-ops-mcp#765 lands `--network` support,
# we render a working config that pins .host to the bridge IP that
# Docker assigned to the backend container at runtime.
#
# Env:
#   BACKEND_NAME            container name (default: source-mssql-db-backend)
set -euo pipefail

BACKEND_NAME="${BACKEND_NAME:-source-mssql-db-backend}"

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

BACKEND_IP=$(docker inspect "$BACKEND_NAME" \
  --format '{{.NetworkSettings.Networks.bridge.IPAddress}}')
if [[ -z "$BACKEND_IP" ]]; then
  echo "[render-config] could not resolve bridge IP for $BACKEND_NAME." >&2
  echo "[render-config] is the container running on the default bridge network?" >&2
  exit 1
fi

mkdir -p "$(dirname "$OUTPUT")"
jq --arg h "$BACKEND_IP" '.host = $h' "$TEMPLATE" > "$OUTPUT"
echo "[render-config] $TEMPLATE → $OUTPUT (host=$BACKEND_IP)" >&2
