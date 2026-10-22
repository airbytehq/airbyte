#!/usr/bin/env bash
# airbytehq/oncall#13714 — CDC deserialization fails for temporal columns
# whose SQL Server types are user-defined aliases.
#
# A baseline read establishes CDC state; subsequent UPDATE/INSERT events
# exercise Debezium's value conversion rather than only the JDBC snapshot.
#
# Env:
#   VERSION       source-mssql tag (default: 5.1.1)
#   EXPECT        fail for the published regression; pass after the fix
#   REPRO_OUT     output parent dir (default: /tmp/source-mssql-repro)
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SKILL="$(cd "$HERE/.." && pwd)"
GENERIC="$(cd "$SKILL/../source-mssql-e2e-tests" && pwd)"
REPO_ROOT="$(git -C "$HERE" rev-parse --show-toplevel)"
LIB="$REPO_ROOT/airbyte-integrations/db-harness-lib"

REPRO_OUT="${REPRO_OUT:-/tmp/source-mssql-repro}"
STEP_NAME="${STEP_NAME:-13714}"
EXPECT="${EXPECT:-fail}"
BASELINE_STATE="$REPRO_OUT/$STEP_NAME/state.json"
export REPRO_OUT

"$GENERIC/scripts/run.sh" \
  --command=read \
  --test-version="${VERSION:-5.1.1}" \
  --step-name="$STEP_NAME/baseline" \
  --fixture="$SKILL/fixtures/sql/00-init-cdc.sql" \
  --fixture="$SKILL/fixtures/sql/repro-13714-alias-datetime.sql" \
  --config-template="$SKILL/fixtures/configs/cdc.template.json" \
  --catalog="$SKILL/fixtures/catalogs/ausencia-alias-cdc.json" \
  --keep-backend \
  --expect-test=pass \
  --min-states=1

mkdir -p "$(dirname "$BASELINE_STATE")"
"$LIB/scripts/extract-state.py" \
  "$REPRO_OUT/$STEP_NAME/baseline/read/stdout.txt" \
  > "$BASELINE_STATE"
"$GENERIC/scripts/apply-sql.sh" \
  "$SKILL/fixtures/sql/repro-13714-alias-datetime-changes.sql"

EXPECT_ARGS=(--expect-test="$EXPECT")
if [[ "$EXPECT" == fail ]]; then
  EXPECT_ARGS+=(--expect-match='stderr:invalid textual value')
else
  EXPECT_ARGS+=(--min-records=1)
  EXPECT_ARGS+=(--expect-match='stdout:2026-10-17T00:00:00\.000000')
  EXPECT_ARGS+=(--expect-match='stdout:2026-10-17')
  EXPECT_ARGS+=(--expect-match='stdout:15:00:03\.987654')
  EXPECT_ARGS+=(--expect-match='stdout:2026-10-17T14:56:58\.987654')
fi

"$GENERIC/scripts/run.sh" \
  --command=read \
  --test-version="${VERSION:-5.1.1}" \
  --step-name="$STEP_NAME/changes" \
  --skip-fixtures \
  --config-template="$SKILL/fixtures/configs/cdc.template.json" \
  --catalog="$SKILL/fixtures/catalogs/ausencia-alias-cdc.json" \
  --state="$BASELINE_STATE" \
  --keep-backend \
  "${EXPECT_ARGS[@]}"
