#!/usr/bin/env bash
# Reproduce airbytehq/oncall#12094: source-mssql writes Debezium schema
# history for every table in the database, regardless of which streams
# the configured catalog selects.
#
# Symptom: stderr.txt contains many "Adding table CdcTest.dbo.* to the
# list of capture schema tables" lines (one per noise table), even
# though the configured catalog has a single stream.
#
# Env:
#   VERSION       source-mssql tag (default: 4.4.2)
#   REPRO_OUT     output parent dir (default: /tmp/source-mssql-repro)
#   MIN_LOADED    threshold for the schema-history-bloat assertion
#                 (default: 30)
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SKILL="$(cd "$HERE/.." && pwd)"
GENERIC="$(cd "$SKILL/../source-mssql-e2e-tests" && pwd)"

REPRO_OUT="${REPRO_OUT:-/tmp/source-mssql-repro}"
VERSION="${VERSION:-4.4.2}"
MIN_LOADED="${MIN_LOADED:-30}"
export REPRO_OUT

"$GENERIC/scripts/apply-sql.sh" "$SKILL/fixtures/sql/00-init-cdc.sql"
"$GENERIC/scripts/apply-sql.sh" "$SKILL/fixtures/sql/repro-12094-schema-history.sql"

mkdir -p "$REPRO_OUT/working"
"$GENERIC/scripts/render-config.sh" \
  "$SKILL/fixtures/configs/cdc.template.json" \
  "$REPRO_OUT/working/cdc.json"

"$GENERIC/scripts/run-protocol-cmd.sh" read repro-12094 "$VERSION" \
  --config-path="$REPRO_OUT/working/cdc.json" \
  --catalog-path="$SKILL/fixtures/catalogs/users-cdc.json" \
  --enable-debug-logs=True

# The Debezium "Adding table" lines surface as AirbyteLog messages on
# stdout, not stderr — bulk-CDK pipes connector logging through stdout
# as `{"type":"LOG", …}` envelopes.
OUT="$REPRO_OUT/repro-12094/stdout.txt"
LOADED=$(grep -c 'Adding table CdcTest\..* to the list of capture schema tables' "$OUT" || true)
if [[ "$LOADED" -lt "$MIN_LOADED" ]]; then
  echo "FAIL: expected >=$MIN_LOADED 'Adding table' lines in $OUT, got $LOADED." >&2
  exit 1
fi
echo "PASS: repro-12094 reproduced on $VERSION ($LOADED tables loaded into schema history; configured catalog has 1 stream)." >&2
