#!/usr/bin/env bash
#
# End-to-end test for destination-meilisearch using REAL Airbyte source connectors.
#
# Pipeline under test (exactly how the Airbyte platform wires connectors):
#   docker run airbyte/source-postgres   read ... | python main.py write ...
#   docker run airbyte/source-mongodb-v2 read ... | python main.py write ...
#
# It seeds Postgres and MongoDB, syncs them into Meilisearch, verifies documents
# and search results, then mutates Postgres and re-syncs to verify primary-key
# upserts (no duplicates, updated fields).
#
# Requirements: docker (compose v2), python3, curl, and the connector's Python
# environment (run `poetry install` in the connector directory first).
#
# Usage:
#   ./local_e2e/run_e2e.sh            # full run, leaves containers up
#   ./local_e2e/run_e2e.sh --down     # full run, tears everything down at the end
#   PYTHON="path/to/python" ./local_e2e/run_e2e.sh   # custom interpreter
#
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONNECTOR_DIR="$(dirname "$HERE")"
CFG="$HERE/config"
PYTHON="${PYTHON:-poetry run python}"

MEILI_URL="http://localhost:7770"
MEILI_KEY="e2eMasterKey"
AUTH="Authorization: Bearer $MEILI_KEY"
NETWORK="meili-dest-e2e_default"

PASS=0
FAIL=0

say()  { printf '\n\033[1;34m== %s ==\033[0m\n' "$*"; }
ok()   { printf '\033[32m  PASS\033[0m %s\n' "$*"; PASS=$((PASS+1)); }
bad()  { printf '\033[31m  FAIL\033[0m %s\n' "$*"; FAIL=$((FAIL+1)); }

assert_eq() { # desc expected actual
  if [ "$2" = "$3" ]; then ok "$1 (= $2)"; else bad "$1 (expected '$2', got '$3')"; fi
}

meili() { # path -> body
  curl -s -H "$AUTH" "$MEILI_URL$1"
}

json() { # jq-lite: json 'expr reading data from stdin as d'
  python3 -c "import sys,json; d=json.load(sys.stdin); print($1)"
}

run_sync() { # source_image source_config source_catalog dest_catalog
  docker run --rm -i --network "$NETWORK" -v "$CFG":/cfg "$1" \
    read --config "/cfg/$2" --catalog "/cfg/$3" 2>/dev/null \
    | (cd "$CONNECTOR_DIR" && $PYTHON main.py write --config "$CFG/dest_config.json" --catalog "$CFG/$4") \
    | grep -cE '"type":"STATE"' || true
}

# --------------------------------------------------------------------------
say "Starting fresh infrastructure (postgres, mongodb, meilisearch)"
cd "$HERE"
docker compose down -v --remove-orphans >/dev/null 2>&1 || true
docker compose up -d --wait

say "Initializing MongoDB replica set and seed data"
docker exec meili-dest-e2e-mongodb-1 mongosh --quiet --eval \
  'try { rs.status().ok } catch(e) { rs.initiate({_id:"rs0",members:[{_id:0,host:"mongodb:27017"}]}).ok }' >/dev/null
sleep 3
docker exec meili-dest-e2e-mongodb-1 mongosh --quiet --eval '
db = db.getSiblingDB("sales");
db.customers.drop();
db.customers.insertMany([
  {name: "Acme Corp",   tier: "enterprise", country: "US", seats: 250},
  {name: "Globex",      tier: "startup",    country: "DE", seats: 12},
  {name: "Initech",     tier: "growth",     country: "FR", seats: 48},
  {name: "Umbrella SA", tier: "enterprise", country: "ES", seats: 300},
]);' >/dev/null
ok "MongoDB seeded (4 customers)"

say "Generating source catalogs from 'discover' (like the Airbyte platform does)"
docker run --rm --network "$NETWORK" -v "$CFG":/cfg airbyte/source-postgres:latest \
  discover --config /cfg/pg_source_config.json 2>/dev/null > "$CFG/.pg_discover.jsonl"
docker run --rm --network "$NETWORK" -v "$CFG":/cfg airbyte/source-mongodb-v2:latest \
  discover --config /cfg/mongo_source_config.json 2>/dev/null > "$CFG/.mongo_discover.jsonl"
python3 - "$CFG" <<'EOF'
import json, sys
cfg = sys.argv[1]

