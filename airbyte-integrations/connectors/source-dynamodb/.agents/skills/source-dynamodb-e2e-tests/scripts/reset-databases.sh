#!/usr/bin/env bash
# Delete every table on the source-dynamodb e2e backend.
# Used by run.sh --reset=fixture before a second comparison sweep.
#
# Env:
#   BACKEND_NAME   container name (default: source-dynamodb-db-backend)
#   AWS_CLI_IMAGE  AWS CLI image (default: amazon/aws-cli:2.38.2)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/aws-cli.sh"

echo "[reset-databases] deleting every table on $BACKEND_NAME" >&2
while IFS= read -r table_name; do
  [[ -n "$table_name" ]] || continue
  echo "[reset-databases] deleting $table_name" >&2
  ddb_aws delete-table --table-name "$table_name" >/dev/null
  ddb_aws wait table-not-exists --table-name "$table_name"
done < <(ddb_aws list-tables --output json | jq -r '.TableNames[]?')
