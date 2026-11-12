#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SKILL="$(cd "$HERE/.." && pwd)"
GENERIC="$(cd "$SKILL/../source-mysql-e2e-tests" && pwd)"
REPO_ROOT="$(git -C "$HERE" rev-parse --show-toplevel)"
LIB="$REPO_ROOT/airbyte-integrations/db-harness-lib"

REPRO_OUT="${REPRO_OUT:-/tmp/source-mysql-repro}"
VERSION="${VERSION:-3.53.4}"
STEP_NAME="${STEP_NAME:-cdc-replay}"
BASELINE_STATE="$REPRO_OUT/$STEP_NAME/state.json"
export REPRO_OUT

"$GENERIC/scripts/run.sh" \
  --command=read \
  --test-version="$VERSION" \
  --step-name="$STEP_NAME/baseline" \
  --fixture="$SKILL/fixtures/sql/00-init-cdc.sql" \
  --config-template="$SKILL/fixtures/configs/cdc.template.json" \
  --catalog="$SKILL/fixtures/catalogs/users-cdc.json" \
  --keep-backend \
  --expect-test=pass \
  --min-records=3 \
  --min-states=1

mkdir -p "$(dirname "$BASELINE_STATE")"
"$LIB/scripts/extract-state.py" \
  "$REPRO_OUT/$STEP_NAME/baseline/read/stdout.txt" \
  > "$BASELINE_STATE"
"$GENERIC/scripts/apply-sql.sh" \
  "$SKILL/fixtures/sql/mutate-insert-users.sql"

"$GENERIC/scripts/run.sh" \
  --command=read \
  --test-version="$VERSION" \
  --step-name="$STEP_NAME/replay" \
  --skip-fixtures \
  --config-template="$SKILL/fixtures/configs/cdc.template.json" \
  --catalog="$SKILL/fixtures/catalogs/users-cdc.json" \
  --state="$BASELINE_STATE" \
  --keep-backend \
  --expect-test=pass \
  --expect-match='stdout:dave@example\.com' \
  --forbid-match='stdout:alice@example\.com'
