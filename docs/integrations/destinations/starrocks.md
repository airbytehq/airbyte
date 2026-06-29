# StarRocks

The StarRocks destination connector syncs data from Airbyte sources to [StarRocks](https://www.starrocks.io/) using the [Stream Load](https://docs.starrocks.io/docs/loading/StreamLoad/) HTTP API.

## Prerequisites

- A running StarRocks cluster (self-hosted or [CelerData Cloud](https://www.celerdata.com/))
- Network access from Airbyte to your StarRocks FE node on port 9030 (MySQL) and port 8030 (Stream Load HTTP)
- A StarRocks user with CREATE TABLE, DROP TABLE, and INSERT permissions on the target database
- The target database must already exist

## Setup guide

Create a dedicated StarRocks user for Airbyte:

```sql
CREATE USER airbyte_user IDENTIFIED BY 'your_password';
GRANT CREATE TABLE ON DATABASE your_database TO airbyte_user;
GRANT DROP ON DATABASE your_database TO airbyte_user;
GRANT INSERT ON ALL TABLES IN DATABASE your_database TO airbyte_user;
GRANT SELECT ON ALL TABLES IN DATABASE your_database TO airbyte_user;
```

## Loading modes

**Typed (recommended):** Creates tables with typed columns matching the source schema. Airbyte types map to StarRocks types (`STRING`, `BIGINT`, `DOUBLE`, `BOOLEAN`, `JSON`, `DATE`, `DATETIME`, `LARGEINT`, `DECIMAL(38,9)`). Each table includes `_airbyte_ab_id` (UUID) and `_airbyte_emitted_at` (timestamp) metadata columns. Tables use StarRocks' [UNIQUE KEY](https://docs.starrocks.io/docs/table_design/table_types/unique_table/) model — deduplication is performed on the source primary key if defined, otherwise on `_airbyte_ab_id`.

**Raw JSON:** Stores all data as JSON in a single `_airbyte_data` column. Useful when you prefer to handle transformations yourself.

## Supported sync modes

| Sync mode | Supported |
| :-------- | :-------- |
| Full Refresh - Overwrite | Yes |
| Full Refresh - Append | Yes |
| Incremental - Append | Yes |
| Incremental - Append + Deduped | Yes |
| Namespaces | No |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject |
| :------ | :--------- | :----------- | :------ |
| 0.1.0   | 2025-03-10 | [TBD](https://github.com/airbytehq/airbyte/pull/0) | Initial release |

</details>
