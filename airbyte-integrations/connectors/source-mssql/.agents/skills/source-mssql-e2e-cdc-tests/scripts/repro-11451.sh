#!/usr/bin/env bash
# Reproduce airbytehq/oncall#11451: source-mssql 4.3.4+ rejects a
# saved offset whose commit_lsn is older than the per-instance min LSN,
# even when the data is still present in the change table at read time.
#
# Symptom: read with the saved state exits non-zero with
#   "Saved offset no longer present on the server, please reset the
#    connection. Saved LSN '...' is no longer available in SQL Server
#    transaction logs."
#
# Flow:
#   1. Init clean CdcTest with dbo.users CDC-enabled (3 baseline rows).
#   2. Run a baseline `read` against BASELINE_VERSION; capture STATE.
#   3. Generate noise commits, sys.sp_cdc_scan, sys.sp_cdc_cleanup_change_table
#      with low_water_mark = max_lsn. After this, fn_cdc_get_min_lsn('dbo_users')
#      is greater than the saved baseline LSN.
#   4. Re-run `read` against TARGET_VERSION passing the stale state file.
#      Expect non-zero exit + the "Saved offset no longer present" string.
#
# Env:
#   BASELINE_VERSION    source-mssql tag for state capture (default: 4.4.2).
#                       Any version works; this is the connector that
#                       writes the STATE message we'll later replay.
#   TARGET_VERSION      source-mssql tag to reproduce the regression on
#                       (default: 4.3.4 — the first version with the
#                       new per-instance LSN-range check). Try 4.4.2 /
#                       4.4.3 / latest to confirm the bug persists.
#   REPRO_OUT           output parent dir (default: /tmp/source-mssql-repro)
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SKILL="$(cd "$HERE/.." && pwd)"
GENERIC="$(cd "$SKILL/../source-mssql-e2e-tests" && pwd)"

REPRO_OUT="${REPRO_OUT:-/tmp/source-mssql-repro}"
BASELINE_VERSION="${BASELINE_VERSION:-4.4.2}"
TARGET_VERSION="${TARGET_VERSION:-4.3.4}"
export REPRO_OUT

# 1. Clean CdcTest + dbo.users CDC enable.
"$GENERIC/scripts/apply-sql.sh" "$SKILL/fixtures/sql/00-init-cdc.sql"

mkdir -p "$REPRO_OUT/working"
"$GENERIC/scripts/render-config.sh" \
  "$SKILL/fixtures/configs/cdc.template.json" \
  "$REPRO_OUT/working/cdc.json"

# 2. Baseline read — captures STATE.
"$GENERIC/scripts/run-protocol-cmd.sh" read repro-11451-baseline "$BASELINE_VERSION" \
  --config-path="$REPRO_OUT/working/cdc.json" \
  --catalog-path="$SKILL/fixtures/catalogs/users-cdc.json"

# 3. Pull STATE messages out of stdout.txt into a state file.
"$SKILL/scripts/extract-state.py" \
  "$REPRO_OUT/repro-11451-baseline/stdout.txt" \
  > "$REPRO_OUT/working/state.json"

# 4. Generate noise + advance min LSN past the saved state.
"$GENERIC/scripts/apply-sql.sh" "$SKILL/fixtures/sql/repro-11451-lsn-cleanup.sql"

# 5. Re-read with stale state. Expect non-zero + the "Saved offset
#    no longer present" string.
set +e
"$GENERIC/scripts/run-protocol-cmd.sh" read repro-11451-stale "$TARGET_VERSION" \
  --config-path="$REPRO_OUT/working/cdc.json" \
  --catalog-path="$SKILL/fixtures/catalogs/users-cdc.json" \
  --state-path="$REPRO_OUT/working/state.json"
RC=$?
set -e

ERR="$REPRO_OUT/repro-11451-stale/stderr.txt"
if [[ "$RC" -eq 0 ]]; then
  echo "FAIL: expected non-zero exit on $TARGET_VERSION (regression unreproduced)." >&2
  exit 1
fi
if ! grep -q "Saved offset no longer present" "$ERR"; then
  echo "FAIL: expected 'Saved offset no longer present' in $ERR." >&2
  exit 1
fi
if ! grep -q "is no longer available in SQL Server transaction logs" "$ERR"; then
  echo "FAIL: expected 'is no longer available in SQL Server transaction logs' in $ERR." >&2
  exit 1
fi
echo "PASS: repro-11451 reproduced on $TARGET_VERSION (baseline=$BASELINE_VERSION, exit=$RC)." >&2
