#!/usr/bin/env bash
# Prove that a CDC read can resume from saved state after upstream changes:
# the replay emits only the changed rows and its Debezium offset advances.
#
# Env:
#   VERSION       source-mssql tag (default: 5.0.0)
#   REPRO_OUT     output parent dir (default: /tmp/source-mssql-repro)
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SKILL="$(cd "$HERE/.." && pwd)"
GENERIC="$(cd "$SKILL/../source-mssql-e2e-tests" && pwd)"

REPRO_OUT="${REPRO_OUT:-/tmp/source-mssql-repro}"
VERSION="${VERSION:-5.0.0}"
STEP_NAME="${STEP_NAME:-canary-resume}"
export REPRO_OUT

"$GENERIC/scripts/stop-backend.sh" || true
"$GENERIC/scripts/run.sh" \
  --command=read \
  --replay \
  --test-version="$VERSION" \
  --step-name="$STEP_NAME" \
  --fixture="$SKILL/fixtures/sql/00-init-cdc.sql" \
  --fixture="$SKILL/fixtures/sql/canary-resume-seed.sql" \
  --mutate="$SKILL/fixtures/sql/canary-resume-mutate.sql" \
  --config-template="$SKILL/fixtures/configs/cdc.template.json" \
  --catalog="$SKILL/fixtures/catalogs/resume-canary-cdc.json" \
  --keep-backend

ARTIFACTS="$REPRO_OUT/$STEP_NAME"
SECOND_OUT="$ARTIFACTS/read-2/stdout.txt"
STATE_1="$ARTIFACTS/state-1.json"
STATE_2="$ARTIFACTS/state-2.json"

if ! jq -e 'length > 0' "$STATE_1" >/dev/null; then
  echo "FAIL: first read did not emit a STATE in $STATE_1." >&2
  exit 1
fi

RECORD_IDS="$(jq -s -c '[.[] | select(.type == "RECORD") | .record.data.id] | sort' "$SECOND_OUT")"
if [[ "$RECORD_IDS" != "[101,102,104]" ]]; then
  echo "FAIL: expected replay IDs [101,102,104], got $RECORD_IDS." >&2
  exit 1
fi

STATE_1_OFFSET="$(jq -er '.[] | select(.type == "GLOBAL") | .global.shared_state.state.mssql_cdc_offset | to_entries | if length == 1 then .[0].value | fromjson | .commit_lsn else error("expected one mssql_cdc_offset entry") end' "$STATE_1")"
STATE_2_OFFSET="$(jq -er '.[] | select(.type == "GLOBAL") | .global.shared_state.state.mssql_cdc_offset | to_entries | if length == 1 then .[0].value | fromjson | .commit_lsn else error("expected one mssql_cdc_offset entry") end' "$STATE_2")"
if [[ -z "$STATE_1_OFFSET" || -z "$STATE_2_OFFSET" ]]; then
  echo "FAIL: could not find commit_lsn in replay states." >&2
  exit 1
fi
if ! python3 - "$STATE_1_OFFSET" "$STATE_2_OFFSET" <<'PY'
import sys

if int(sys.argv[2].replace(":", ""), 16) <= int(sys.argv[1].replace(":", ""), 16):
    raise SystemExit(1)
PY
then
  echo "FAIL: commit_lsn did not advance from $STATE_1_OFFSET to $STATE_2_OFFSET." >&2
  exit 1
fi

echo "PASS: canary-resume emitted only IDs $RECORD_IDS and advanced commit_lsn from $STATE_1_OFFSET to $STATE_2_OFFSET." >&2
