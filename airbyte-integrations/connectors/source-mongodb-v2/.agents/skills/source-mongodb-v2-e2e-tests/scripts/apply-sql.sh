#!/usr/bin/env bash
# Apply a mongosh JavaScript fixture to the e2e backend on stdin.
#
# The name follows the db-harness-lib engine contract (apply-sql.sh), but
# MongoDB fixtures are mongosh scripts (.js), not SQL.
#
# Usage:  apply-sql.sh <path/to/fixture.js>
#
# Env:
#   BACKEND_NAME        container name (default: source-mongodb-v2-db-backend)
#   BACKEND_DB          database the script starts in (default: test_db)
set -euo pipefail

BACKEND_NAME="${BACKEND_NAME:-source-mongodb-v2-db-backend}"
BACKEND_DB="${BACKEND_DB:-test_db}"

if [[ $# -lt 1 ]]; then
  echo "usage: $(basename "$0") <path/to/fixture.js>" >&2
  exit 2
fi
FIXTURE="$1"
if [[ ! -f "$FIXTURE" ]]; then
  echo "[apply-sql] not a file: $FIXTURE" >&2
  exit 2
fi

docker exec -i "$BACKEND_NAME" \
  mongosh --quiet "mongodb://localhost:27017/$BACKEND_DB" < "$FIXTURE"
echo "[apply-sql] applied $FIXTURE." >&2
