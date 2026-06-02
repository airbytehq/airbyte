#!/usr/bin/env bash
# Apply a .sql file to the e2e backend via `docker cp` + `docker exec sqlcmd`.
#
# Usage:  apply-sql.sh <path/to/file.sql>
#
# Env:
#   BACKEND_NAME            container name (default: source-mssql-db-backend)
#   BACKEND_SA_PASSWORD     sa password (default: Test_password_1)
set -euo pipefail

BACKEND_NAME="${BACKEND_NAME:-source-mssql-db-backend}"
BACKEND_SA_PASSWORD="${BACKEND_SA_PASSWORD:-Test_password_1}"

if [[ $# -lt 1 ]]; then
  echo "usage: $(basename "$0") <path/to/file.sql>" >&2
  exit 2
fi
SQL_FILE="$1"
if [[ ! -f "$SQL_FILE" ]]; then
  echo "[apply-sql] not a file: $SQL_FILE" >&2
  exit 2
fi

REMOTE="/tmp/$(basename "$SQL_FILE")"
docker cp "$SQL_FILE" "$BACKEND_NAME:$REMOTE"
docker exec "$BACKEND_NAME" /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P "$BACKEND_SA_PASSWORD" -C -i "$REMOTE"
echo "[apply-sql] applied $SQL_FILE." >&2
