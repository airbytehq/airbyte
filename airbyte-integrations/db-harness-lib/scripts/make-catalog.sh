#!/usr/bin/env bash
# Derive a ConfiguredAirbyteCatalog from the output of a `discover` run.
#
# Usage:  make-catalog.sh <discover-output-dir> <output.json>
#
# `read` requires a *configured* catalog, but `discover` emits a plain
# AirbyteCatalog. Hand-writing the configured form is the step most
# likely to be done inconsistently — and a catalog that has drifted from
# the fixture is what produces the "bad config" failures on read — so
# derive it mechanically from a real discover instead.
#
# The configured streams carry `generation_id`, `minimum_generation_id`,
# `sync_id`, `destination_object_name`, `include_files`, `cursor_field`,
# and `stream.is_file_based` because the bulk-CDK schema validator
# rejects them as null — verified on both 4.4.12 and 5.0.0. `discover`
# does not emit `is_file_based`, so it is filled in here rather than
# copied, and `cursor_field` is an empty list when there is no cursor.
#
# Env:
#   STREAMS       comma-separated stream names to select (default: all)
#   SYNC_MODE     full_refresh | incremental (default: full_refresh)
#   CURSOR_FIELD  cursor field name, set only for incremental
set -euo pipefail

STREAMS="${STREAMS:-}"
SYNC_MODE="${SYNC_MODE:-full_refresh}"
CURSOR_FIELD="${CURSOR_FIELD:-}"

if [[ $# -lt 2 ]]; then
  echo "usage: $(basename "$0") <discover-output-dir> <output.json>" >&2
  exit 2
fi
DISCOVER_DIR="$1"
OUTPUT="$2"

case "$SYNC_MODE" in
  full_refresh|incremental) ;;
  *) echo "[make-catalog] SYNC_MODE must be full_refresh|incremental (got '$SYNC_MODE')" >&2; exit 2 ;;
esac

STDOUT_FILE="$(find "$DISCOVER_DIR" -name stdout.txt -type f 2>/dev/null | head -n 1)"
if [[ -z "$STDOUT_FILE" ]]; then
  echo "[make-catalog] no stdout.txt under $DISCOVER_DIR — did discover run?" >&2
  exit 1
fi

mkdir -p "$(dirname "$OUTPUT")"
TMP_OUTPUT="$(mktemp "$OUTPUT.XXXXXX")"
trap 'rm -f "$TMP_OUTPUT"' EXIT

jq -s \
  --arg streams "$STREAMS" \
  --arg mode "$SYNC_MODE" \
  --arg cursor "$CURSOR_FIELD" '
  ([.[] | select(.type == "CATALOG")] | last | .catalog.streams) as $all
  | (if $streams == "" then $all
     else ($streams | split(",")) as $want
       | [$all[] | select((.name as $n | $want | index($n)) != null)]
     end) as $sel
  | if ($sel | length) == 0 then
      error("no discovered streams matched STREAMS=\($streams)")
    else
      {streams: [$sel[] | {
          stream: (. + {is_file_based: (.is_file_based // false)}),
          sync_mode: $mode,
          cursor_field: (if $cursor == "" then [] else [$cursor] end),
          destination_sync_mode: (if $mode == "incremental" then "append" else "overwrite" end),
          generation_id: 0,
          minimum_generation_id: 0,
          sync_id: 0,
          destination_object_name: .name,
          include_files: false
        }
        + {primary_key: (.source_defined_primary_key // [])}
      ]}
    end
  ' "$STDOUT_FILE" > "$TMP_OUTPUT"
mv "$TMP_OUTPUT" "$OUTPUT"

echo "[make-catalog] $OUTPUT ($(jq '.streams | length' "$OUTPUT") stream(s), $SYNC_MODE)" >&2
