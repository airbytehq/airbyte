#!/usr/bin/env bash
# Start a throwaway SQL Server 2022 container for source-mssql e2e tests.
# Idempotent: succeeds whether or not the container already exists.
#
# Env:
#   BACKEND_NAME            container name (default: source-mssql-db-backend)
#   BACKEND_SA_PASSWORD     sa password (default: Test_password_1)
#   BACKEND_PORT            host port mapped to 1433/tcp (default: 1433)
set -euo pipefail

BACKEND_NAME="${BACKEND_NAME:-source-mssql-db-backend}"
BACKEND_SA_PASSWORD="${BACKEND_SA_PASSWORD:-Test_password_1}"
BACKEND_PORT="${BACKEND_PORT:-1433}"

if docker inspect "$BACKEND_NAME" >/dev/null 2>&1; then
  echo "[start-backend] $BACKEND_NAME already exists; reusing." >&2
else
  docker run -d --rm \
    --name "$BACKEND_NAME" \
    -e ACCEPT_EULA=Y \
    -e MSSQL_SA_PASSWORD="$BACKEND_SA_PASSWORD" \
    -e MSSQL_AGENT_ENABLED=true \
    -e MSSQL_PID=Developer \
    -p "$BACKEND_PORT:1433" \
    mcr.microsoft.com/mssql/server:2022-latest >/dev/null
fi

echo "[start-backend] waiting for $BACKEND_NAME to accept connections…" >&2
for _ in $(seq 1 60); do
  if docker exec "$BACKEND_NAME" /opt/mssql-tools18/bin/sqlcmd \
       -S localhost -U sa -P "$BACKEND_SA_PASSWORD" -C -Q "SELECT 1" \
       >/dev/null 2>&1; then
    echo "[start-backend] $BACKEND_NAME ready." >&2
    exit 0
  fi
  sleep 2
done

echo "[start-backend] timed out waiting for $BACKEND_NAME after 120s." >&2
exit 1
