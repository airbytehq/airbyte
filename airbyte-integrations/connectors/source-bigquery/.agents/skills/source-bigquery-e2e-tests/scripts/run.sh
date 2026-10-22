#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(git -C "$SKILL_DIR" rev-parse --show-toplevel)"

export CONNECTOR=source-bigquery
export BACKEND_MODE=remote
export ENGINE_SCRIPTS_DIR="$SKILL_DIR/scripts"
export DEFAULT_CONFIG_TEMPLATE="$SKILL_DIR/fixtures/configs/base.template.json"
export DEFAULT_FIXTURE="$SKILL_DIR/fixtures/sql/00-smoke-table-and-view.sql"
export REPRO_OUT="${REPRO_OUT:-/tmp/source-bigquery-repro}"
export PROVEFIX_RUN_ID="${PROVEFIX_RUN_ID:-$(date +%Y%m%d%H%M%S)_$(hostname | cksum | cut -c1-6)_$$}"
export PROVEFIX_DATASET="PROVEFIX_${PROVEFIX_RUN_ID}"
export GSM_PROJECT="${GSM_PROJECT:-dataline-integration-testing}"
export BIGQUERY_PROJECT="${BIGQUERY_PROJECT:-dataline-integration-testing}"
export BIGQUERY_LOCATION="${BIGQUERY_LOCATION:-US}"
export BIGQUERY_SECRET_NAME="${BIGQUERY_SECRET_NAME:-SECRET_SOURCE-BIGQUERY_CREDENTIALS__CREDS}"
export BIGQUERY_CONFIG_FILE="${BIGQUERY_CONFIG_FILE:-$REPRO_OUT/.bigquery-config.json}"
BIGQUERY_AIRBYTE_EDITION="${BIGQUERY_AIRBYTE_EDITION-CLOUD}"

if [[ -z "${AIRBYTE_OPS:-}" ]]; then
  if command -v airbyte-ops >/dev/null 2>&1; then
    AIRBYTE_OPS=airbyte-ops
  else
    AIRBYTE_OPS="uvx airbyte-internal-ops"
  fi
fi
export AIRBYTE_OPS

args=("$@")
if [[ -n "$BIGQUERY_AIRBYTE_EDITION" ]]; then
  # shellcheck disable=SC2086
  if help_output="$($AIRBYTE_OPS cloud connector regression-test --help 2>&1)" \
    && grep -q -- '--extra-env' <<< "$help_output"; then
    has_separator=false
    for arg in "${args[@]}"; do
      if [[ "$arg" == "--" ]]; then
        has_separator=true
        break
      fi
    done
    if [[ "$has_separator" == true ]]; then
      args+=("--extra-env" "AIRBYTE_EDITION=$BIGQUERY_AIRBYTE_EDITION")
    else
      args+=("--" "--extra-env" "AIRBYTE_EDITION=$BIGQUERY_AIRBYTE_EDITION")
    fi
  else
    echo "[source-bigquery] airbyte-ops lacks --extra-env (airbytehq/airbyte-ops-mcp#349); this run uses only the query API path, not the Storage Read API that Cloud uses." >&2
  fi
fi

exec "$REPO_ROOT/airbyte-integrations/db-harness-lib/scripts/run.sh" "${args[@]}"
