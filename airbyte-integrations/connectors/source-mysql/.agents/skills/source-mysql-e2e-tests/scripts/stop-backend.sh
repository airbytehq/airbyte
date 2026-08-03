#!/usr/bin/env bash
# Stop and remove the source-mysql e2e backend container.
# Idempotent: a no-op if the container doesn't exist.
#
# Env:
#   BACKEND_NAME        container name (default: source-mysql-db-backend)
set -euo pipefail

BACKEND_NAME="${BACKEND_NAME:-source-mysql-db-backend}"

docker rm -f "$BACKEND_NAME" >/dev/null 2>&1 || true
echo "[stop-backend] $BACKEND_NAME removed." >&2
