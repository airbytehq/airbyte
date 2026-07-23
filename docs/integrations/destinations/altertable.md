# Altertable

This page guides you through the process of setting up the [Altertable](https://altertable.ai) destination connector.

## Prerequisites

1. An [Altertable](https://altertable.ai) account.
2. Your lakehouse credentials (username and password) — see the [Altertable documentation](https://altertable.ai/docs/lakehouse/authentication) to retrieve them.
3. An existing catalog — see the [Altertable documentation](https://altertable.ai/docs/lakehouse/catalogs) to create one.

## Connection parameters

- **Username**
  - Your Altertable lakehouse username.
- **Password**
  - Your Altertable lakehouse password.
- **Catalog**
  - The target catalog where data will be written.
- **Schema**
  - The schema within the catalog to write data to.
- **Host** _(optional)_
  - Hostname of the Altertable Flight SQL server. Defaults to `flight.altertable.ai`.
- **Port** _(optional)_
  - Port of the Altertable Flight SQL server. Defaults to `443`.
- **Use TLS** _(optional)_
  - Whether to use TLS for the connection. Defaults to `true`. Recommended for production.

## Supported sync modes

| Sync mode                                                                                                                                     | Supported? |
| :-------------------------------------------------------------------------------------------------------------------------------------------- | :--------- |
| [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite)                   | Yes        |
| [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append)                         | Yes        |
| [Full Refresh - Overwrite + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite-deduped) | No         |
| [Incremental Sync - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append)                      | Yes        |
| [Incremental Sync - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped)    | Yes        |

## Output schema

Each stream is written to its own table within the configured catalog and schema. Columns are mapped from the source JSON schema to DuckDB types.

## Data type map

Airbyte JSON Schema types are mapped to Altertable (DuckDB) types as follows:

| Airbyte Type                                                                | Altertable Type |
| :-------------------------------------------------------------------------- | :-------------- |
| `string`                                                                    | `VARCHAR`       |
| `string` + `format: date`                                                   | `DATE`          |
| `string` + `format: date-time`                                              | `TIMESTAMPTZ`   |
| `string` + `format: date-time` + `airbyte_type: timestamp_without_timezone` | `TIMESTAMP`     |
| `string` + `format: time`                                                   | `TIME`          |
| `integer`                                                                   | `BIGINT`        |
| `number`                                                                    | `DOUBLE`        |
| `boolean`                                                                   | `BOOLEAN`       |
| `object` / `array`                                                          | `JSON`          |

## Namespace support

This destination supports [namespaces](https://docs.airbyte.com/platform/using-airbyte/core-concepts/namespaces). The namespace maps to an Altertable schema.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject         |
| :------ | :--------- | :----------- | :-------------- |
| 0.1.0   | 2026-04-10 |              | Initial release |

</details>
