#!/usr/bin/env bash
# Start a throwaway PostgreSQL container for source-postgres e2e tests.
# Idempotent: succeeds whether or not the container already exists.
#
# Env:
#   BACKEND_NAME        container name (default: source-postgres-db-backend)
#   BACKEND_PASSWORD    postgres password (default: test_password)
#   BACKEND_DB          initial database (default: test_db)
#   BACKEND_PORT        host port mapped to 5432/tcp (default: 5432)
#   BACKEND_IMAGE       image (default: postgres:16)
set -euo pipefail

BACKEND_NAME="${BACKEND_NAME:-source-postgres-db-backend}"
BACKEND_PASSWORD="${BACKEND_PASSWORD:-test_password}"
BACKEND_DB="${BACKEND_DB:-test_db}"
BACKEND_PORT="${BACKEND_PORT:-5432}"
BACKEND_IMAGE="${BACKEND_IMAGE:-postgres:16}"

if [[ "$(docker inspect -f '{{.State.Running}}' "$BACKEND_NAME" 2>/dev/null || echo false)" == "true" ]]; then
  echo "[start-backend] $BACKEND_NAME already running; reusing." >&2
else
  docker rm -f "$BACKEND_NAME" >/dev/null 2>&1 || true
  docker run -d --rm \
    --name "$BACKEND_NAME" \
    -e POSTGRES_PASSWORD="$BACKEND_PASSWORD" \
    -e POSTGRES_DB="$BACKEND_DB" \
    -p "$BACKEND_PORT:5432" \
    "$BACKEND_IMAGE" \
    -c wal_level=logical \
    -c max_replication_slots=10 \
    -c max_wal_senders=10 >/dev/null
fi

echo "[start-backend] waiting for $BACKEND_NAME to accept connections…" >&2
for _ in $(seq 1 60); do
  if docker exec -e PGPASSWORD="$BACKEND_PASSWORD" "$BACKEND_NAME" \
       psql -U postgres -d "$BACKEND_DB" -Atc "SELECT 1" >/dev/null 2>&1; then
    echo "[start-backend] $BACKEND_NAME ready." >&2
    exit 0
  fi
  sleep 2
done

echo "[start-backend] timed out waiting for $BACKEND_NAME after 120s." >&2
exit 1