def catalog_from(path):
    with open(path) as f:
        for line in f:
            try: m = json.loads(line)
            except json.JSONDecodeError: continue
            if m.get("type") == "CATALOG":
                return {s["name"]: s for s in m["catalog"]["streams"]}
    raise SystemExit(f"no CATALOG message in {path}")

pg = catalog_from(f"{cfg}/.pg_discover.jsonl")
with open(f"{cfg}/pg_source_catalog.json", "w") as f:
    json.dump({"streams": [
        {"stream": pg[n], "sync_mode": "full_refresh", "destination_sync_mode": "append", "primary_key": [["id"]]}
        for n in ("users", "products")
    ]}, f, indent=2)

mongo = catalog_from(f"{cfg}/.mongo_discover.jsonl")
with open(f"{cfg}/mongo_source_catalog.json", "w") as f:
    json.dump({"streams": [
        {"stream": mongo["customers"], "sync_mode": "full_refresh", "destination_sync_mode": "append",
         "primary_key": [["_id"]]}
    ]}, f, indent=2)
print("  catalogs written")
EOF

# --------------------------------------------------------------------------
say "Sync 1: Postgres (users, products) -> Meilisearch [append_dedup, natural PK]"
states=$(run_sync airbyte/source-postgres:latest pg_source_config.json pg_source_catalog.json dest_catalog_pg.json)
ok "sync completed ($states state checkpoints)"

assert_eq "users index primaryKey" "id" "$(meili /indexes/users | json "d['primaryKey']")"
assert_eq "users document count" "5" "$(meili '/indexes/users/documents?limit=0' | json "d['total']")"
assert_eq "products document count" "6" "$(meili '/indexes/products/documents?limit=0' | json "d['total']")"
hit=$(curl -s -H "$AUTH" -H 'Content-Type: application/json' "$MEILI_URL/indexes/products/search" \
  -d '{"q":"keyboard"}' | json "d['hits'][0]['title'] if d['hits'] else 'NO HIT'")
assert_eq "full-text search 'keyboard'" "Mechanical Keyboard" "$hit"

say "Sync 2: mutate Postgres, re-sync, verify upsert (no duplicates)"
docker exec meili-dest-e2e-postgres-1 psql -q -U postgres -d sales -c \
  "UPDATE users SET city='Paris' WHERE id=1;
   INSERT INTO users (name,email,city,signup_date) VALUES ('Barbara Liskov','barbara@example.com','Cambridge MA','2024-06-01');"
run_sync airbyte/source-postgres:latest pg_source_config.json pg_source_catalog.json dest_catalog_pg.json >/dev/null
assert_eq "user 1 city updated in place" "Paris" "$(meili /indexes/users/documents/1 | json "d['city']")"
assert_eq "users count after upsert (+1 new, no dupes)" "6" "$(meili '/indexes/users/documents?limit=0' | json "d['total']")"
assert_eq "products count unchanged" "6" "$(meili '/indexes/products/documents?limit=0' | json "d['total']")"

say "Sync 3: MongoDB (customers) -> Meilisearch [append_dedup on _id]"
run_sync airbyte/source-mongodb-v2:latest mongo_source_config.json mongo_source_catalog.json dest_catalog_mongo.json >/dev/null
assert_eq "customers index primaryKey" "_id" "$(meili /indexes/customers | json "d['primaryKey']")"
assert_eq "customers document count" "4" "$(meili '/indexes/customers/documents?limit=0' | json "d['total']")"
hits=$(curl -s -H "$AUTH" -H 'Content-Type: application/json' "$MEILI_URL/indexes/customers/search" \
  -d '{"q":"enterprise"}' | json "len(d['hits'])")
assert_eq "search 'enterprise' hit count" "2" "$hits"

say "Sync 4: MongoDB re-sync, verify _id-based dedup"
run_sync airbyte/source-mongodb-v2:latest mongo_source_config.json mongo_source_catalog.json dest_catalog_mongo.json >/dev/null
assert_eq "customers count after re-sync (no dupes)" "4" "$(meili '/indexes/customers/documents?limit=0' | json "d['total']")"

# --------------------------------------------------------------------------
say "Result: $PASS passed, $FAIL failed"
if [ "${1:-}" = "--down" ]; then
  docker compose down -v --remove-orphans >/dev/null
  echo "  infrastructure torn down"
else
  echo "  containers left running (Meilisearch UI data: $MEILI_URL, key: $MEILI_KEY)"
  echo "  tear down with: docker compose -f $HERE/compose.yaml down -v"
fi
[ "$FAIL" -eq 0 ]
