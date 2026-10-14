#!/usr/bin/env bash
# MongoDB engine shim; orchestration lives in db-harness-lib.
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(git -C "$SKILL_DIR" rev-parse --show-toplevel)"
export CONNECTOR=source-mongodb-v2
export ENGINE_SCRIPTS_DIR="$SKILL_DIR/scripts"
export DEFAULT_CONFIG_TEMPLATE="$SKILL_DIR/fixtures/configs/base.template.json"
export DEFAULT_FIXTURE="$SKILL_DIR/fixtures/js/00-init-base.js"
export BACKEND_NAME="${BACKEND_NAME:-source-mongodb-v2-db-backend}"
export BACKEND_REPLSET="${BACKEND_REPLSET:-rs0}"
# The connector takes a connection string rather than host/port fields.
export CONFIG_HOST_JQ="${CONFIG_HOST_JQ:-.database_config.connection_string = (\"mongodb://\" + \$h + \":27017/?replicaSet=$BACKEND_REPLSET\")}"

exec "$REPO_ROOT/airbyte-integrations/db-harness-lib/scripts/run.sh" "$@"
