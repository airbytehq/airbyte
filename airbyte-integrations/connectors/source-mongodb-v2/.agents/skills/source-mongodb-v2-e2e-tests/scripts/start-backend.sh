#!/usr/bin/env bash
# Start a throwaway single-node MongoDB replica set for source-mongodb-v2
# e2e tests. Idempotent: succeeds whether or not the container already
# exists.
#
# The connector requires a replica set (it reads the oplog / change
# streams even for non-CDC discovery of the resume token), so the node is
# started with --replSet and initiated once it accepts connections. The
# replica-set member is registered under the container's bridge IP, not
# `localhost`, because the connector container launched by `airbyte-ops`
# performs replica-set discovery and must be able to reach the advertised
# host.
#
# Env:
#   BACKEND_NAME        container name (default: source-mongodb-v2-db-backend)
#   BACKEND_PORT        host port mapped to 27017/tcp (default: 27017)
#   BACKEND_IMAGE       image (default: mongo:7.0)
#   BACKEND_REPLSET     replica set name (default: rs0)
set -euo pipefail

BACKEND_NAME="${BACKEND_NAME:-source-mongodb-v2-db-backend}"
BACKEND_PORT="${BACKEND_PORT:-27017}"
BACKEND_IMAGE="${BACKEND_IMAGE:-mongo:7.0}"
BACKEND_REPLSET="${BACKEND_REPLSET:-rs0}"

mongosh() {
  docker exec -i "$BACKEND_NAME" mongosh --quiet "$@"
}

if [[ "$(docker inspect -f '{{.State.Running}}' "$BACKEND_NAME" 2>/dev/null || echo false)" == "true" ]]; then
  echo "[start-backend] $BACKEND_NAME already running; reusing." >&2
else
  docker rm -f "$BACKEND_NAME" >/dev/null 2>&1 || true
  docker run -d --rm \
    --name "$BACKEND_NAME" \
    -p "$BACKEND_PORT:27017" \
    "$BACKEND_IMAGE" \
    --replSet "$BACKEND_REPLSET" \
    --bind_ip_all >/dev/null
fi

echo "[start-backend] waiting for $BACKEND_NAME to accept connections…" >&2
ready=false
for _ in $(seq 1 60); do
  if mongosh --eval 'db.adminCommand({ ping: 1 })' >/dev/null 2>&1; then
    ready=true
    break
  fi
  sleep 2
done
if [[ "$ready" != true ]]; then
  echo "[start-backend] timed out waiting for $BACKEND_NAME after 120s." >&2
  exit 1
fi

BACKEND_IP=$(docker inspect "$BACKEND_NAME" \
  --format '{{.NetworkSettings.Networks.bridge.IPAddress}}')
if [[ -z "$BACKEND_IP" ]]; then
  echo "[start-backend] could not resolve bridge IP for $BACKEND_NAME." >&2
  exit 1
fi

# rs.status() fails with NotYetInitialized (code 94) until rs.initiate().
if mongosh --eval 'rs.status().ok' >/dev/null 2>&1; then
  echo "[start-backend] replica set $BACKEND_REPLSET already initiated." >&2
else
  echo "[start-backend] initiating replica set $BACKEND_REPLSET at $BACKEND_IP:27017" >&2
  mongosh --eval "rs.initiate({ _id: '$BACKEND_REPLSET', members: [{ _id: 0, host: '$BACKEND_IP:27017' }] })" >/dev/null
fi

echo "[start-backend] waiting for $BACKEND_NAME to elect a primary…" >&2
for _ in $(seq 1 30); do
  if [[ "$(mongosh --eval 'db.hello().isWritablePrimary' 2>/dev/null)" == "true" ]]; then
    echo "[start-backend] $BACKEND_NAME ready (primary at $BACKEND_IP:27017)." >&2
    exit 0
  fi
  sleep 1
done

echo "[start-backend] $BACKEND_NAME never became primary." >&2
exit 1
