#!/usr/bin/env bash
# airbytehq/oncall#13433 — CDC heartbeats advance through an expensive
# backlog without records for the configured streams.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SKILL="$(cd "$HERE/.." && pwd)"
GENERIC="$(cd "$SKILL/../source-mssql-e2e-tests" && pwd)"
ROOT="$(git -C "$SKILL" rev-parse --show-toplevel)"

IMAGE_TAG="${IMAGE_TAG:-${1:-5.0.0}}"
EXPECT="${EXPECT:-bug}"
INCLUDED_TABLES="${INCLUDED_TABLES:-350}"
NOISE_TRANSACTIONS="${NOISE_TRANSACTIONS:-20000}"
REPRO_OUT="${REPRO_OUT:-/home/ubuntu/repro13433/$EXPECT}"
export REPRO_OUT
mkdir -p "$REPRO_OUT"

if [[ "$INCLUDED_TABLES" != 350 || "$NOISE_TRANSACTIONS" != 20000 ]]; then
  sed \
    -e "s/<= 350/<= $INCLUDED_TABLES/g" \
    -e "s/<= 20000/<= $NOISE_TRANSACTIONS/g" \
    "$SKILL/fixtures/sql/13433-progressing-heartbeats-part1.sql" \
    > "$REPRO_OUT/part1.sql"
  sed \
    -e "s/<= 20000/<= $NOISE_TRANSACTIONS/g" \
    "$SKILL/fixtures/sql/13433-progressing-heartbeats-part2.sql" \
    > "$REPRO_OUT/part2.sql"
  PART1="$REPRO_OUT/part1.sql"
  PART2="$REPRO_OUT/part2.sql"
else
  PART1="$SKILL/fixtures/sql/13433-progressing-heartbeats-part1.sql"
  PART2="$SKILL/fixtures/sql/13433-progressing-heartbeats-part2.sql"
fi

"$GENERIC/scripts/start-backend.sh"
"$GENERIC/scripts/apply-sql.sh" "$SKILL/fixtures/sql/00-init-cdc.sql"
"$GENERIC/scripts/apply-sql.sh" "$PART1"

python3 - "$REPRO_OUT/catalog.json" "$INCLUDED_TABLES" <<'PY'
import json
import sys

path, count = sys.argv[1], int(sys.argv[2])
def stream(name):
    return {
        "stream": {
            "name": name,
            "namespace": "dbo",
            "json_schema": {
                "type": "object",
                "properties": {
                    "id": {"type": "number", "airbyte_type": "integer"},
                    "v": {"type": "number", "airbyte_type": "integer"},
                    "_ab_cdc_updated_at": {"type": "string"},
                    "_ab_cdc_deleted_at": {"type": "string"},
                    "_ab_cdc_cursor": {"type": "number", "airbyte_type": "integer"},
                    "_ab_cdc_event_serial_no": {"type": "string"},
                    "_ab_cdc_lsn": {"type": "string"},
                },
            },
            "supported_sync_modes": ["incremental"],
            "source_defined_cursor": True,
            "default_cursor_field": ["_ab_cdc_cursor"],
            "source_defined_primary_key": [["id"]],
            "is_resumable": True,
            "is_file_based": False,
        },
        "sync_mode": "incremental",
        "destination_sync_mode": "append_dedup",
        "primary_key": [["id"]],
        "cursor_field": ["_ab_cdc_cursor"],
        "generation_id": 0,
        "minimum_generation_id": 0,
        "sync_id": 0,
        "destination_object_name": name,
        "include_files": False,
    }
catalog = {"streams": [stream("repro_13433")] +
           [stream(f"catalog_static_13433_{i:03d}") for i in range(1, count + 1)]}
with open(path, "w") as f:
    json.dump(catalog, f, indent=2)
PY

jq '.replication_method.initial_waiting_seconds = 120' \
  "$SKILL/fixtures/configs/cdc.template.json" > "$REPRO_OUT/config-template.json"

"$GENERIC/scripts/run.sh" \
  --command=read \
  --test-version="$IMAGE_TAG" \
  --step-name=first \
  --skip-fixtures \
  --config-template="$REPRO_OUT/config-template.json" \
  --catalog="$REPRO_OUT/catalog.json" \
  --keep-backend
"$GENERIC/scripts/extract-state.py" "$REPRO_OUT/first/read/stdout.txt" \
  > "$REPRO_OUT/state.json"

"$GENERIC/scripts/apply-sql.sh" "$PART2"
cp "$REPRO_OUT/first/config.json" "$REPRO_OUT/config-second.json"

start_epoch="$(date +%s)"
"$GENERIC/scripts/run.sh" \
  --command=read \
  --test-version="$IMAGE_TAG" \
  --step-name=second \
  --skip-fixtures \
  --config-template="$REPRO_OUT/config-second.json" \
  --catalog="$REPRO_OUT/catalog.json" \
  --state="$REPRO_OUT/state.json" \
  --keep-backend
end_epoch="$(date +%s)"

python3 - "$REPRO_OUT" "$start_epoch" "$end_epoch" "$EXPECT" <<'PY' | tee "$REPRO_OUT/summary.txt"
import json
import re
import sys
from pathlib import Path

out, start, end, expect = Path(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
stderr = (out / "second" / "stderr.txt").read_text()
stdout = (out / "second" / "stdout.txt").read_text()
logs = stderr + stdout
progress = re.findall(r"Heartbeat progressing to position", logs)
close = re.findall(r"Shutting down Debezium engine: heartbeat position has progressed", logs)
new_close = re.findall(r"heartbeat position has progressed but no records were received", logs)
states = []
for line in stdout.splitlines():
    try:
        message = json.loads(line)
    except json.JSONDecodeError:
        continue
    if message.get("type") == "STATE":
        states.append(message)
print(f"duration_seconds={end - start}")
print(f"heartbeat_progressing_lines={len(progress)}")
print(f"progress_close_lines={len(close)}")
print(f"progress_without_records_close_lines={len(new_close)}")
print(f"state_count={len(states)}")
if states:
    print("state_timestamps_relative_to_start=protocol timestamps are not present; artifact order used")
if expect == "bug":
    if not progress or close or len(states) != 1:
        raise SystemExit("baseline expectation failed")
else:
    if not progress or not close or not new_close or len(states) < 1:
        raise SystemExit("fixed expectation failed")
PY
