---
description: >-
  BigQuery is a fully managed, highly scalable, and cost-effective data warehouse
  offered by Google Cloud.
---

# BigQuery (v2)

The BigQuery (v2) source connector reads tables, views, materialized views, external tables and table snapshots from Google BigQuery datasets. It supports full refresh and incremental syncs, discovers nested `STRUCT` and `ARRAY` schemas and primary key constraints, reads tables through the BigQuery Storage Read API in parallel read streams, and checkpoints every read stream so that large tables resume after an interruption.

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
| Storage Read API          | Yes       | On by default, see [Read throughput](#read-throughput)           |
| SSL                       | Yes       | All traffic to the BigQuery API uses HTTPS                       |

The connector is read-only. It reads table data through the Storage Read API, runs `SELECT` queries for views and incremental syncs, and never writes to your project.

## Getting started

### Requirements

- A Google Cloud project with the BigQuery API enabled.
- A service account with read access to the datasets to sync, permission to run query jobs and, for high-speed reads, permission to create Storage Read API sessions.
- A JSON key for that service account.

### Service account

Create a dedicated service account for Airbyte by following Google's [Create service accounts](https://cloud.google.com/iam/docs/service-accounts-create) guide, then grant it the following roles. Using a dedicated account keeps permissions and auditing simple.

| Role                                                          | Where to grant it                                                                               | Why                                                                                                                                       |
| :------------------------------------------------------------ | :---------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------- |
| BigQuery Data Viewer (`roles/bigquery.dataViewer`)            | The project, or each dataset to sync                                                            | Lists datasets and tables, reads table schemas and table data                                                                             |
| BigQuery Job User (`roles/bigquery.jobUser`)                  | The project that runs the query jobs (**Project ID**, or **Job Execution Project ID** when set) | Runs the `SELECT` queries for views, incremental syncs and the fallback read path                                                         |
| BigQuery Read Session User (`roles/bigquery.readSessionUser`) | The project that runs the query jobs                                                            | Reads tables through the Storage Read API, the high-speed path. See [Permissions for high-speed reads](#permissions-for-high-speed-reads) |

### Permissions for high-speed reads

The connector reads tables through the [BigQuery Storage Read API](https://cloud.google.com/bigquery/docs/reference/storage) by default. This is the path that makes large tables fast, and it needs permissions that the query path does not:

| Permission                      | Included in role           | Where it is needed                                                                                 |
| :------------------------------ | :------------------------- | :------------------------------------------------------------------------------------------------- |
| `bigquery.readsessions.create`  | BigQuery Read Session User | The project that runs the jobs, which is **Project ID** or, when set, **Job Execution Project ID** |
| `bigquery.readsessions.getData` | BigQuery Read Session User | The same project                                                                                   |
| `bigquery.tables.getData`       | BigQuery Data Viewer       | The datasets to sync                                                                               |

Google bills Storage Read API usage by the bytes read, separately from the bytes a query processes. See [BigQuery pricing](https://cloud.google.com/bigquery/pricing).

Without these permissions the sync still works. At the start of every sync the connector checks once whether it can open a read session. If it can't, it logs a warning that names the missing permission and reads through the query path instead. That path is much slower and scans the table for every query it runs, so grant the role before syncing tables larger than a few gigabytes. Turning **Use the BigQuery Storage Read API** off forces the query path.

The other permissions the connector uses are `bigquery.datasets.get`, `bigquery.tables.list`, `bigquery.tables.get` and `bigquery.jobs.create`.

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
| **Use the BigQuery Storage Read API**  | No       | Advanced, on by default. Reads tables through the Storage Read API and streams query results through it. Turn it off to read everything through the query API, which is much slower on large tables. See [Read throughput](#read-throughput).        |

4. Click **Set up source**. The connection test lists the datasets and their tables and runs a trivial query. It fails with `Discovered zero tables` when the dataset, or the whole project, contains no tables.

## Replication

### Discovered streams

Every dataset is a namespace and every table, view, materialized view, external table and table snapshot in it is a stream. BigQuery ML models are skipped, as are tables without columns. Column names and types come from the table metadata, including the nested fields of `STRUCT` columns and the element type of `ARRAY` columns. A table with a `PRIMARY KEY` constraint, which BigQuery declares but does not enforce, reports it as the source-defined primary key.

### Full refresh

A full refresh of a table opens a Storage Read API session, which splits the table into read streams. A read stream is BigQuery's unit of parallel reading and has nothing to do with an Airbyte stream. The connector reads the read streams in order, up to **Max Concurrent Queries to Database** at a time, and asks for many small read streams of about 8 GiB each so that checkpoints are frequent. Every completed read stream is a checkpoint.

Views, materialized views, external tables and table snapshots can't be read through the Storage Read API. They are read with one `SELECT` query each, and so is every table when the Storage Read API is unavailable. On that fallback path a table with a single-column primary key is split into key ranges of roughly equal size, computed with `APPROX_QUANTILES` over the key column, and each range is one query and one checkpoint. Tables without such a key are read in one query.

### Incremental sync

Incremental sync uses a cursor column that you choose for each stream. The first sync of an incremental stream reads the whole table the same way a full refresh does, through the Storage Read API in parallel read streams, so a terabyte table's first sync takes minutes rather than days. To keep that read consistent, the connector pins it to one version of the table: it picks a snapshot time a couple of seconds in the past, opens the read session on the table as of that time, and reads the cursor's maximum as of that same time with BigQuery time travel. That maximum becomes the cursor checkpoint once every read stream is complete. Later syncs run a query for the rows whose cursor is greater than the checkpoint and not greater than the table's current maximum, and the highest value read becomes the next checkpoint. Rows whose cursor is `NULL` are never read.

Choose a cursor column whose values only grow and are never updated, such as an insertion timestamp or a sequence number. If the table is partitioned or clustered on that column, BigQuery prunes the data it scans, which lowers the bytes billed for each incremental sync.

The following column types are supported as cursors:

| Cursor column type                          | Notes                                  |
| :------------------------------------------ | :------------------------------------- |
| `INT64`, `NUMERIC`, `BIGNUMERIC`, `FLOAT64` |                                        |
| `STRING`                                    | Ordered as BigQuery orders strings     |
| `DATE`, `DATETIME`, `TIME`, `TIMESTAMP`     | Compared at full microsecond precision |

`BOOL`, `BYTES`, `JSON`, `STRUCT` and `ARRAY` columns can't be cursors. `GEOGRAPHY`, `INTERVAL` and `RANGE` columns appear in the cursor list because they are read as strings, but they haven't been validated as cursors, so prefer one of the types in the table.

### State and resuming

The connector emits state while it reads, not only at the end of a sync. For a table read through the Storage Read API the state names the read session, the last read stream that completed in order and the row offset of every read stream still in progress, and a sync that fails or is cancelled resumes exactly there. The first sync of an incremental stream also records its snapshot time and the cursor maximum at that time, so a resumed sync keeps the same table version and the same checkpoint. A read session is valid for six hours after it opens. A full refresh that resumes later than that reads the table again from the start; an incremental first sync reopens a session at its recorded snapshot time, which BigQuery serves for the table's time travel window of two to seven days, and only takes a new snapshot beyond that. On the query path the state holds the last completed key range of a full refresh, or the last cursor value of an incremental sync. Resetting the connection's state makes the next sync start from the beginning.

The connector also reads the state saved by the legacy BigQuery source. A stream with legacy state resumes after the legacy cursor value instead of reading the table again.

### Read throughput

The Storage Read API delivers table data as compressed Arrow batches over many read streams at once, and BigQuery serves the read streams without running a query. The query path, used for views, incremental syncs and as the fallback, pages each result through the BigQuery REST API a few thousand rows at a time and scans the table for every query it runs. Measured on a table of 515 GiB and 275 million rows:

| Read path                           | Throughput                      | Time to read the table                                  |
| :---------------------------------- | :------------------------------ | :------------------------------------------------------ |
| Storage Read API, four read streams | at least 480 MB/s of table data | well under an hour, depending on the worker's resources |
| Query API, four queries at a time   | about 3.7 MB/s per query        | about ten hours                                         |

When the connector has the Storage Read API permissions, query results also stream through it, so views and incremental syncs benefit as well: on a 5.2 million row, 1.3 GB test table one query took about 15 minutes through the REST API and under a minute through the Storage Read API. The rows and values are identical on every path. The permissions are listed under [Permissions for high-speed reads](#permissions-for-high-speed-reads).

### Bytes billed

A full refresh of a table through the Storage Read API reads the table once and is billed as Storage Read API bytes, not as query bytes. Views, incremental syncs and the fallback path run queries whose bytes processed follow [BigQuery's on-demand pricing](https://cloud.google.com/bigquery/pricing), or your reservation. An incremental query reads the cursor range, and each key range of the fallback path scans the whole table unless the table is clustered or partitioned on the key. To move query cost and quota to another project, set **Job Execution Project ID**.

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
- Primary key constraints become source-defined primary keys.
- Incremental sync is offered only for streams that have a column of a supported cursor type, and only those columns can be chosen as the cursor. The legacy source accepted any column.
- Tables are read through the Storage Read API in parallel read streams, and full refresh syncs emit state and resume after an interruption.
- A service account key is the only supported credential.
- The connection test fails on a dataset without tables.
- Dates before 1582-10-15 and timestamps in year 1 come through unchanged. The legacy source shifted them by two days.
- Legacy incremental state is understood and resumed from, as described in [State and resuming](#state-and-resuming).

## Limitations and troubleshooting

- **No change data capture.** Deleted rows are not detected and updated rows are only picked up when the cursor column changes.
- **`Discovered zero tables`** during the connection test means the dataset, or the project when **Dataset ID** is empty, has no tables the service account can see.
- **Discovery of a whole project is slow** when the project has thousands of datasets, because the tables are listed one dataset at a time. Set **Dataset ID**.
- **`Access Denied`, `PERMISSION_DENIED` or `Not found` errors** point at a missing role on the data project or the job project. Check the roles listed under [Service account](#service-account), and remember that **Job Execution Project ID** needs the BigQuery Job User role too.
- **A warning about the Storage Read API at the start of a sync** means the service account lacks a permission listed under [Permissions for high-speed reads](#permissions-for-high-speed-reads). The sync completes through the query path, but large tables take much longer.
- **Read sessions expire after six hours.** A table whose sync is interrupted and resumed more than six hours later is read again from the start.
- **`GEOGRAPHY`, `INTERVAL` and `RANGE` cursors** haven't been validated. Use one of the [supported cursor types](#incremental-sync).

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                                                     |
| :------ | :--------- | :------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0.1.0   | 2026-09-18 | [85853](https://github.com/airbytehq/airbyte/pull/85853) | New connector on the Bulk CDK with Storage Read API reads and resumable read streams, cursor incremental reads, nested schemas, primary keys and speed mode |

</details>
