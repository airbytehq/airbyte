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

say "Seeding Elasticsearch (articles) and Kafka/Redpanda (events topic)"
curl -s -X PUT "http://localhost:59200/articles" -H 'Content-Type: application/json' \
  -d '{"mappings":{"properties":{"title":{"type":"text"},"body":{"type":"text"},"author":{"properties":{"name":{"type":"keyword"},"team":{"type":"keyword"}}},"tags":{"type":"keyword"}}}}' >/dev/null
curl -s -X POST "http://localhost:59200/_bulk" -H 'Content-Type: application/x-ndjson' --data-binary '@-' >/dev/null <<'EOF'
{"index":{"_index":"articles","_id":"art-1"}}
{"title":"Getting started with Meilisearch","body":"A practical guide to instant search.","author":{"name":"Ada","team":"docs"},"tags":["search","guide"]}
{"index":{"_index":"articles","_id":"art-2"}}
{"title":"Why typo tolerance matters","body":"Users make typos. Your search should not care.","author":{"name":"Grace","team":"engineering"},"tags":["search","ux"]}
{"index":{"_index":"articles","_id":"art-3"}}
{"title":"Migrating from Elasticsearch","body":"Moving an index without downtime.","author":{"name":"Alan","team":"engineering"},"tags":["migration"]}
{"index":{"_index":"articles","_id":"art-4"}}
{"title":"Faceted navigation patterns","body":"Filters and facets for ecommerce.","author":{"name":"Margaret","team":"design"},"tags":["facets","ecommerce"]}
{"index":{"_index":"articles","_id":"art-5"}}
{"title":"Ranking rules explained","body":"How result ordering is decided.","author":{"name":"Linus","team":"engineering"},"tags":["ranking","search"]}
EOF
curl -s "http://localhost:59200/articles/_refresh" >/dev/null
ok "Elasticsearch seeded (5 articles)"

docker exec meili-dest-e2e-redpanda-1 rpk topic create events -X brokers=localhost:9092 >/dev/null 2>&1 || true
for i in $(seq 1 20); do
  echo "{\"event_id\": $i, \"type\": \"page_view\", \"page\": \"/docs/page-$i\", \"user\": \"user-$((i % 5))\", \"ts\": \"2026-07-07T10:00:$(printf %02d $i)Z\"}"
done | docker exec -i meili-dest-e2e-redpanda-1 rpk topic produce events -X brokers=localhost:9092 >/dev/null
ok "Kafka topic seeded (20 events)"

say "Generating source catalogs from 'discover' (like the Airbyte platform does)"
docker run --rm --network "$NETWORK" -v "$CFG":/cfg airbyte/source-postgres:latest \
  discover --config /cfg/pg_source_config.json 2>/dev/null > "$CFG/.pg_discover.jsonl"
docker run --rm --network "$NETWORK" -v "$CFG":/cfg airbyte/source-mongodb-v2:latest \
  discover --config /cfg/mongo_source_config.json 2>/dev/null > "$CFG/.mongo_discover.jsonl"
docker run --rm -v "$CFG":/cfg airbyte/source-faker:latest \
  discover --config /cfg/faker_source_config.json 2>/dev/null > "$CFG/.faker_discover.jsonl"
docker run --rm --network "$NETWORK" -v "$CFG":/cfg airbyte/source-elasticsearch:latest \
  discover --config /cfg/es_source_config.json 2>/dev/null > "$CFG/.es_discover.jsonl"
# Kafka configs are generated with per-run consumer groups so every sync reads
# the topic from the beginning (committed offsets would otherwise make re-runs empty).
python3 - "$CFG" <<'EOF'
import json, sys, time
cfg = sys.argv[1]
base = {
    "bootstrap_servers": "redpanda:9092",
    "subscription": {"subscription_type": "subscribe", "topic_pattern": "events"},
    "protocol": {"security_protocol": "PLAINTEXT"},
    "MessageFormat": {"deserialization_type": "JSON"},
    "test_topic": "events",
    "client_id": "airbyte-e2e-client",
    "client_dns_lookup": "use_all_dns_ips",
    "enable_auto_commit": False,
    "auto_commit_interval_ms": 5000,
    "retry_backoff_ms": 100,
    "request_timeout_ms": 30000,
    "receive_buffer_bytes": 32768,
    "max_poll_records": 500,
    "polling_time": 3000,
    "auto_offset_reset": "earliest",
    "repeated_calls": 3,
    "max_records_process": 100000,
}
run_id = int(time.time())
for n in (1, 2):
    with open(f"{cfg}/kafka_source_config_{n}.json", "w") as f:
        json.dump({**base, "group_id": f"airbyte-e2e-{run_id}-{n}"}, f, indent=2)
