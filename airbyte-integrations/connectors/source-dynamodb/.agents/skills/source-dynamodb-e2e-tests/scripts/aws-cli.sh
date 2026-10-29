#!/usr/bin/env bash
# Helpers for running the AWS CLI against the local DynamoDB backend.
set -euo pipefail

BACKEND_NAME="${BACKEND_NAME:-source-dynamodb-db-backend}"
AWS_CLI_IMAGE="${AWS_CLI_IMAGE:-amazon/aws-cli:2.38.2}"

ddb_backend_ip() {
  local backend_ip
  backend_ip="$(docker inspect "$BACKEND_NAME" \
    --format '{{.NetworkSettings.Networks.bridge.IPAddress}}')"
  if [[ -z "$backend_ip" ]]; then
    echo "[aws-cli] could not resolve bridge IP for $BACKEND_NAME." >&2
    return 1
  fi
  printf '%s\n' "$backend_ip"
}

ddb_aws() {
  local backend_ip
  backend_ip="$(ddb_backend_ip)"
  docker run --rm \
    -e AWS_ACCESS_KEY_ID=dummy \
    -e AWS_SECRET_ACCESS_KEY=dummy \
    -e AWS_DEFAULT_REGION=us-east-1 \
    "$AWS_CLI_IMAGE" \
    --endpoint-url "http://${backend_ip}:8000" \
    dynamodb "$@"
}

ddb_table_exists() {
  local table_name="$1"
  ddb_aws list-tables --output json \
    | jq -e --arg table "$table_name" '.TableNames | index($table) != null' >/dev/null
}
