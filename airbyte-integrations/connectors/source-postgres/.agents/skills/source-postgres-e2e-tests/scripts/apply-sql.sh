#!/usr/bin/env bash
# Apply a .sql file to the e2e backend via `docker exec psql` on stdin.
#
# Usage:  apply-sql.sh <path/to/file.sql>
#
# Env:
#   BACKEND_NAME        container name (default: source-postgres-db-backend)
#   BACKEND_DB          database to apply against (default: test_db)
set -euo pipefail

BACKEND_NAME="${BACKEND_NAME:-source-postgres-db-backend}"
BACKEND_DB="${BACKEND_DB:-test_db}"

if [[ $# -lt 1 ]]; then
  echo "usage: $(basename "$0") <path/to/file.sql>" >&2
  exit 2
fi
SQL_FILE="$1"
if [[ ! -f "$SQL_FILE" ]]; then
  echo "[apply-sql] not a file: $SQL_FILE" >&2
  exit 2
fi

# psql connects over the local unix socket as the postgres superuser
# (trust auth in the stock image), so no password is needed here.
docker exec -i "$BACKEND_NAME" \
  psql -v ON_ERROR_STOP=1 -U postgres -d "$BACKEND_DB" < "$SQL_FILE"
echo "[apply-sql] applied $SQL_FILE." >&2
