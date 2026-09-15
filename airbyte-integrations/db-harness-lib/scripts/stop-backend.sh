#!/usr/bin/env bash
# Default backend teardown: remove the engine's backend container.
# Engines needing extra cleanup (volumes, networks, sidecars) provide
# their own stop-backend.sh in ENGINE_SCRIPTS_DIR, which run.sh prefers.
#
# Env:
#   BACKEND_NAME    container name (required)
set -euo pipefail

BACKEND_NAME="${BACKEND_NAME:?BACKEND_NAME must be set}"

docker rm -f "$BACKEND_NAME" >/dev/null 2>&1 || true
echo "[stop-backend] $BACKEND_NAME removed." >&2
