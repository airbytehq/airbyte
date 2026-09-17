#!/usr/bin/env bash
# airbytehq/oncall#13544 — source-mssql loses schema-history DDL records
# Issue: https://github.com/airbytehq/oncall/issues/13544
# when the final Debezium offset is a heartbeat. A subsequent sync then
# emits a newly added column as NULL.
#
# Multi-phase: baseline read → add a column and create a second capture
# instance → advance the CDC upper bound with an excluded CDC-enabled table
# → verify a heartbeat final offset → insert another row and replay with the
# heartbeat state. The side table advances CDC's upper bound without producing
# configured-stream rows. The Debezium heartbeat interval is 10s, so this case
# uses a 60s initial wait instead of the default 5s harness timeout.
#
# Env:
#   VERSION       source-mssql tag (default: dev)
#   EXPECT_BUG    expected behavior, 1 for the unfixed connector and 0
#                 for a fixed connector (default: 0)
#   REPRO_OUT     output parent dir (default: /tmp/source-mssql-repro)
#   STEP_NAME     artifact subtree name (default: 13544)
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SKILL="$(cd "$HERE/.." && pwd)"
GENERIC="$(cd "$SKILL/../source-mssql-e2e-tests" && pwd)"
REPO_ROOT="$(git -C "$HERE" rev-parse --show-toplevel)"
LIB="$REPO_ROOT/airbyte-integrations/db-harness-lib"

REPRO_OUT="${REPRO_OUT:-/tmp/source-mssql-repro}"
VERSION="${VERSION:-dev}"
EXPECT_BUG="${EXPECT_BUG:-0}"
STEP_NAME="${STEP_NAME:-13544}"
BASELINE_STATE="$REPRO_OUT/$STEP_NAME/state1.json"
STATE2="$REPRO_OUT/$STEP_NAME/state2.json"
export REPRO_OUT

if [[ "$EXPECT_BUG" != 0 && "$EXPECT_BUG" != 1 ]]; then
  echo "EXPECT_BUG must be 0 or 1 (got '$EXPECT_BUG')" >&2
  exit 2
fi

"$GENERIC/scripts/run.sh" \
  --command=read \
  --test-version="$VERSION" \
  --step-name="$STEP_NAME/baseline" \
  --fixture="$SKILL/fixtures/sql/00-init-cdc.sql" \
  --config-template="$SKILL/fixtures/configs/cdc-13544.template.json" \
  --catalog="$SKILL/fixtures/catalogs/users-cdc.json" \
  --keep-backend \
  --expect-test=pass \
  --min-states=1

mkdir -p "$(dirname "$BASELINE_STATE")"
"$LIB/scripts/extract-state.py" \
  "$REPRO_OUT/$STEP_NAME/baseline/read/stdout.txt" \
  > "$BASELINE_STATE"

"$GENERIC/scripts/apply-sql.sh" \
  "$SKILL/fixtures/sql/repro-13544-add-column.sql"

run_alter_read() {
  local step_name="$1" state_path="$2" expect_dave="$3"
  local -a args=(
    --command=read
    --test-version="$VERSION"
    --step-name="$step_name"
    --skip-fixtures
    --config-template="$SKILL/fixtures/configs/cdc-13544.template.json"
    --catalog="$SKILL/fixtures/catalogs/users-nickname-cdc.json"
    --state="$state_path"
    --keep-backend
  )
  if [[ "$expect_dave" == 1 ]]; then
    args+=(--min-states=1)
    args+=(--expect-match='stdout:"nickname":"dave"')
  fi
  "$GENERIC/scripts/run.sh" "${args[@]}"
}

extract_state2() {
  local output_path
  output_path="$(mktemp "${STATE2}.XXXXXX")"
  "$LIB/scripts/extract-state.py" \
    "$REPRO_OUT/$STEP_NAME/$1/read/stdout.txt" \
    > "$output_path"
  if [[ ! -s "$output_path" ]] || ! jq empty "$output_path"; then
    rm -f "$output_path"
    return 1
  fi
  mv "$output_path" "$STATE2"
}

offset_json() {
  jq -c '
    [
      .. | objects | .mssql_cdc_offset? // empty
      | if type == "object" and has("change_lsn") then .
        elif type == "object" then .[]?
        else .
        end
      | if type == "string" then try fromjson catch empty else . end
      | select(type == "object" and has("change_lsn"))
    ] | first // null
  ' "$STATE2"
}

run_alter_read "$STEP_NAME/alter" "$BASELINE_STATE" 1
extract_state2 alter

HEARTBEAT_OFFSET="$(offset_json)"
for attempt in 1 2 3; do
  CHANGE_LSN="$(jq -r '.change_lsn // empty' <<<"$HEARTBEAT_OFFSET")"
  if [[ "$CHANGE_LSN" == "NULL" ]]; then
    break
  fi
  echo "[13544] heartbeat precondition not reached after alter attempt $attempt; retrying with state2" >&2
  run_alter_read "$STEP_NAME/alter-retry-$attempt" "$STATE2" 0
  if ! extract_state2 "alter-retry-$attempt"; then
    echo "[13544] alter retry emitted no STATE message; heartbeat final offset not reached" >&2
    break
  fi
  HEARTBEAT_OFFSET="$(offset_json)"
done

CHANGE_LSN="$(jq -r '.change_lsn // empty' <<<"$HEARTBEAT_OFFSET")"
echo "[13544] state2 offset: $HEARTBEAT_OFFSET"
if [[ "$CHANGE_LSN" != "NULL" ]]; then
  echo "[13544] heartbeat final offset not reached (change_lsn='$CHANGE_LSN')" >&2
  exit 2
fi

"$GENERIC/scripts/apply-sql.sh" \
  "$SKILL/fixtures/sql/repro-13544-insert-after-heartbeat.sql"

RESUME_ARGS=(
  --command=read
  --test-version="$VERSION"
  --step-name="$STEP_NAME/resume"
  --skip-fixtures
  --config-template="$SKILL/fixtures/configs/cdc-13544.template.json"
  --catalog="$SKILL/fixtures/catalogs/users-nickname-cdc.json"
  --state="$STATE2"
  --keep-backend
)
if [[ "$EXPECT_BUG" == 1 ]]; then
  RESUME_ARGS+=(
    '--expect-match=stdout:"id":5,"email":"erin@example.com","nickname":null'
    '--forbid-match=stdout:"nickname":"erin"'
  )
else
  RESUME_ARGS+=(
    '--forbid-match=stdout:"id":5,"email":"erin@example.com","nickname":null'
    '--expect-match=stdout:"nickname":"erin"'
  )
fi
"$GENERIC/scripts/run.sh" "${RESUME_ARGS[@]}"
