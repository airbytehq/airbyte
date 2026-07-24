# NebulaGraph

## Overview

The Airbyte NebulaGraph destination writes records to a NebulaGraph 3.x cluster as vertices and/or edges. Each Airbyte stream is mapped to a Nebula tag (vertex label) by default, or to an edge type when explicitly configured. Raw records are preserved in a dedicated JSON string property alongside metadata columns; optional typed columns can be provisioned based on each stream's JSON Schema.

## Sync overview

### Output schema

- Each Airbyte stream maps to a Nebula entity:
  - Vertex (default): Tag name derived as `namespace__stream` (lowercase). If the source emits no namespace, the tag name is the stream name.
  - Edge (optional): Edge type name derived as `namespace__stream` unless overridden by `edge_type` in the config.
- For every written vertex or edge, the following properties are stored:
  - `_airbyte_data` (string): the full raw JSON payload
  - `_airbyte_ab_id` (string): the Airbyte-assigned UUID per record
  - `_airbyte_emitted_at` (int64): source emission timestamp (ms epoch)
  - `_airbyte_loaded_at` (int64): destination load timestamp (ms epoch)
- Optional typed columns: If `typed.enabled` is set for a mapped stream, top-level primitive fields from the stream schema are materialized as additional properties on the tag/edge at startup. Nested objects and arrays are not typed and remain in `_airbyte_data`.

### Data type mapping

| Source (JSON Schema) | NebulaGraph property type | Notes                                  |
| :------------------- | :------------------------ | :------------------------------------- |
| string               | string                    |                                         |
| integer              | int64                     |                                         |
| number               | double                    |                                         |
| boolean              | bool                      |                                         |
| object               | —                         | kept in `_airbyte_data` only            |
| array                | —                         | kept in `_airbyte_data` only            |

### Features

| Feature                        | Supported?(Yes/No) | Notes                                                       |
| :----------------------------- | :----------------- | :---------------------------------------------------------- |
| Full Refresh Sync              | yes                |                                                             |
| Incremental - Append Sync      | yes                | Spec declares append-only destination sync mode             |
| Incremental - Append + Deduped | no                 |                                                             |
| Namespaces                     | yes                | Tag/edge names include namespace prefix when present         |

### Performance considerations

- Batched writes: In append mode, records are buffered per stream and flushed using `INSERT VERTEX/EDGE` with up to `max_batch_records` rows per batch (default 500).
- Upsert mode: If `use_upsert` is enabled, the destination performs per-record `UPSERT` statements which are safer for deduping but significantly slower than batched inserts.
- Startup-time schema: When `typed.enabled` is true for a stream, the connector performs minimal DDL at startup to add missing typed properties. There is no runtime DDL during the sync.
- VID length: Vertex IDs and edge endpoints use FIXED_STRING(N) where N is `vid_fixed_string_length` (default 128). Ensure concatenated IDs fit within this limit.

## Getting started

### Requirements

- NebulaGraph 3.x cluster reachable by Airbyte
- Graph service (`graphd`) host(s) and port(s)
- Nebula user credentials
- Optional: Permission to create a space and perform DDL if `create_space_if_missing` and typed columns are used

### Setup guide

1. Provide connection details:
   - `graphd_addresses`: Comma-separated list like `host:9669` or `node1:9669,node2:9669`.
   - `space`: Target space name. If missing and allowed, the connector will create it as `vid_type=FIXED_STRING(N)` with `N=vid_fixed_string_length`.
   - `username` and `password`.
2. Configure write behavior (optional):
   - `create_space_if_missing` (default true)
   - `vid_fixed_string_length` (default 128)
   - `vid_separator` used to concatenate VID parts (default `::`)
   - `use_upsert` (default false) for per-record UPSERTs
   - `max_batch_records` (default 500)
3. Map streams (optional but recommended):
   - By default, unmapped streams are written as vertices with VID = `_airbyte_ab_id`.
   - To control vertex IDs, set `entity_type: "vertex"` with `vid_fields` to build a VID from top-level fields using `vid_separator`.
   - To write edges, set `entity_type: "edge"` with `src_fields`, `dst_fields`, and optional `rank_field`. You may override the edge type name via `edge_type`.
   - To materialize top-level primitive fields as typed properties, set `typed.enabled: true` for that stream.

### Example configuration

```json
{
  "graphd_addresses": "graphd:9669",
  "space": "airbyte_space",
  "username": "root",
  "password": "nebula",
  "create_space_if_missing": true,
  "vid_fixed_string_length": 128,
  "vid_separator": "::",
  "use_upsert": false,
  "max_batch_records": 500,
  "streams": [
    {
      "name": "users",
      "namespace": "public",
      "entity_type": "vertex",
      "vid_fields": ["tenant_id", "user_id"],
      "typed": { "enabled": true }
    },
    {
      "name": "orders_rel",
      "namespace": "public",
      "entity_type": "edge",
      "edge_type": "public__users_to_orders",
      "src_fields": ["tenant_id", "user_id"],
      "dst_fields": ["tenant_id", "order_id"],
      "rank_field": "version",
      "typed": { "enabled": true }
    }
  ]
}
```

### Querying written data (examples)

- Fetch raw JSON for vertices of tag `public__users`:

```text
MATCH (v:`public__users`) RETURN v.`public__users`.`_airbyte_data` AS d LIMIT 10;
```

- Fetch raw JSON for edges of type `public__users_to_orders`:

```text
MATCH ()-[e:`public__users_to_orders`]->() RETURN e.`public__users_to_orders`.`_airbyte_data` AS d LIMIT 10;
```

## Known limitations

- Append-only: Overwrite and "Append + Deduped" modes are not supported.
- Deletes are not replicated.
- Only top-level primitive fields are typed; nested objects/arrays remain in `_airbyte_data`.
- SSL and SSH Tunnel are not configurable in this version.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject         |
| :------ | :--------- | :----------- | :-------------- |
| 0.1.0   | 2025-09-30 | —            | Initial release |

</details>


