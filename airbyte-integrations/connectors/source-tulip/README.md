# Source Tulip — Airbyte Connector

Airbyte source connector that syncs data from [Tulip](https://tulip.co) Tables into any Airbyte destination.

## Features

- **Multi-table sync** — Automatically discovers all Tulip tables and exposes each as an independently selectable stream.
- **Dynamic schema discovery** — Schemas are fetched live from the Tulip API on every discover run. Adding or removing columns in Tulip is reflected immediately.
- **Incremental sync** — Two-phase sync strategy (BOOTSTRAP then INCREMENTAL) using `_sequenceNumber` as the primary cursor. A 60-second `_updatedAt` lookback window prevents data loss from late commits.
- **Cursor-based pagination** — Uses `_sequenceNumber > last_value` instead of offset pagination, which is reliable even when data is being inserted concurrently.
- **tableLink exclusion** — Automatically excludes `tableLink` fields from API requests to reduce database load on the Tulip API.
- **Snowflake-friendly column names** — Custom fields are named `label__id` (e.g., `customer_name__rqoqm`) for readability and uniqueness.

## Configuration

| Field                | Required | Description                                                           |
| -------------------- | -------- | --------------------------------------------------------------------- |
| `subdomain`          | Yes      | Your Tulip instance subdomain (e.g., `acme` for `acme.tulip.co`)      |
| `api_key`            | Yes      | Tulip API key with `tables:read` scope                                |
| `api_secret`         | Yes      | Tulip API secret                                                      |
| `workspace_id`       | No       | Workspace ID for workspace-scoped table access                        |
| `sync_from_date`     | No       | ISO 8601 timestamp (`YYYY-MM-DDTHH:MM:SSZ`) to limit the initial sync |
| `custom_filter_json` | No       | JSON array of Tulip API filter objects applied to every request       |

### Authentication Setup

1. Log in to your Tulip instance.
2. Navigate to **Account Settings > API Tokens**.
3. Create a new API token with the **tables:read** scope.
4. Copy the API Key and API Secret into the connector configuration.

For workspace-scoped access, also provide the Workspace ID (found in your Tulip workspace settings URL).

## Type Mapping

| Tulip Type  | JSON Schema Type               |
| ----------- | ------------------------------ |
| `integer`   | `integer`                      |
| `float`     | `number`                       |
| `boolean`   | `boolean`                      |
| `timestamp` | `string` (format: `date-time`) |
| `datetime`  | `string` (format: `date-time`) |
| `interval`  | `integer`                      |
| `user`      | `string`                       |
| `tableLink` | _excluded_                     |
| All others  | `string`                       |

All fields are nullable (`["null", "<type>"]`).

### System Fields

Every stream includes these system fields:

| Field             | Type      | Description                     |
| ----------------- | --------- | ------------------------------- |
| `id`              | string    | Primary key                     |
| `_createdAt`      | date-time | Record creation timestamp       |
| `_updatedAt`      | date-time | Last update timestamp           |
| `_sequenceNumber` | integer   | Monotonically increasing cursor |

## Sync Modes

### Full Refresh

Reads all records from each selected table.

### Incremental

Uses a two-phase strategy:

1. **BOOTSTRAP** — Fetches all historical records ordered by `_sequenceNumber`. Completes when a batch returns fewer than 100 records.
2. **INCREMENTAL** — Fetches new and updated records using `_updatedAt > (last_updated_at - 60s)`. The 60-second lookback window catches records committed during the previous sync. `_sequenceNumber` is only used for pagination within a single sync run.

State is checkpointed every 500 records. The `_updatedAt` cursor is frozen during a sync and only advanced after successful completion, preventing data loss on interruption.

## Development

### Prerequisites

- Python 3.9+
- A Tulip instance with API credentials

### Setup

```bash
python -m venv .venv_airbyte
source .venv_airbyte/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

### Running Locally

```bash
# Output the connector spec
python main.py spec

# Test connection
python main.py check --config secrets/config.json

# Discover available tables
python main.py discover --config secrets/config.json

# Read data
python main.py read --config secrets/config.json --catalog integration_tests/configured_catalog.json
```

### Testing

```bash
# Unit tests (no API access needed)
pytest unit_tests/ -v

# Integration tests (requires secrets/config.json with valid credentials)
pytest integration_tests/acceptance.py -v
```

### Docker

```bash
docker build -t airbyte/source-tulip:dev .
docker run --rm airbyte/source-tulip:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-tulip:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-tulip:dev discover --config /secrets/config.json
```

## Project Structure

```
source_tulip/
  __init__.py           # Package exports
  source.py             # SourceTulip — check_connection, streams discovery
  streams.py            # TulipTableStream — data reading, pagination, incremental sync
  utils.py              # Column naming, type mapping, field mapping, record transform
  spec.yaml             # Connector configuration schema
  schemas/.gitkeep      # Empty — schemas are dynamic
unit_tests/             # 100 unit tests
integration_tests/      # 9 acceptance tests (live API)
main.py                 # Entry point
Dockerfile              # Container image
```
