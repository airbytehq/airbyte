#!/usr/bin/env bash
# airbytehq/airbyte#85286 — a GLOBAL state whose per-stream state is `{}`
# (initial snapshot interrupted before its first checkpoint) is treated
# as a completed snapshot on 5.0.0: the stream gets no partition and the
# retry emits zero records for it, so the destination promotes an
# incomplete table.
#
# The seed rows (alice/bob/carol) are inserted BEFORE CDC is enabled on
# the table, so they are absent from the change table and can only be
# produced by the initial snapshot. A skipped snapshot is then directly
# observable as "seed rows missing from the read".
#
# Multi-phase:
#   1. baseline read (CONTROL_VERSION) on clean CdcTest → capture STATE.
#   2. insert one more row (dave) → 4 rows total; blank the stream_state
#      in the captured STATE to `{}` while keeping the Debezium offset.
#   3. replay `{}` state on CONTROL_VERSION → expect the bug: only the
#      CDC row (dave) is emitted, the seed rows are silently lost.
#   4. replay `{}` state on TARGET_VERSION  → expect a restarted snapshot
#      (all 4 rows incl. alice, ≥1 STATE).
#   5. true-positive analogue: replay the *unmodified* completed state on
#      TARGET_VERSION → must not re-snapshot; only the CDC insert (dave)
#      is emitted, the seed rows are not.
#
# Env:
#   CONTROL_VERSION   known-bad tag (default: 5.0.0)
#   TARGET_VERSION    tag under test (default: dev)
#   REPRO_OUT         output parent dir (default: /tmp/source-mssql-repro)
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SKILL="$(cd "$HERE/.." && pwd)"
GENERIC="$(cd "$SKILL/../source-mssql-e2e-tests" && pwd)"

REPRO_OUT="${REPRO_OUT:-/tmp/source-mssql-repro}"
CONTROL_VERSION="${CONTROL_VERSION:-5.0.0}"
TARGET_VERSION="${TARGET_VERSION:-dev}"
STEP_NAME="${STEP_NAME:-85286}"
export REPRO_OUT

COMPLETED_STATE="$REPRO_OUT/$STEP_NAME/completed-state.json"
EMPTY_STATE="$REPRO_OUT/$STEP_NAME/empty-stream-state.json"

common=(
  --command=read
  --config-template="$SKILL/fixtures/configs/cdc.template.json"
  --catalog="$SKILL/fixtures/catalogs/users-cdc.json"
  --keep-backend
)

# Phase 1: baseline snapshot on the control image, capture STATE.
"$GENERIC/scripts/run.sh" "${common[@]}" \
  --test-version="$CONTROL_VERSION" \
  --step-name="$STEP_NAME/baseline" \
  --fixture="$SKILL/fixtures/sql/repro-85286-init-cdc-preseeded.sql" \
  --expect-test=pass --min-records=3 --min-states=1

# Phase 2: derive both replay states, then add a post-snapshot row.
mkdir -p "$(dirname "$COMPLETED_STATE")"
"$GENERIC/scripts/extract-state.py" \
  "$REPRO_OUT/$STEP_NAME/baseline/read/stdout.txt" > "$COMPLETED_STATE"
"$SKILL/scripts/blank-stream-state.py" "$COMPLETED_STATE" > "$EMPTY_STATE"
"$GENERIC/scripts/apply-sql.sh" \
  "$SKILL/fixtures/sql/repro-85286-insert-after-snapshot.sql"

# Phase 3: `{}` stream state on the control image → bug: stream skipped.
"$GENERIC/scripts/run.sh" "${common[@]}" \
  --test-version="$CONTROL_VERSION" \
  --step-name="$STEP_NAME/empty-control" \
  --skip-fixtures --state="$EMPTY_STATE" \
  --expect-test=pass \
  --expect-match='stdout:dave@example.com' \
  --forbid-match='stdout:alice@example.com'

# Phase 4: `{}` stream state on the target image → snapshot restarts.
"$GENERIC/scripts/run.sh" "${common[@]}" \
  --test-version="$TARGET_VERSION" \
  --step-name="$STEP_NAME/empty-target" \
  --skip-fixtures --state="$EMPTY_STATE" \
  --expect-test=pass --min-records=4 --min-states=1 \
  --expect-match='stdout:alice@example.com' \
  --expect-match='stdout:dave@example.com'

# Phase 5: completed (non-empty) state on the target image → no
# re-snapshot; only the CDC change since the baseline is emitted.
"$GENERIC/scripts/run.sh" "${common[@]}" \
  --test-version="$TARGET_VERSION" \
  --step-name="$STEP_NAME/completed-target" \
  --skip-fixtures --state="$COMPLETED_STATE" \
  --expect-test=pass --min-records=1 --min-states=1 \
  --expect-match='stdout:dave@example.com' \
  --forbid-match='stdout:alice@example.com'
