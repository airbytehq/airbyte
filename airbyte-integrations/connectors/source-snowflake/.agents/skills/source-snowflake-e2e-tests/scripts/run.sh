#!/usr/bin/env bash
# Snowflake engine shim; orchestration lives in db-harness-lib.
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(git -C "$SKILL_DIR" rev-parse --show-toplevel)"
export CONNECTOR=source-snowflake
export BACKEND_MODE=remote
export ENGINE_SCRIPTS_DIR="$SKILL_DIR/scripts"
export DEFAULT_CONFIG_TEMPLATE="$SKILL_DIR/fixtures/configs/utc-session.template.json"
export DEFAULT_FIXTURE="$SKILL_DIR/fixtures/sql/00-cursor-canary-base.sql"
export REPRO_OUT="${REPRO_OUT:-/tmp/source-snowflake-repro}"
export PROVEFIX_RUN_ID="${PROVEFIX_RUN_ID:-$(date +%Y%m%d%H%M%S)_$$}"
export PROVEFIX_SCHEMA="PROVEFIX_${PROVEFIX_RUN_ID}"
export GSM_PROJECT="${GSM_PROJECT:-dataline-integration-testing}"
export SNOWFLAKE_SECRET_NAME="${SNOWFLAKE_SECRET_NAME:-SECRET_SOURCE-SNOWFLAKE_KEY_PAIR__CREDS}"
export SNOWFLAKE_CONFIG_FILE="${SNOWFLAKE_CONFIG_FILE:-$REPRO_OUT/.snowflake-config.json}"

exec "$REPO_ROOT/airbyte-integrations/db-harness-lib/scripts/run.sh" "$@"
