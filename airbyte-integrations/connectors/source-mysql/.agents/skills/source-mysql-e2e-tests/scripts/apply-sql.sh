#!/usr/bin/env bash
# Apply a .sql file to the e2e backend via `docker exec mysql` on stdin.
#
# Usage:  apply-sql.sh <path/to/file.sql>
#
# Env:
#   BACKEND_NAME        container name (default: source-mysql-db-backend)
#   BACKEND_PASSWORD    root password (default: test_password)
#   BACKEND_DB          database to apply against (default: test_db)
set -euo pipefail

BACKEND_NAME="${BACKEND_NAME:-source-mysql-db-backend}"
BACKEND_PASSWORD="${BACKEND_PASSWORD:-test_password}"
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

# MYSQL_PWD avoids the "password on the command line is insecure" warning.
docker exec -i -e MYSQL_PWD="$BACKEND_PASSWORD" "$BACKEND_NAME" \
  mysql -uroot "$BACKEND_DB" < "$SQL_FILE"
echo "[apply-sql] applied $SQL_FILE." >&2
