#!/usr/bin/env bash
# Drop every non-system database on the source-mongodb-v2 e2e backend.
# Used by run.sh --reset=fixture before a second comparison sweep.
#
# Env:
#   BACKEND_NAME        container name (default: source-mongodb-v2-db-backend)
set -euo pipefail

BACKEND_NAME="${BACKEND_NAME:-source-mongodb-v2-db-backend}"

echo "[reset-databases] dropping non-system databases on $BACKEND_NAME" >&2
docker exec -i "$BACKEND_NAME" mongosh --quiet --eval '
  const system = new Set(["admin", "local", "config"]);
  db.adminCommand({ listDatabases: 1, nameOnly: true }).databases
    .map((d) => d.name)
    .filter((name) => !system.has(name))
    .forEach((name) => {
      db.getSiblingDB(name).dropDatabase();
      print(`[reset-databases] dropped ${name}`);
    });
' >&2
