#!/usr/bin/env bash
# MSSQL engine shim; implementation moved to db-harness-lib.
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(git -C "$SKILL_DIR" rev-parse --show-toplevel)"

exec "$REPO_ROOT/airbyte-integrations/db-harness-lib/scripts/extract-state.py" "$@"
