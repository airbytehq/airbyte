#!/usr/bin/env bash
# Stop and remove the source-mssql e2e backend container.
# Idempotent: a no-op if the container doesn't exist.
#
# Env:
#   BACKEND_NAME            container name (default: source-mssql-db-backend)
set -euo pipefail

BACKEND_NAME="${BACKEND_NAME:-source-mssql-db-backend}"

docker rm -f "$BACKEND_NAME" >/dev/null 2>&1 || true
echo "[stop-backend] $BACKEND_NAME removed." >&2
