#!/usr/bin/env bash
set -euo pipefail

: "${REPRO_OUT:?REPRO_OUT must be set}"
: "${PROVEFIX_DATASET:?PROVEFIX_DATASET must be set}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OWNED_MARKER="$REPRO_OUT/.provefix-owned-$PROVEFIX_DATASET"

# shellcheck source=./bq-auth.sh
source "$SCRIPT_DIR/bq-auth.sh"

if bigquery_dataset_exists "$PROVEFIX_DATASET"; then
  if [[ -f "$OWNED_MARKER" ]]; then
    echo "[start-backend] reusing owned dataset $BIGQUERY_PROJECT:$PROVEFIX_DATASET" >&2
    exit 0
  fi
  echo "[start-backend] refusing unowned dataset $BIGQUERY_PROJECT:$PROVEFIX_DATASET; inspect with $SCRIPT_DIR/sweep-orphans.sh --dry-run" >&2
  exit 1
fi

bigquery_create_dataset "$PROVEFIX_DATASET"
temporary_marker="$(mktemp "$REPRO_OUT/.provefix-owned.XXXXXX")"
printf '%s\n' "$PROVEFIX_DATASET" > "$temporary_marker"
chmod 600 "$temporary_marker"
mv "$temporary_marker" "$OWNED_MARKER"
echo "[start-backend] created owned dataset $BIGQUERY_PROJECT:$PROVEFIX_DATASET" >&2
