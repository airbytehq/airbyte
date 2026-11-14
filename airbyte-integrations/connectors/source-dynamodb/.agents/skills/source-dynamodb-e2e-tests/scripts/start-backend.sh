#!/usr/bin/env bash
# Start a throwaway DynamoDB Local backend for source-dynamodb e2e tests.
# Idempotent: succeeds whether or not the container already exists.
#
# Env:
#   BACKEND_NAME   container name (default: source-dynamodb-db-backend)
#   BACKEND_PORT   host port mapped to 8000/tcp (default: 8000)
#   BACKEND_IMAGE  image (default: amazon/dynamodb-local:3.3.2)
#   AWS_CLI_IMAGE  image used for readiness probes (default: amazon/aws-cli:2.38.2)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_NAME="${BACKEND_NAME:-source-dynamodb-db-backend}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
BACKEND_IMAGE="${BACKEND_IMAGE:-amazon/dynamodb-local:3.3.2}"
export BACKEND_NAME
# shellcheck disable=SC1091
source "$SCRIPT_DIR/aws-cli.sh"

if [[ "$(docker inspect -f '{{.State.Running}}' "$BACKEND_NAME" 2>/dev/null || echo false)" == "true" ]]; then
  echo "[start-backend] $BACKEND_NAME already running; reusing." >&2
else
  docker rm -f "$BACKEND_NAME" >/dev/null 2>&1 || true
  docker run -d --rm \
    --name "$BACKEND_NAME" \
    -p "$BACKEND_PORT:8000" \
    "$BACKEND_IMAGE" \
    -jar DynamoDBLocal.jar \
    -inMemory \
    -sharedDb >/dev/null
fi

echo "[start-backend] waiting for $BACKEND_NAME to accept requests…" >&2
ready=false
for _ in $(seq 1 60); do
  if ddb_aws list-tables --output json >/dev/null 2>&1; then
    ready=true
    break
  fi
  sleep 2
done
if [[ "$ready" != true ]]; then
  echo "[start-backend] timed out waiting for $BACKEND_NAME after 120s." >&2
  exit 1
fi

echo "[start-backend] $BACKEND_NAME ready." >&2
