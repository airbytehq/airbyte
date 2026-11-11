#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SKILL="$(cd "$HERE/.." && pwd)"
GENERIC="$(cd "$SKILL/../source-mysql-e2e-tests" && pwd)"

"$GENERIC/scripts/run.sh" \
  --command=read \
  --test-version="${VERSION:-3.53.4}" \
  --step-name=cdc-initial-load \
  --fixture="$SKILL/fixtures/sql/00-init-cdc.sql" \
  --config-template="$SKILL/fixtures/configs/cdc.template.json" \
  --catalog="$SKILL/fixtures/catalogs/users-cdc.json" \
  --keep-backend \
  --expect-test=pass \
  --min-records=3 \
  --min-states=1
