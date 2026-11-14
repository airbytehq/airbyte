#!/usr/bin/env bash
# airbytehq/oncall#11451 — source-mssql 4.3.4+ rejects a saved offset
# whose commit_lsn is older than the per-instance min LSN, even when
# the data is still present in the change table at read time.
#
# Multi-phase: baseline read (captures STATE) → advance min_lsn past
# the saved offset via sp_cdc_cleanup_change_table → replay read with
# stale STATE, expect the rejection.
#
# Migrated from scripts/repro-11451.sh: the inline extract-state hop
# and grep-on-stderr assertions collapse to the generic skill's
# `extract-state.py` + `run.sh --state=… --expect-match=stderr:…` per
# phase. `--step-name=11451/{baseline,stale}` gives each phase its own
# artifact subtree so the caller can inspect either read separately.
#
# Env:
#   BASELINE_VERSION    source-mssql tag for state capture (default: 4.4.2).
#                       Any version works; this is the connector that
#                       writes the STATE we later replay.
#   TARGET_VERSION      source-mssql tag to reproduce the regression on
#                       (default: 4.3.4 — the first version with the
#                       new per-instance LSN-range check). Try 4.4.2 /
#                       4.4.3 / latest to confirm the bug persists.
#   REPRO_OUT           output parent dir (default: /tmp/source-mssql-repro)
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SKILL="$(cd "$HERE/.." && pwd)"
GENERIC="$(cd "$SKILL/../source-mssql-e2e-tests" && pwd)"
REPO_ROOT="$(git -C "$HERE" rev-parse --show-toplevel)"
LIB="$REPO_ROOT/airbyte-integrations/db-harness-lib"

REPRO_OUT="${REPRO_OUT:-/tmp/source-mssql-repro}"
BASELINE_VERSION="${BASELINE_VERSION:-4.4.2}"
TARGET_VERSION="${TARGET_VERSION:-4.3.4}"
STEP_NAME="${STEP_NAME:-11451}"
export REPRO_OUT

BASELINE_STATE="$REPRO_OUT/$STEP_NAME/state.json"

# Phase 1: baseline read on clean CdcTest, capture STATE.
"$GENERIC/scripts/run.sh" \
  --command=read \
  --test-version="$BASELINE_VERSION" \
  --step-name="$STEP_NAME/baseline" \
  --fixture="$SKILL/fixtures/sql/00-init-cdc.sql" \
  --config-template="$SKILL/fixtures/configs/cdc.template.json" \
  --catalog="$SKILL/fixtures/catalogs/users-cdc.json" \
  --keep-backend \
  --expect-test=pass \
  --min-states=1

# Phase 2: pull STATE from baseline, advance min_lsn past the saved LSN.
mkdir -p "$(dirname "$BASELINE_STATE")"
"$LIB/scripts/extract-state.py" \
  "$REPRO_OUT/$STEP_NAME/baseline/read/stdout.txt" \
  > "$BASELINE_STATE"
"$GENERIC/scripts/apply-sql.sh" \
  "$SKILL/fixtures/sql/repro-11451-lsn-cleanup.sql"

# Phase 3: replay read with stale STATE against TARGET_VERSION, expect
# the offset-rejection error. --skip-fixtures preserves the CDC state
# Phase 2 established — re-applying 00-init-cdc.sql here would drop
# and recreate CdcTest and wipe out the min_lsn advancement we just
# made, defeating the repro.
"$GENERIC/scripts/run.sh" \
  --command=read \
  --test-version="$TARGET_VERSION" \
  --step-name="$STEP_NAME/stale" \
  --skip-fixtures \
  --config-template="$SKILL/fixtures/configs/cdc.template.json" \
  --catalog="$SKILL/fixtures/catalogs/users-cdc.json" \
  --state="$BASELINE_STATE" \
  --keep-backend \
  --expect-test=fail \
  --expect-match='stderr:Saved offset no longer present' \
  --expect-match='stderr:is no longer available in SQL Server transaction logs'
