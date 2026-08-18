#!/usr/bin/env bash
# Reproduce airbytehq/oncall#12162: source-mssql crashes when a CDC
# stream's identifier contains whitespace.
#
# Symptom: read exits non-zero with a Debezium configuration error
# rejecting the `message.key.columns` value.
#
# Env:
#   VERSION       source-mssql tag (default: 4.4.2). Use VERSION=dev
#                 after `:airbyteDocker` to test a fix locally.
#   REPRO_OUT     output parent dir (default: /tmp/source-mssql-repro)
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SKILL="$(cd "$HERE/.." && pwd)"
GENERIC="$(cd "$SKILL/../source-mssql-e2e-tests" && pwd)"

REPRO_OUT="${REPRO_OUT:-/tmp/source-mssql-repro}"
VERSION="${VERSION:-4.4.2}"
export REPRO_OUT

"$GENERIC/scripts/apply-sql.sh" "$SKILL/fixtures/sql/00-init-cdc.sql"
"$GENERIC/scripts/apply-sql.sh" "$SKILL/fixtures/sql/repro-12162-spaces-in-name.sql"

mkdir -p "$REPRO_OUT/working"
"$GENERIC/scripts/render-config.sh" \
  "$SKILL/fixtures/configs/cdc.template.json" \
  "$REPRO_OUT/working/cdc.json"

set +e
"$GENERIC/scripts/run-protocol-cmd.sh" read repro-12162 "$VERSION" \
  --config-path="$REPRO_OUT/working/cdc.json" \
  --catalog-path="$SKILL/fixtures/catalogs/order-items-cdc.json"
RC=$?
set -e

ERR="$REPRO_OUT/repro-12162/stderr.txt"
if [[ "$RC" -eq 0 ]]; then
  echo "FAIL: expected non-zero exit on $VERSION (regression unreproduced)." >&2
  exit 1
fi
if ! grep -q "io.debezium.DebeziumException" "$ERR"; then
  echo "FAIL: expected 'io.debezium.DebeziumException' in $ERR." >&2
  exit 1
fi
if ! grep -q "message.key.columns" "$ERR"; then
  echo "FAIL: expected 'message.key.columns' in $ERR." >&2
  exit 1
fi
echo "PASS: repro-12162 reproduced on $VERSION (exit=$RC)." >&2
