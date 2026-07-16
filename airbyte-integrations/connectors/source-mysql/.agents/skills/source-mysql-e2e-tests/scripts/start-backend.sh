#!/usr/bin/env bash
# Start a throwaway MySQL container for source-mysql e2e tests.
# Idempotent: succeeds whether or not the container already exists.
#
# Started with ROW-format binary logging + GTIDs so the same backend can
# be reused by a CDC repro (binlog) without a restart.
#
# Env:
#   BACKEND_NAME        container name (default: source-mysql-db-backend)
#   BACKEND_PASSWORD    root password (default: test_password)
#   BACKEND_DB          initial database (default: test_db)
#   BACKEND_PORT        host port mapped to 3306/tcp (default: 3306)
#   BACKEND_IMAGE       image (default: mysql:8.0)
set -euo pipefail

BACKEND_NAME="${BACKEND_NAME:-source-mysql-db-backend}"
BACKEND_PASSWORD="${BACKEND_PASSWORD:-test_password}"
BACKEND_DB="${BACKEND_DB:-test_db}"
BACKEND_PORT="${BACKEND_PORT:-3306}"
BACKEND_IMAGE="${BACKEND_IMAGE:-mysql:8.0}"

if docker inspect "$BACKEND_NAME" >/dev/null 2>&1; then
  echo "[start-backend] $BACKEND_NAME already exists; reusing." >&2
else
  docker run -d --rm \
    --name "$BACKEND_NAME" \
    -e MYSQL_ROOT_PASSWORD="$BACKEND_PASSWORD" \
    -e MYSQL_DATABASE="$BACKEND_DB" \
    -p "$BACKEND_PORT:3306" \
    "$BACKEND_IMAGE" \
    --server-id=223344 \
    --log-bin=mysql-bin \
    --binlog-format=ROW \
    --binlog-row-image=FULL \
    --gtid-mode=ON \
    --enforce-gtid-consistency=ON >/dev/null
fi

echo "[start-backend] waiting for $BACKEND_NAME to accept connections…" >&2
for _ in $(seq 1 60); do
  if docker exec -e MYSQL_PWD="$BACKEND_PASSWORD" "$BACKEND_NAME" \
       mysql -uroot -N -e "SELECT 1" >/dev/null 2>&1; then
    echo "[start-backend] $BACKEND_NAME ready." >&2
    exit 0
  fi
  sleep 2
done

echo "[start-backend] timed out waiting for $BACKEND_NAME after 120s." >&2
exit 1
