#!/usr/bin/env bash
# airbytehq/oncall#12094 — source-mssql writes Debezium schema history
# for every table in the database, regardless of catalog selection.
# Read's stdout.txt contains N "Adding table CdcTest.dbo.* to the list
# of capture schema tables" AirbyteLog envelopes where N includes every
# noise table, even though the configured catalog has one stream.
#
# Migrated from scripts/repro-12094.sh: the inline `grep -c '<X>' | -lt`
# threshold check collapses to `--expect-match=stdout:<X>:N` where N
# defaults to 30 (the fixture creates 30 noise tables).
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

"$GENERIC/scripts/run.sh" \
  --command=read \
  --test-version="${VERSION:-4.4.2}" \
  --step-name=12094 \
  --fixture="$SKILL/fixtures/sql/00-init-cdc.sql" \
  --fixture="$SKILL/fixtures/sql/repro-12094-schema-history.sql" \
  --config-template="$SKILL/fixtures/configs/cdc.template.json" \
  --catalog="$SKILL/fixtures/catalogs/users-cdc.json" \
  --keep-backend \
  --expect-match='stdout:Adding table CdcTest\..* to the list of capture schema tables:'"${MIN_LOADED:-30}" \
  -- --enable-debug-logs=True
