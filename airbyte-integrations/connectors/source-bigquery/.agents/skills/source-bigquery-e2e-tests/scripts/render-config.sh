#!/usr/bin/env bash
set -euo pipefail
umask 077

if [[ $# -lt 2 ]]; then
  echo "usage: $(basename "$0") <template.json> <output.json>" >&2
  exit 2
fi
: "${REPRO_OUT:?REPRO_OUT must be set}"
: "${BIGQUERY_PROJECT:?BIGQUERY_PROJECT must be set}"
: "${PROVEFIX_DATASET:?PROVEFIX_DATASET must be set}"
TEMPLATE="$1"
OUTPUT="$2"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ ! -f "$TEMPLATE" ]]; then
  echo "[render-config] template not found: $TEMPLATE" >&2
  exit 2
fi

"$SCRIPT_DIR/fetch-config.sh"
mkdir -p "$(dirname "$OUTPUT")"
jq \
  --arg project "$BIGQUERY_PROJECT" \
  --arg dataset "$PROVEFIX_DATASET" \
  --rawfile credentials "$REPRO_OUT/.bigquery-sa.json" \
  '. + {project_id: $project, dataset_id: $dataset, credentials_json: $credentials}' \
  "$TEMPLATE" > "$OUTPUT"
chmod 600 "$OUTPUT"
echo "[render-config] rendered config for dataset $PROVEFIX_DATASET" >&2
