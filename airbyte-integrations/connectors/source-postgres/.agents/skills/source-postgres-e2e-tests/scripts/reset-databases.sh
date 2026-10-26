#!/usr/bin/env bash
# Reset non-system databases on the source-postgres e2e backend.
# Used by run.sh --reset=fixture before a second comparison sweep.
#
# Env:
#   BACKEND_NAME        container name (default: source-postgres-db-backend)
#   BACKEND_PASSWORD    postgres password (default: test_password)
#   BACKEND_DB          database to recreate (default: test_db)
set -euo pipefail

BACKEND_NAME="${BACKEND_NAME:-source-postgres-db-backend}"
BACKEND_PASSWORD="${BACKEND_PASSWORD:-test_password}"
BACKEND_DB="${BACKEND_DB:-test_db}"

if [[ "$BACKEND_DB" == "postgres" || "$BACKEND_DB" == "template0" || "$BACKEND_DB" == "template1" ]]; then
  echo "[reset-databases] BACKEND_DB must not be a system database (got: $BACKEND_DB)" >&2
  exit 1
fi

echo "[reset-databases] dropping non-system databases on $BACKEND_NAME" >&2
docker exec -e PGPASSWORD="$BACKEND_PASSWORD" "$BACKEND_NAME" \
  psql -U postgres -d postgres -Atc \
    "SELECT datname FROM pg_database WHERE datistemplate = false AND datname <> 'postgres'" \
  | while IFS= read -r db; do
      escaped_db="${db//\"/\"\"}"
      docker exec -e PGPASSWORD="$BACKEND_PASSWORD" "$BACKEND_NAME" \
        psql -U postgres -d postgres -v ON_ERROR_STOP=1 \
          -c "DROP DATABASE \"$escaped_db\" WITH (FORCE)"
    done

escaped_backend_db="${BACKEND_DB//\"/\"\"}"
docker exec -e PGPASSWORD="$BACKEND_PASSWORD" "$BACKEND_NAME" \
  psql -U postgres -d postgres -v ON_ERROR_STOP=1 \
  -c "CREATE DATABASE \"$escaped_backend_db\""
