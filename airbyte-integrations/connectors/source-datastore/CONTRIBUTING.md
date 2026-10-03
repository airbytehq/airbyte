# Contributing to source-datastore

## Overview

**source-datastore** exports entities from [Google Cloud Datastore](https://cloud.google.com/datastore/docs). Each configured Kind becomes one Airbyte stream. Schema is inferred at discovery time by sampling up to 100 entities per Kind.

## Local setup

### Prerequisites

- Python 3.11+
- A GCP service account with `roles/datastore.user` on the target project
- A `secrets/config.json` file (git-ignored) with the following shape:

```json
{
  "project_id": "my-gcp-project",
  "credentials_json": "{... full service account JSON key ...}",
  "namespace": "",
  "kinds": ["MyKind"]
}
```

### Run unit tests

```bash
cd airbyte-integrations/connectors/source-datastore
pip install -e ".[tests]"
pytest unit_tests/
```

### Run the connector locally

```bash
python main.py spec
python main.py check --config secrets/config.json
python main.py discover --config secrets/config.json
python main.py read --config secrets/config.json --catalog integration_tests/configured_catalog.json
```

### Build and run via Docker

```bash
docker build -t airbyte/source-datastore:dev .
docker run --rm airbyte/source-datastore:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-datastore:dev check --config /secrets/config.json
```

## Design notes

- **Schema inference**: `get_json_schema()` runs a `fetch(limit=100)` query against the Kind on each `discover` call. Properties observed in the sample are added to the schema; `additionalProperties: true` ensures unseen properties still flow through.
- **Incremental sync**: The cursor field is user-selected per stream in the Airbyte UI (`source_defined_cursor = False`). The connector applies a `>=` filter on the cursor property using the Datastore `PropertyFilter` API. All Datastore property types usable as a cursor (datetime, integer, string) are supported.
- **Type serialization**: `datetime` → ISO 8601 UTC string, `Key` → flat path string (`Kind/id`), `bytes` → base64 string.
- **Primary key**: `_key` (flat path of the entity key). Recommended destination mode: **Append + Dedupe** on `_key`.
