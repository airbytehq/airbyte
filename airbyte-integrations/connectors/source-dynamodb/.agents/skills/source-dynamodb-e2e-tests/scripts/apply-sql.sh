#!/usr/bin/env bash
# Apply a JSON fixture to the e2e DynamoDB backend.
#
# The name follows the db-harness-lib engine contract (apply-sql.sh), but
# DynamoDB fixtures are JSON documents, not SQL.
#
# Usage:  apply-sql.sh <path/to/fixture.json>
#
# Env:
#   BACKEND_NAME   container name (default: source-dynamodb-db-backend)
#   AWS_CLI_IMAGE  AWS CLI image (default: amazon/aws-cli:2.38.2)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/aws-cli.sh"

if [[ $# -lt 1 ]]; then
  echo "usage: $(basename "$0") <path/to/fixture.json>" >&2
  exit 2
fi
FIXTURE="$1"
if [[ ! -f "$FIXTURE" ]]; then
  echo "[apply-sql] not a file: $FIXTURE" >&2
  exit 2
fi
jq -e '.tables | type == "array"' "$FIXTURE" >/dev/null

while IFS= read -r table; do
  table_name="$(jq -r '.create.TableName' <<<"$table")"
  create_json="$(jq -c '.create' <<<"$table")"

  if ddb_table_exists "$table_name"; then
    echo "[apply-sql] deleting existing table $table_name" >&2
    ddb_aws delete-table --table-name "$table_name" >/dev/null
    ddb_aws wait table-not-exists --table-name "$table_name"
  fi

  echo "[apply-sql] creating table $table_name" >&2
  ddb_aws create-table --cli-input-json "$create_json" >/dev/null
  ddb_aws wait table-exists --table-name "$table_name"

  while IFS= read -r item; do
    [[ -n "$item" ]] || continue
    ddb_aws put-item --table-name "$table_name" --item "$item" >/dev/null
  done < <(jq -c '.items[]?' <<<"$table")
done < <(jq -c '.tables[]' "$FIXTURE")

echo "[apply-sql] applied $FIXTURE." >&2
