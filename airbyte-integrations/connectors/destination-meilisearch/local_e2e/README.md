# Local end-to-end test with real data sources

Tests `destination-meilisearch` the way the Airbyte platform actually runs it: a real
Airbyte **source** connector's `read` output is piped straight into this destination's
`write`, against real databases.

```
Faker          ──▶ airbyte/source-faker         ──┐
Postgres       ──▶ airbyte/source-postgres      ──┤
MongoDB        ──▶ airbyte/source-mongodb-v2    ──┼── stdin ──▶ destination-meilisearch ──▶ Meilisearch v1.48
Elasticsearch  ──▶ airbyte/source-elasticsearch ──┤
Kafka/Redpanda ──▶ airbyte/source-kafka         ──┘
```

## What it covers

All three document-id modes and all three sync modes of the connector go through real pipelines:

| Step | Verifies |
| --- | --- |
| Faker sync (10k users, products, purchases) | **volume batching** (10+ flushes), nested documents, `purchases` in plain `append` mode → random `_ab_pk` |
| Postgres sync (`users`, `products`, `order_items`) | index auto-creation, natural `id` primary key, **composite PK → deterministic `_ab_pk` hash**, counts, full-text search |
| Postgres mutate + re-sync | primary-key **upsert**: updated fields replace in place, no duplicates — for both natural and hashed ids |
| MongoDB sync (`customers`) | `_id` (ObjectId hex) as primary key, search |
| MongoDB re-sync | `_id`-based dedup, stable count |
| Elasticsearch sync (`articles`) | the **ES → Meilisearch migration** path: `overwrite` mode (the ES source exposes no primary key), nested `_source` documents, search; re-migration stays duplicate-free |
| Kafka sync (`events` topic) | streaming JSON messages; the source nests payloads under `value`, so dedup runs on the **nested key** `value.event_id` → deterministic hash; a full topic re-read plus 5 new events lands exactly +5 |

Kafka source configs are generated with a fresh consumer group per run — committed
offsets would otherwise make re-runs read nothing.

Source catalogs are generated from each source's own `discover` output, like the platform does.

## Prerequisites

- Docker with Compose v2 (OrbStack works)
- `poetry install` run in the connector directory (or pass `PYTHON` pointing at any
  interpreter that has `airbyte-cdk` and `meilisearch` installed)

## Run

```bash
cd airbyte-integrations/connectors/destination-meilisearch
./local_e2e/run_e2e.sh          # leaves containers up for inspection
./local_e2e/run_e2e.sh --down   # tears everything down at the end
```

Every run starts from fresh volumes, so assertions are deterministic. While containers
are up, Meilisearch is at http://localhost:7770 (API key `e2eMasterKey`), Postgres at
localhost:55432, MongoDB at localhost:57017.
