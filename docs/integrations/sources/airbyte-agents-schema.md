# Airbyte Agents Schema

The **Airbyte Agents Schema** source turns Airbyte's own configuration metadata into an
[Agents Schema](https://github.com/dbt-labs/agents_schema)-shaped dataset. Point it at a single
**destination** and it enumerates every connection landing in that destination, then emits streams
describing each active stream and its physical destination table — ready to sync to Parquet, DuckDB,
or back into a warehouse `AGENTS` schema so a SQL agent can discover how Airbyte-landed data is laid
out, without any write access to the destination warehouse.

## Prerequisites

- An [Airbyte API application](https://docs.airbyte.com/using-airbyte/getting-started/api) (`client_id` + `client_secret`).
- The **destination id** (actor GUID) you want to describe. The workspace is inferred from the
  destination, so it is not a separate input.

## Setup guide

| Field | Description |
| --- | --- |
| `client_id` | Client id of your Airbyte API application. |
| `client_secret` | Client secret of your Airbyte API application. |
| `destination_id` | Actor id (GUID) of the destination to describe. |
| `host` | (Optional) Host of a Self-Managed Airbyte deployment. Leave blank for Airbyte Cloud. |

## Supported streams

| Stream | Agents Schema analog | Grain | Description |
| --- | --- | --- | --- |
| `root` | `AGENTS.ROOT` | one row per `(provider, key)` | A JSON `index` of the destination's stream/table inventory plus `skill/…` markdown guidance on how to query Airbyte-landed data. |
| `airbyte_stream` | `AGENTS.DBT_MODEL` | one row per selected stream | Logical stream identity (source, namespace, name, primary key, cursor, sync mode) plus typed `columns` (field name + JSON Schema type), sync freshness (`last_sync_status`, `last_sync_at`, `is_syncing`), and the derived physical destination table name. |

Sync these with namespace `AGENTS` to produce real `AGENTS.ROOT` / `AGENTS.AIRBYTE_STREAM` tables.

### How the catalog is read

Connection enumeration uses the Airbyte **public API** (`/connections`), scoped server-side to the
destination's workspace and filtered to the destination id. Each connection's full configured
catalog — which the public API does not expose — is then read from the Airbyte **Config API**
(`web_backend/connections/get`, the same endpoint PyAirbyte uses), authenticated with the same
bearer token. This is what supplies field-level column types and sync freshness on `airbyte_stream`.

## How the physical table name is derived

The connector never reads the destination warehouse. It derives the physical (typed final) table
name from the connection's namespace configuration:

- **schema/namespace** — `source` uses the stream namespace, `destination` uses the destination's
  default schema, `custom_format` substitutes the stream namespace into `namespaceFormat`.
- **table** — the connection `prefix` prepended to the stream name.

Final identifier casing/truncation is destination-specific (Snowflake upper-cases, BigQuery preserves
case, Postgres lower-cases) and is documented in the `root` guidance rather than applied here.

## Limitations

- Column types and freshness come from the **Config API** (`web_backend/connections/get`), which is
  Airbyte's internal API and carries no public stability contract. The public-API fields (selection,
  primary key, cursor, namespace/prefix) remain available even when the Config API is not.
- `destination_namespace` is null when a connection uses `namespaceDefinition: destination`; the
  destination's default schema is not exposed by either API.
- Incremental sync is not yet implemented. A follow-up will add a cursor on connection `updatedAt`.
- The `root` index is intentionally response-independent (dataset description + pointer to
  `AGENTS.AIRBYTE_STREAM`); the fully-paginated, authoritative per-stream/table inventory lives in
  `airbyte_stream`.

## Changelog

| Version | Date | Pull Request | Subject |
| --- | --- | --- | --- |
| 0.3.0 | 2026-07-08 | [81596](https://github.com/airbytehq/airbyte/pull/81596) | Enrich `airbyte_stream` with typed columns and sync freshness by reading each connection's configured catalog from the Config API. |
| 0.2.0 | 2026-07-15 | [81596](https://github.com/airbytehq/airbyte/pull/81596) | Scope `connections` to the destination's workspace (resolve via `destinations/{id}`) so enumeration no longer paginates the whole org; make the `root` index response-independent. |
| 0.1.0 | 2026-07-08 | | Initial release: `root` and `airbyte_stream` streams from Airbyte config metadata. |