EOF
docker run --rm --network "$NETWORK" -v "$CFG":/cfg airbyte/source-kafka:latest \
  discover --config /cfg/kafka_source_config_1.json 2>/dev/null > "$CFG/.kafka_discover.jsonl"
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
pg_pks = {"users": [["id"]], "products": [["id"]], "order_items": [["order_id"], ["product_id"]]}
with open(f"{cfg}/pg_source_catalog.json", "w") as f:
    json.dump({"streams": [
        {"stream": pg[n], "sync_mode": "full_refresh", "destination_sync_mode": "append", "primary_key": pk}
        for n, pk in pg_pks.items()
    ]}, f, indent=2)

mongo = catalog_from(f"{cfg}/.mongo_discover.jsonl")
with open(f"{cfg}/mongo_source_catalog.json", "w") as f:
    json.dump({"streams": [
        {"stream": mongo["customers"], "sync_mode": "full_refresh", "destination_sync_mode": "append",
         "primary_key": [["_id"]]}
    ]}, f, indent=2)

faker = catalog_from(f"{cfg}/.faker_discover.jsonl")
with open(f"{cfg}/faker_source_catalog.json", "w") as f:
    json.dump({"streams": [
        {"stream": faker[n], "sync_mode": "full_refresh", "destination_sync_mode": "append", "primary_key": [["id"]]}
        for n in ("users", "products", "purchases")
    ]}, f, indent=2)

es = catalog_from(f"{cfg}/.es_discover.jsonl")
with open(f"{cfg}/es_source_catalog.json", "w") as f:
    json.dump({"streams": [
        {"stream": es["articles"], "sync_mode": "full_refresh", "destination_sync_mode": "overwrite", "primary_key": []}
    ]}, f, indent=2)

kafka = catalog_from(f"{cfg}/.kafka_discover.jsonl")
with open(f"{cfg}/kafka_source_catalog.json", "w") as f:
    json.dump({"streams": [
        {"stream": kafka["events"], "sync_mode": "full_refresh", "destination_sync_mode": "append", "primary_key": []}
    ]}, f, indent=2)
print("  catalogs written")
EOF

# --------------------------------------------------------------------------
say "Sync 0: Faker (10k users, 100 products, purchases) -> volume/batching test"
states=$(run_sync airbyte/source-faker:latest faker_source_config.json faker_source_catalog.json dest_catalog_faker.json)
ok "sync completed ($states state checkpoints)"

assert_eq "faker users count (10 batch flushes)" "10000" "$(meili '/indexes/users/documents?limit=0' | json "d['total']")"
assert_eq "faker products count" "100" "$(meili '/indexes/products/documents?limit=0' | json "d['total']")"
assert_eq "purchases index primaryKey (append mode -> synthetic)" "_ab_pk" "$(meili /indexes/purchases | json "d['primaryKey']")"
purchases=$(meili '/indexes/purchases/documents?limit=0' | json "d['total']")
if [ "$purchases" -gt 0 ]; then ok "purchases synced via random _ab_pk ($purchases docs)"; else bad "purchases empty"; fi
# Faker stream names collide with the Postgres tables on purpose-neutral names;
# clear them so the Postgres phase starts from clean indexes.
for idx in users products purchases; do
  curl -s -X DELETE -H "$AUTH" "$MEILI_URL/indexes/$idx" >/dev/null
done
ok "faker indexes cleared for the Postgres phase"

say "Sync 1: Postgres (users, products, order_items) -> Meilisearch [append_dedup]"
states=$(run_sync airbyte/source-postgres:latest pg_source_config.json pg_source_catalog.json dest_catalog_pg.json)
ok "sync completed ($states state checkpoints)"

