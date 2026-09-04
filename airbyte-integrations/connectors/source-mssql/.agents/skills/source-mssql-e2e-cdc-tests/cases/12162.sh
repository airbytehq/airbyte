#!/usr/bin/env bash
# airbytehq/oncall#12162 — source-mssql crashes when a CDC stream's
# identifier contains whitespace. Read exits non-zero with a Debezium
# configuration error rejecting the `message.key.columns` value.
#
# Migrated from scripts/repro-12162.sh: the inline `grep -q '<X>' "$ERR"
# || exit 1` boilerplate collapses to `--expect-match=stderr:<X>` flags
# that `run.sh` enforces before returning.
#
# Env:
#   VERSION       source-mssql tag (default: 4.4.2). Use VERSION=dev
#                 after `:dockerBuildx` to test a fix locally.
#   REPRO_OUT     output parent dir (default: /tmp/source-mssql-repro)
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SKILL="$(cd "$HERE/.." && pwd)"
GENERIC="$(cd "$SKILL/../source-mssql-e2e-tests" && pwd)"

"$GENERIC/scripts/run.sh" \
  --command=read \
  --test-version="${VERSION:-4.4.2}" \
  --step-name=12162 \
  --fixture="$SKILL/fixtures/sql/00-init-cdc.sql" \
  --fixture="$SKILL/fixtures/sql/repro-12162-spaces-in-name.sql" \
  --config-template="$SKILL/fixtures/configs/cdc.template.json" \
  --catalog="$SKILL/fixtures/catalogs/order-items-cdc.json" \
  --keep-backend \
  --expect-test=fail \
  --expect-match=stderr:io.debezium.DebeziumException \
  --expect-match=stderr:message.key.columns
