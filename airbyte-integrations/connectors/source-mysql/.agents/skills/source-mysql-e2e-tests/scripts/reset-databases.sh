#!/usr/bin/env bash
# Reset non-system databases on the source-mysql e2e backend.
# Used by run.sh --reset=fixture before a second comparison sweep.
#
# Env:
#   BACKEND_NAME        container name (default: source-mysql-db-backend)
#   BACKEND_PASSWORD    root password (default: test_password)
#   BACKEND_DB          database to recreate (default: test_db)
set -euo pipefail

BACKEND_NAME="${BACKEND_NAME:-source-mysql-db-backend}"
BACKEND_PASSWORD="${BACKEND_PASSWORD:-test_password}"
BACKEND_DB="${BACKEND_DB:-test_db}"

echo "[reset-databases] dropping non-system databases on $BACKEND_NAME" >&2
docker exec -e MYSQL_PWD="$BACKEND_PASSWORD" "$BACKEND_NAME" \
  mysql -uroot -N -e "SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('mysql','information_schema','performance_schema','sys')" \
  | while IFS= read -r db; do
      docker exec -e MYSQL_PWD="$BACKEND_PASSWORD" "$BACKEND_NAME" \
        mysql -uroot -e "DROP DATABASE \`$db\`"
    done
docker exec -e MYSQL_PWD="$BACKEND_PASSWORD" "$BACKEND_NAME" \
  mysql -uroot -e "CREATE DATABASE \`$BACKEND_DB\`"
