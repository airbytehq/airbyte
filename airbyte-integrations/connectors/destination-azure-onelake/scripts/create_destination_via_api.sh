#!/usr/bin/env bash
# Create the Microsoft OneLake destination via Airbyte API (workaround when
# "Set up destination" button does nothing in the UI due to oneOf/format spec).
#
# Usage:
#   1. Get your workspace ID: open Airbyte UI, go to Settings → Account or
#      use: curl -s -H "Authorization: Bearer $AIRBYTE_API_TOKEN" \
#        http://localhost:8000/api/v1/workspaces/list | jq '.workspaces[0].workspaceId'
#   2. Export AIRBYTE_API_TOKEN if your Airbyte uses token auth (Cloud or OSS).
#      For local OSS without auth, you may need to disable auth or use a local token.
#   3. Edit CONFIG_JSON path and WORKSPACE_ID below, then run this script.
#
# OSS default base URL (no auth): http://localhost:8000/api/v1
# Cloud: https://api.airbyte.com/v1  (requires Bearer token)

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_JSON="${1:-$SCRIPT_DIR/../sample_secrets/config.json}"
BASE_URL="${AIRBYTE_BASE_URL:-http://localhost:8000/api/v1}"
WORKSPACE_ID="${AIRBYTE_WORKSPACE_ID:-}"

if [[ -z "$WORKSPACE_ID" ]]; then
  echo "Set AIRBYTE_WORKSPACE_ID (and optionally AIRBYTE_BASE_URL and AIRBYTE_API_TOKEN)."
  echo "Example: export AIRBYTE_WORKSPACE_ID=\$(curl -s \"$BASE_URL/workspaces/list\" | jq -r '.workspaces[0].workspaceId')"
  exit 1
fi

if [[ ! -f "$CONFIG_JSON" ]]; then
  echo "Config not found: $CONFIG_JSON"
  exit 1
fi

# Microsoft OneLake connector definition ID (from metadata.yaml)
DEST_DEFINITION_ID="${AIRBYTE_DESTINATION_DEFINITION_ID:-0916f160-fc17-4cdc-a4aa-c6bcee3c63b2}"

# Build request body
BODY=$(jq -n \
  --arg name "Microsoft OneLake (API)" \
  --arg workspaceId "$WORKSPACE_ID" \
  --arg destinationDefinitionId "$DEST_DEFINITION_ID" \
  --slurpfile conn "$CONFIG_JSON" \
  '{name: $name, workspaceId: $workspaceId, destinationDefinitionId: $destinationDefinitionId, connectionConfiguration: ($conn[0])}')

echo "Creating destination at $BASE_URL/destinations ..."
if [[ -n "$AIRBYTE_API_TOKEN" ]]; then
  RESP=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/destinations" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $AIRBYTE_API_TOKEN" \
    -d "$BODY")
else
  RESP=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/destinations" \
    -H "Content-Type: application/json" \
    -d "$BODY")
fi

HTTP_BODY=$(echo "$RESP" | head -n -1)
HTTP_CODE=$(echo "$RESP" | tail -n 1)

if [[ "$HTTP_CODE" -ge 200 && "$HTTP_CODE" -lt 300 ]]; then
  echo "Destination created successfully."
  echo "$HTTP_BODY" | jq '.'
else
  echo "Request failed with HTTP $HTTP_CODE"
  echo "$HTTP_BODY" | jq '.' 2>/dev/null || echo "$HTTP_BODY"
  exit 1
fi
