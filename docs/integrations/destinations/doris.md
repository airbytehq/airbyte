# Doris

destination-doris is a destination connector that loads data into [Apache Doris](https://doris.apache.org/) using [Stream Load](https://doris.apache.org/docs/data-operate/import/stream-load-manual). It uses the Airbyte Bulk CDK with batch aggregation and HTTP PUT requests for efficient data ingestion.

## Sync overview

### Output schema

Each stream will be output into its own table in Doris. The table schema is derived from the source schema, with each source field mapped to a corresponding Doris column. In addition, each table includes the following Airbyte metadata columns:

- `_airbyte_raw_id`: A UUID assigned by Airbyte to each record. Column type: `VARCHAR(40)`.
- `_airbyte_extracted_at`: A timestamp representing when the record was extracted from the source. Column type: `DATETIME(3)`.
- `_airbyte_meta`: A JSON string containing sync metadata (sync ID, field-level changes). Column type: `STRING`.
- `_airbyte_generation_id`: An integer identifying the generation of the sync. Column type: `BIGINT`.

### Type mapping

| Airbyte Type                    | Doris Type     |
| :------------------------------ | :------------- |
| Boolean                         | BOOLEAN        |
| Integer                         | BIGINT         |
| Number                          | DECIMAL(38, 9) |
| String                          | STRING         |
| Date                            | DATE           |
| Timestamp (with/without tz)     | DATETIME(3)    |
| Time (with/without tz)          | STRING         |
| Object                          | JSON           |
| Array                           | JSON           |
| Union / Unknown                 | STRING         |

### Features

| Feature                         | Supported | Notes                                                  |
| :------------------------------ | :-------- | :----------------------------------------------------- |
| Full Refresh - Overwrite        | Yes       | Uses DUPLICATE KEY model with temp table + rename      |
| Full Refresh - Append           | Yes       | Uses DUPLICATE KEY model                               |
| Incremental - Append            | Yes       | Uses DUPLICATE KEY model                               |
| Incremental - Append + Deduped  | Yes       | Uses UNIQUE KEY model for automatic deduplication      |
| Schema Evolution                | Yes       | Supports adding, modifying, and dropping columns       |
| Configurable Batch Size         | Yes       | Batch rows, bytes, flush interval are user-configurable|

### Performance considerations

Data is written to Doris using [Stream Load](https://doris.apache.org/docs/data-operate/import/stream-load-manual) via HTTP PUT requests with JSON format. The connector accumulates records into batches before flushing, which can be tuned via the Advanced configuration parameters:

- **Batch Max Rows**: Maximum records per batch (default: 100,000)
- **Batch Max Bytes**: Maximum bytes per batch (default: 50 MB)
- **Batch Flush Interval**: Maximum idle time before a batch is flushed (default: 10,000 ms)
- **Enable Gzip**: Optional gzip compression to reduce network transfer size

Each Stream Load request is assigned a unique label for idempotency. Failed requests are retried up to 3 times with exponential backoff.

## Getting started

### Requirements

- Apache Doris version 2.0 or above
- The Doris FE HTTP port (default 8030) must be accessible from Airbyte
- The Doris FE MySQL protocol port (default 9030) must be accessible from Airbyte
- A Doris user with permissions to create databases, tables, and execute Stream Load

### Setup guide

#### Connection parameters

| Parameter    | Description                                           | Default |
| :----------- | :---------------------------------------------------- | :------ |
| Host         | Hostname or IP address of the Doris FE node           |         |
| HTTP Port    | HTTP port of the FE node for Stream Load              | 8030    |
| Query Port   | MySQL protocol port of the FE node for DDL operations | 9030    |
| Database     | Name of the target Doris database                     |         |
| Username     | Doris username                                        | root    |
| Password     | Doris password                                        |         |

#### Advanced parameters

| Parameter              | Description                                                 | Default    |
| :--------------------- | :---------------------------------------------------------- | :--------- |
| Batch Max Rows         | Maximum number of records per batch before flushing         | 100,000    |
| Batch Max Bytes        | Maximum size in bytes per batch before flushing             | 50,000,000 |
| Batch Flush Interval   | Maximum time in milliseconds before a batch is flushed      | 10,000     |
| Flush Queue Size       | Maximum buffered batches before applying backpressure       | 5          |
| Enable Gzip            | Compress data with gzip before sending to Doris             | false      |

### Table models

- **Append / Overwrite modes**: Tables are created with `DUPLICATE KEY` model using `_airbyte_raw_id` as the key and `DISTRIBUTED BY HASH(_airbyte_raw_id) BUCKETS AUTO`.
- **Deduped mode**: Tables are created with `UNIQUE KEY` model using the configured primary key columns and `DISTRIBUTED BY HASH` on the first primary key column.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                    |
| :------ | :--------- | :------------------------------------------------------- | :--------------------------------------------------------- |
| 0.2.0   | 2026-04-13 |                                                          | Rewrite with Bulk CDK: structured schema, dedup, batch config |
| 0.1.0   | 2022-11-14 | [17884](https://github.com/airbytehq/airbyte/pull/17884) | Initial Commit                                             |

</details>
