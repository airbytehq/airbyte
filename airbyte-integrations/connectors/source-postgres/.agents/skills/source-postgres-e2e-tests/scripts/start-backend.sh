#!/usr/bin/env bash
# Start a throwaway PostgreSQL container for source-postgres e2e tests.
# Idempotent: succeeds whether or not the container already exists.
#
# Started with `wal_level=logical` so the same backend can be reused by
# the CDC variant (logical replication slots + publications) without a
# restart.
#
# Env:
#   BACKEND_NAME        container name (default: source-postgres-db-backend)
#   BACKEND_PASSWORD    postgres superuser password (default: test_password)
#   BACKEND_DB          initial database (default: test_db)
#   BACKEND_PORT        host port mapped to 5432/tcp (default: 5432)
#   BACKEND_IMAGE       image (default: postgres:16)
set -euo pipefail

BACKEND_NAME="${BACKEND_NAME:-source-postgres-db-backend}"
BACKEND_PASSWORD="${BACKEND_PASSWORD:-test_password}"
BACKEND_DB="${BACKEND_DB:-test_db}"
BACKEND_PORT="${BACKEND_PORT:-5432}"
BACKEND_IMAGE="${BACKEND_IMAGE:-postgres:16}"

if docker inspect "$BACKEND_NAME" >/dev/null 2>&1; then
  echo "[start-backend] $BACKEND_NAME already exists; reusing." >&2
else
  docker run -d --rm \
    --name "$BACKEND_NAME" \
    -e POSTGRES_PASSWORD="$BACKEND_PASSWORD" \
    -e POSTGRES_DB="$BACKEND_DB" \
    -p "$BACKEND_PORT:5432" \
    "$BACKEND_IMAGE" \
    -c wal_level=logical \
    -c max_wal_senders=10 \
    -c max_replication_slots=10 >/dev/null
fi

echo "[start-backend] waiting for $BACKEND_NAME to accept connections…" >&2
for _ in $(seq 1 60); do
  if docker exec "$BACKEND_NAME" pg_isready -U postgres -d "$BACKEND_DB" >/dev/null 2>&1; then
    echo "[start-backend] $BACKEND_NAME ready." >&2
    exit 0
  fi
  sleep 2
done

echo "[start-backend] timed out waiting for $BACKEND_NAME after 120s." >&2
exit 1
