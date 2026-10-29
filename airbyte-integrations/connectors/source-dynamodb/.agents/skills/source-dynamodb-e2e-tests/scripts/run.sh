#!/usr/bin/env bash
# DynamoDB engine shim; orchestration lives in db-harness-lib.
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(git -C "$SKILL_DIR" rev-parse --show-toplevel)"
export CONNECTOR=source-dynamodb
export ENGINE_SCRIPTS_DIR="$SKILL_DIR/scripts"
export DEFAULT_CONFIG_TEMPLATE="$SKILL_DIR/fixtures/configs/base.template.json"
export DEFAULT_FIXTURE="$SKILL_DIR/fixtures/json/00-init-base.json"
export BACKEND_NAME="${BACKEND_NAME:-source-dynamodb-db-backend}"
export CONFIG_HOST_JQ="${CONFIG_HOST_JQ:-.endpoint = (\"http://\" + \$h + \":8000\")}"

exec "$REPO_ROOT/airbyte-integrations/db-harness-lib/scripts/run.sh" "$@"
