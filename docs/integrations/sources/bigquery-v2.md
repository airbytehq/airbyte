---
description: >-
  BigQuery is a fully managed, highly scalable, and cost-effective data warehouse
  offered by Google Cloud.
---

# BigQuery (v2)

The BigQuery (v2) source connector reads tables, views, materialized views, external tables and table snapshots from Google BigQuery datasets. It supports full refresh and incremental syncs, discovers nested `STRUCT` and `ARRAY` schemas and primary key constraints, checkpoints its progress so that large tables resume after an interruption, and can read through the BigQuery Storage Read API for high throughput.

This connector is the successor of the [BigQuery](bigquery.md) source, rebuilt on Airbyte's Bulk CDK. It accepts the same configuration properties. See [Differences from the BigQuery (legacy) source](#differences-from-the-bigquery-legacy-source) for what changed.

## Features

| Feature                   | Supported | Notes                                                            |
| :------------------------ | :-------- | :--------------------------------------------------------------- |
| Full refresh sync         | Yes       |                                                                  |
| Incremental sync - append | Yes       | Cursor based, see [Incremental sync](#incremental-sync)          |
| Change data capture (CDC) | No        | BigQuery has no change log for the connector to read             |
| Namespaces                | Yes       | Each dataset is a namespace                                      |
| Primary keys              | Yes       | Read from the table's `PRIMARY KEY` constraint                   |
| Nested schemas            | Yes       | `STRUCT` and `ARRAY` columns keep their structure in the catalog |
| Storage Read API          | Optional  | See [Read throughput](#read-throughput)                          |
| SSL                       | Yes       | All traffic to the BigQuery API uses HTTPS                       |

The connector is read-only. It runs `SELECT` queries and metadata reads and never writes to your project.

## Getting started

### Requirements

- A Google Cloud project with the BigQuery API enabled.
- A service account with read access to the datasets to sync and permission to run query jobs.
- A JSON key for that service account.

### Service account

Create a dedicated service account for Airbyte by following Google's [Create service accounts](https://cloud.google.com/iam/docs/service-accounts-create) guide, then grant it the following roles. Using a dedicated account keeps permissions and auditing simple.

| Role                                                          | Where to grant it                                                                               | Why                                                           |
| :------------------------------------------------------------ | :---------------------------------------------------------------------------------------------- | :------------------------------------------------------------ |
| BigQuery Data Viewer (`roles/bigquery.dataViewer`)            | The project, or each dataset to sync                                                            | Lists datasets and tables, reads table schemas and table data |
| BigQuery Job User (`roles/bigquery.jobUser`)                  | The project that runs the query jobs (**Project ID**, or **Job Execution Project ID** when set) | Runs the `SELECT` queries                                     |
| BigQuery Read Session User (`roles/bigquery.readSessionUser`) | The project that runs the query jobs                                                            | Only when **Use the BigQuery Storage Read API** is turned on  |

The permissions the connector uses are `bigquery.datasets.get`, `bigquery.tables.list`, `bigquery.tables.get`, `bigquery.tables.getData` and `bigquery.jobs.create`, plus `bigquery.readsessions.create` and `bigquery.readsessions.getData` for the Storage Read API.

### Service account key

Follow Google's [Create and delete service account keys](https://cloud.google.com/iam/docs/keys-create-delete) guide and choose the JSON key type. Download the key file: you paste its contents into the **Service Account Key JSON** field. Google shows the key only once, so keep the file until the source is set up, then delete it from your computer.

### Set up the BigQuery source in Airbyte

1. In the Airbyte UI, click **Sources** and then **+ New source**.
2. Select **BigQuery** from the source type list.
3. Fill in the connection fields:

| Field                                  | Required | Description                                                                                                                                                                                                                                          |
| :------------------------------------- | :------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Project ID**                         | Yes      | The Google Cloud project that owns the datasets to read.                                                                                                                                                                                             |
| **Dataset ID**                         | No       | Restricts the source to one dataset. Leave it empty to discover every dataset of the project. Set it on projects with a large number of datasets, because discovery lists every table of every dataset it can see.                                   |
| **Service Account Key JSON**           | Yes      | The contents of the JSON key file.                                                                                                                                                                                                                   |
| **Job Execution Project ID**           | No       | Advanced. The project that runs, and is billed for, the query jobs. Use it to keep Airbyte's query quota and cost apart from the data project, or to read from a project where the service account only has data access. Defaults to **Project ID**. |
| **Max Concurrent Queries to Database** | No       | Advanced. How many tables the connector reads at the same time. Leave it empty to let Airbyte choose.                                                                                                                                                |
| **Use the BigQuery Storage Read API**  | No       | Advanced, off by default. Streams query results through the Storage Read API instead of paging them through the REST API. See [Read throughput](#read-throughput).                                                                                   |

4. Click **Set up source**. The connection test lists the datasets and their tables and runs a trivial query. It fails with `Discovered zero tables` when the dataset, or the whole project, contains no tables.

## Replication

### Discovered streams

Every dataset is a namespace and every table, view, materialized view, external table and table snapshot in it is a stream. BigQuery ML models are skipped, as are tables without columns. Column names and types come from the table metadata, including the nested fields of `STRUCT` columns and the element type of `ARRAY` columns. A table with a `PRIMARY KEY` constraint, which BigQuery declares but does not enforce, reports it as the source-defined primary key.

### Full refresh

A full refresh reads every row of the stream with one ordered query per table. Streams with a primary key are read in primary key order and checkpoint their position, so a sync that stops halfway resumes from the last checkpoint instead of starting over. Streams without a primary key are read in one pass.

### Incremental sync

Incremental sync uses a cursor column that you choose for each stream. At the start of a sync the connector reads the highest cursor value in the table, then reads the rows whose cursor is greater than the last synced value and not greater than that maximum, ordered by the cursor. The highest cursor value read becomes the starting point of the next sync. Rows whose cursor is `NULL` are never read.

Choose a cursor column whose values only grow and are never updated, such as an insertion timestamp or a sequence number. If the table is partitioned or clustered on that column, BigQuery prunes the data it scans, which lowers the bytes billed for each incremental sync.

The following column types are supported as cursors:

| Cursor column type                          | Notes                                  |
| :------------------------------------------ | :------------------------------------- |
| `INT64`, `NUMERIC`, `BIGNUMERIC`, `FLOAT64` |                                        |
| `STRING`                                    | Ordered as BigQuery orders strings     |
| `DATE`, `DATETIME`, `TIME`, `TIMESTAMP`     | Compared at full microsecond precision |

`BOOL`, `BYTES`, `JSON`, `STRUCT` and `ARRAY` columns can't be cursors. `GEOGRAPHY`, `INTERVAL` and `RANGE` columns appear in the cursor list because they are read as strings, but they haven't been validated as cursors, so prefer one of the types in the table.

### State and resuming

The connector emits state while it reads, not only at the end of a sync. A sync that fails or is cancelled resumes from the last checkpoint: after the last primary key value for a full refresh of a keyed table, or after the last cursor value for an incremental sync. Resetting the connection's state makes the next sync start from the beginning.

The connector also reads the state saved by the legacy BigQuery source. A stream with legacy state resumes after the legacy cursor value instead of reading the table again.

### Read throughput

By default the connector fetches query results through the BigQuery REST API, which pages through the result a few thousand rows at a time. Tables are read in parallel with each other, up to **Max Concurrent Queries to Database**, but each table is read by a single query. The connector does not split one table across more than one query, because every extra query scans the table again and adds to the bytes billed.

Turning on **Use the BigQuery Storage Read API** streams each query result through the [Storage Read API](https://cloud.google.com/bigquery/docs/reference/storage) instead. The rows and values are identical; only the transport changes. On a test table of 5.2 million rows and 1.3 GB the difference was:

| Read path          | Rows per second | Time to read the table |
| :----------------- | :-------------- | :--------------------- |
| REST API (default) | about 5,400     | about 15 minutes       |
| Storage Read API   | about 104,000   | under 1 minute         |

The Storage Read API requires the BigQuery Read Session User role on the project that runs the query jobs, and Google bills Storage Read API usage separately from the bytes a query processes. Grant the role before turning the option on.

### Bytes billed

Each sync runs one query per stream, reading the whole table for a full refresh or the cursor range for an incremental sync, plus small sampling queries that estimate the row size. The bytes processed follow [BigQuery's on-demand pricing](https://cloud.google.com/bigquery/pricing), or your reservation. To move this cost and quota to another project, set **Job Execution Project ID**.

## Data type mapping

BigQuery column types are mapped to the following Airbyte types. The values every type produces are covered by the connector's [field type tests](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-bigquery-v2/src/test/kotlin/io/airbyte/integrations/source/bigqueryv2/BigQueryFieldTypesTest.kt).

| BigQuery type                                                          | Airbyte type                 | Notes                                                    |
| :--------------------------------------------------------------------- | :--------------------------- | :------------------------------------------------------- |
| `BOOL`                                                                 | `boolean`                    |                                                          |
| `INT64` (`INT`, `SMALLINT`, `INTEGER`, `BIGINT`, `TINYINT`, `BYTEINT`) | `integer`                    |                                                          |
| `FLOAT64`                                                              | `number`                     |                                                          |
| `NUMERIC` (`DECIMAL`)                                                  | `number`                     | Exact, written in plain decimal notation                 |
| `BIGNUMERIC` (`BIGDECIMAL`)                                            | `number`                     | Exact, written in plain decimal notation                 |
| `STRING`                                                               | `string`                     |                                                          |
| `BYTES`                                                                | `string`                     | Base64 encoded                                           |
| `DATE`                                                                 | `date`                       | Exact for every date, including dates before 1582-10-15  |
| `DATETIME`                                                             | `timestamp without timezone` | Microsecond precision                                    |
| `TIME`                                                                 | `time without timezone`      | Microsecond precision                                    |
| `TIMESTAMP`                                                            | `timestamp with timezone`    | UTC, microsecond precision                               |
| `JSON`                                                                 | `json`                       | Any JSON value: object, array, string, number or Boolean |
| `GEOGRAPHY`                                                            | `string`                     | Well-known text (WKT)                                    |
| `INTERVAL`                                                             | `string`                     | BigQuery's canonical interval text                       |
| `RANGE<T>`                                                             | `string`                     | BigQuery's range text                                    |
| `STRUCT`                                                               | `object`                     | Nested fields keep their own types in the schema         |
| `ARRAY<T>`                                                             | `array`                      | Items keep the type of `T`                               |

## Differences from the BigQuery (legacy) source

The connector keeps the configuration properties of the legacy source, so a saved configuration loads unchanged. The output differs in these ways:

- `DATE`, `DATETIME`, `TIME` and `TIMESTAMP` columns are typed as Airbyte date and time types instead of plain strings, `BYTES` columns declare their base64 encoding and `JSON` columns are typed as JSON instead of strings.
- `STRUCT` and `ARRAY` columns carry their nested schema in the catalog instead of an object or array without a schema.
- Primary key constraints become source-defined primary keys, which make full refresh syncs resumable.
- Incremental sync is offered only for streams that have a column of a supported cursor type, and only those columns can be chosen as the cursor. The legacy source accepted any column.
- Full refresh syncs emit state and resume after an interruption.
- A service account key is the only supported credential.
- The connection test fails on a dataset without tables.
- Dates before 1582-10-15 and timestamps in year 1 come through unchanged. The legacy source shifted them by two days.
- Legacy incremental state is understood and resumed from, as described in [State and resuming](#state-and-resuming).

## Limitations and troubleshooting

- **No change data capture.** Deleted rows are not detected and updated rows are only picked up when the cursor column changes.
- **`Discovered zero tables`** during the connection test means the dataset, or the project when **Dataset ID** is empty, has no tables the service account can see.
- **Discovery of a whole project is slow** when the project has thousands of datasets, because the tables are listed one dataset at a time. Set **Dataset ID**.
- **`Access Denied`, `PERMISSION_DENIED` or `Not found` errors** point at a missing role on the data project or the job project. Check the roles listed under [Service account](#service-account), and remember that **Job Execution Project ID** needs the BigQuery Job User role too.
- **Storage Read API reads need the BigQuery Read Session User role** on the project that runs the query jobs.
- **`GEOGRAPHY`, `INTERVAL` and `RANGE` cursors** haven't been validated. Use one of the [supported cursor types](#incremental-sync).

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                                            |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0.1.0   | 2026-09-18 | [85853](https://github.com/airbytehq/airbyte/pull/85853) | New connector on the Bulk CDK: full refresh and cursor incremental reads, nested schemas, primary keys, speed mode and the Storage Read API option |

</details>