assert_eq "users index primaryKey" "id" "$(meili /indexes/users | json "d['primaryKey']")"
assert_eq "users document count" "5" "$(meili '/indexes/users/documents?limit=0' | json "d['total']")"
assert_eq "products document count" "6" "$(meili '/indexes/products/documents?limit=0' | json "d['total']")"
assert_eq "order_items primaryKey (composite -> hash)" "_ab_pk" "$(meili /indexes/order_items | json "d['primaryKey']")"
assert_eq "order_items document count" "8" "$(meili '/indexes/order_items/documents?limit=0' | json "d['total']")"
hit=$(curl -s -H "$AUTH" -H 'Content-Type: application/json' "$MEILI_URL/indexes/products/search" \
  -d '{"q":"keyboard"}' | json "d['hits'][0]['title'] if d['hits'] else 'NO HIT'")
assert_eq "full-text search 'keyboard'" "Mechanical Keyboard" "$hit"

say "Sync 2: mutate Postgres, re-sync, verify upserts (no duplicates)"
docker exec meili-dest-e2e-postgres-1 psql -q -U postgres -d sales -c \
  "UPDATE users SET city='Paris' WHERE id=1;
   INSERT INTO users (name,email,city,signup_date) VALUES ('Barbara Liskov','barbara@example.com','Cambridge MA','2024-06-01');
   UPDATE order_items SET quantity=99 WHERE order_id=1 AND product_id=1;"
run_sync airbyte/source-postgres:latest pg_source_config.json pg_source_catalog.json dest_catalog_pg.json >/dev/null
assert_eq "user 1 city updated in place" "Paris" "$(meili /indexes/users/documents/1 | json "d['city']")"
assert_eq "users count after upsert (+1 new, no dupes)" "6" "$(meili '/indexes/users/documents?limit=0' | json "d['total']")"
assert_eq "products count unchanged" "6" "$(meili '/indexes/products/documents?limit=0' | json "d['total']")"
assert_eq "order_items count unchanged (hash id is stable)" "8" \
  "$(meili '/indexes/order_items/documents?limit=0' | json "d['total']")"
assert_eq "order_items (1,1) quantity updated via hash upsert" "99" \
  "$(meili '/indexes/order_items/documents?limit=100' | json "[x for x in d['results'] if x['order_id']==1 and x['product_id']==1][0]['quantity']")"

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

say "Sync 5: Elasticsearch (articles) -> Meilisearch [overwrite, ES migration]"
run_sync airbyte/source-elasticsearch:latest es_source_config.json es_source_catalog.json dest_catalog_es.json >/dev/null
assert_eq "articles document count" "5" "$(meili '/indexes/articles/documents?limit=0' | json "d['total']")"
hit=$(curl -s -H "$AUTH" -H 'Content-Type: application/json' "$MEILI_URL/indexes/articles/search" \
  -d '{"q":"typo"}' | json "d['hits'][0]['title'] if d['hits'] else 'NO HIT'")
assert_eq "search 'typo' over migrated ES docs" "Why typo tolerance matters" "$hit"
run_sync airbyte/source-elasticsearch:latest es_source_config.json es_source_catalog.json dest_catalog_es.json >/dev/null
assert_eq "articles count after re-migration (overwrite, no dupes)" "5" \
  "$(meili '/indexes/articles/documents?limit=0' | json "d['total']")"

say "Sync 6: Kafka (events topic) -> Meilisearch [append_dedup on nested event_id]"
run_sync airbyte/source-kafka:latest kafka_source_config_1.json kafka_source_catalog.json dest_catalog_kafka.json >/dev/null
assert_eq "events index primaryKey (nested key -> hash)" "_ab_pk" "$(meili /indexes/events | json "d['primaryKey']")"
assert_eq "events document count" "20" "$(meili '/indexes/events/documents?limit=0' | json "d['total']")"
for i in 21 22 23 24 25; do
  echo "{\"event_id\": $i, \"type\": \"click\", \"page\": \"/pricing\", \"user\": \"user-$((i % 5))\", \"ts\": \"2026-07-07T11:00:$i Z\"}"
done | docker exec -i meili-dest-e2e-redpanda-1 rpk topic produce events -X brokers=localhost:9092 >/dev/null
run_sync airbyte/source-kafka:latest kafka_source_config_2.json kafka_source_catalog.json dest_catalog_kafka.json >/dev/null
assert_eq "events count after full re-read (+5 new, hash dedup)" "25" \
  "$(meili '/indexes/events/documents?limit=0' | json "d['total']")"

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
