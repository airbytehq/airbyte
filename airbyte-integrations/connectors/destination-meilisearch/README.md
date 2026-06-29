# Meilisearch Destination

This is the repository for the Meilisearch destination connector, written in Python.
For information about how to use this connector within Airbyte, see
[the documentation](https://docs.airbyte.com/integrations/destinations/meilisearch).

## What it does

Each stream is synced to its own Meilisearch index (index uid = stream name with any
character outside `[a-zA-Z0-9_-]` replaced by `_`). The connector supports:

- **Batch updates** — records are buffered and flushed in batches (configurable via
  `batch_size`), one Meilisearch indexing task per batch.
- **Primary-key upsert / dedup** — for `append_dedup`, the stream's primary key is used
  as the Meilisearch index primary key so records upsert natively on their real key.
- **Partial updates** — set `update_method` to `merge` to update only the fields present
  in each record (`update_documents`), preserving other stored fields. The default
  `replace` fully overwrites matching documents (`add_documents`).

### Sync modes

| Destination sync mode | Behavior                                                                 |
| --------------------- | ------------------------------------------------------------------------ |
| `overwrite`           | Deletes and recreates the index each sync.                               |
| `append`              | Adds every record with a unique generated id (history preserved).        |
| `append_dedup`        | Upserts on the stream primary key (replace, or merge if configured).     |

### Primary key handling

- A single, top-level source primary key (e.g. `id`) is used directly as the Meilisearch
  index primary key, so documents stay clean and Meilisearch dedups natively.
  **Its values must be an integer or a string of only `[a-zA-Z0-9_-]`** (a Meilisearch
  constraint); non-conforming values fail the indexing task.
- A composite or nested key, or a stream with no key, falls back to a synthetic `_ab_pk`
  field — a deterministic hash of the key values, or a random UUID when there is no key.

## Local development

### Prerequisites

- Python `>=3.10,<3.12`
- [Poetry](https://python-poetry.org/)

### Installing

```bash
poetry install --no-root
```

### Configuration

The connector takes a JSON config:

```json
{
  "host": "http://localhost:7700",
  "api_key": "your-meilisearch-api-key",
  "batch_size": 1000,
  "update_method": "replace"
}
```

`api_key` may be omitted if the Meilisearch instance has no master key.

### Running locally

```bash
poetry run destination-meilisearch spec
poetry run destination-meilisearch check --config secrets/config.json
cat messages.jsonl | poetry run destination-meilisearch write --config secrets/config.json --catalog sample_files/configured_catalog.json
```

### Tests

Unit tests (no external dependencies):

```bash
poetry run pytest unit_tests
```

Integration tests require a running Meilisearch instance and a `secrets/config.json`:

```bash
docker run -d -p 7700:7700 -e MEILI_MASTER_KEY=masterKey getmeili/meilisearch:v1.48
poetry run pytest integration_tests
```
