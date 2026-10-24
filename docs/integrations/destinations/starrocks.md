# StarRocks

This page guides you through setting up the StarRocks destination connector.

[StarRocks](https://www.starrocks.io/) is a high-performance analytical database. This
connector writes Airbyte records to StarRocks tables using HTTP **Stream Load** for the data
plane and the MySQL protocol for the control plane (DDL and version detection). It supports
full-refresh and incremental syncs, including Change Data Capture (CDC).

The connector is built in Kotlin on Airbyte's Bulk CDK (Direct Load): records land in typed
StarRocks tables (no raw JSON tables), and the connector chooses the StarRocks table model per sync
mode (DUPLICATE KEY for append, PRIMARY KEY for deduplication).

:::note
This connector is currently available for **Airbyte Open Source (self-managed)** only.
:::

## Features

| Feature                        | Supported | Notes                                                      |
| ------------------------------ | :-------: | ---------------------------------------------------------- |
| Full Refresh - Overwrite       |     O     | DUPLICATE KEY table, swapped in atomically                 |
| Full Refresh - Append          |     O     | DUPLICATE KEY table                                        |
| Incremental - Append           |     O     | DUPLICATE KEY table                                        |
| Incremental - Append + Dedup   |     O     | PRIMARY KEY table, load-time upsert via `__op`             |
| Change Data Capture (CDC)      |     O     | Hard or soft delete (see CDC deletion mode)                |
| Namespaces                     |     O     | Stream namespace maps to a StarRocks database              |
| Replicate Incremental Deletes  |     O     | Via CDC soft delete (`_ab_cdc_deleted_at`)                 |
| SSL/TLS connection             |     O     | Control plane (MySQL protocol) only; Stream Load stays HTTP |
| SSH tunnel (bastion)           |     O     | Carries both planes; use the `SQL` load method when tunneling |
| Airbyte Cloud                  |     X     | Self-managed (OSS) only for now                            |

## Prerequisites

- A running StarRocks cluster, version **3.3.x or newer** (the connector rejects older clusters at
  connection check; the tested ceiling is **4.1.x**).
- Network access from the Airbyte worker to **both** ports:
  - the **query port** (MySQL protocol, default `9030`) for DDL and `SELECT current_version()`, and
  - the **HTTP port** (FE HTTP, default `8030`) for Stream Load.
- A StarRocks user with privileges to create databases/tables and to INSERT (Stream Load) into the
  target database.

## Setup guide

### Step 1: Prepare the StarRocks user and database

Connect to StarRocks over the MySQL protocol (port `9030`) and ensure the sync user can create
objects and load data. For example:

```sql
CREATE USER 'airbyte'@'%' IDENTIFIED BY '{password}';
GRANT CREATE DATABASE ON *.* TO 'airbyte'@'%';
GRANT ALL ON DATABASE {database} TO 'airbyte'@'%';
```

The connector creates the target database (`CREATE DATABASE IF NOT EXISTS`) and the per-stream
tables itself, so the user mainly needs create and load (INSERT) privileges on the target database.
If you leave the **Database** field blank, the connector uses a database named `default`.

### Step 2: Configure the connection

Create a new destination of type **StarRocks** and fill in the connection parameters below. The
connection **Check** validates both planes end to end: it connects over the MySQL protocol, reads
`current_version()`, applies version gating, and then round-trips one row through Stream Load
(create throwaway table, load one row, drop it). A passing check therefore implies a working sync.

### Step 3 (optional): Enable SSL/TLS

SSL applies to the **control plane only** (the MySQL/JDBC connection on port `9030`). Set **SSL** to
true and pick an **SSL Mode**:

- `required` — encrypt the connection but do not verify the server certificate (use for self-signed
  certificates).
- `verify_ca` / `verify_identity` — verify the certificate against the JVM trust store.

The Stream Load data plane (HTTP port `8030`) stays plain HTTP even on TLS-enabled clusters, because
StarRocks' FE HTTP port is not TLS.

## Connection parameters

| Parameter           | Required | Default       | Description                                                                                              |
| ------------------- | :------: | ------------- | -------------------------------------------------------------------------------------------------------- |
| `host`              |   Yes    | —             | FE host of the StarRocks cluster.                                                                         |
| `port`              |   Yes    | `9030`        | MySQL-protocol port for queries/DDL and version detection.                                                |
| `http_port`         |   Yes    | `8030`        | FE HTTP port for Stream Load (data plane).                                                                |
| `username`          |   Yes    | `root`        | Username to access the database.                                                                          |
| `password`          |    No    | —             | Password for the username (stored as a secret).                                                          |
| `database`          |   Yes    | `default`     | Target database. Blank falls back to `default`.                                                           |
| `ssl`               |    No    | `false`       | Use SSL for the MySQL-protocol (control-plane) connection. Does not affect Stream Load.                   |
| `ssl_mode`          |    No    | `required`    | Certificate verification when SSL is on: `required`, `verify_ca`, or `verify_identity`.                   |
| `enable_json`       |    No    | `false`       | Store object fields as the StarRocks `JSON` type instead of a JSON-encoded `STRING`.                     |
| `cdc_deletion_mode` |    No    | `Hard delete` | CDC delete handling for deduped streams: `Hard delete` or `Soft delete`.                                  |
| `load_format`       |    No    | `CSV`         | Stream Load body format: `CSV` (no options) or `JSON` (with a nested `compression` option).               |
| `compression`       |    No    | `none`        | Under the `JSON` load format only: `none`, `gzip`, or `zstd` for the Stream Load request body.            |
| `tunnel_method`     |    No    | No tunnel     | Optional SSH tunnel (jump server / bastion) for both planes. See "SSH tunnel and load method" below.      |
| `load_method`       |    No    | `Stream Load` | How records are loaded: `Stream Load` (HTTP bulk load) or `SQL` (batched INSERT/DELETE over JDBC).        |
| `replication_num`   |    No    | cluster default | Replicas per tablet for tables the connector creates (StarRocks `replication_num`). Unset uses the cluster default (normally 3); set to `1` for single-BE shared-nothing clusters. Applies to newly created tables only. |

## Supported sync modes

| Sync mode                       | Supported | Table model                                   |
| ------------------------------- | :-------: | --------------------------------------------- |
| Full Refresh - Overwrite        |     O     | DUPLICATE KEY                                 |
| Full Refresh - Append           |     O     | DUPLICATE KEY                                 |
| Incremental - Append            |     O     | DUPLICATE KEY                                 |
| Incremental - Append + Dedup    |     O     | PRIMARY KEY                                   |

- **Append / Overwrite** streams write to **DUPLICATE KEY** tables keyed on the per-record unique
  `_airbyte_raw_id`. A DUPLICATE key is not a uniqueness constraint, so append never collapses
  business-duplicate records.
- **Append + Dedup** (and CDC) streams write to **PRIMARY KEY** tables. Deduplication happens at
  load time: each row carries a trailing `__op` column (`0` = upsert, `1` = delete) that StarRocks
  applies against the primary key. PRIMARY KEY columns are forced `NOT NULL` and are immutable
  (never altered) after the table is created.

### Choosing a sync mode

| Goal                                            | Recommended mode                                        |
| ----------------------------------------------- | ------------------------------------------------------- |
| Mirror the source's current state exactly       | Full Refresh - Overwrite, or CDC + Dedup (hard delete)  |
| Keep a large table cheaply up to date           | Incremental - Append + Dedup (with CDC)                 |
| Keep a record that a row was deleted            | Append + Dedup with CDC **soft delete**                 |
| Track every change, updates included            | Incremental - Append (with CDC)                         |
| Simple append-only log / event tables           | Incremental - Append (a cursor is enough)               |
| Fully refresh a small dimension table           | Full Refresh - Overwrite                                |

### Cursor vs CDC incremental

Incremental syncs come in two flavors, and the difference matters when picking a mode:

- **Cursor (standard incremental)** pulls rows whose cursor column (e.g. `updated_at`) is greater
  than the last sync. Simple and works on almost any source, but it **cannot detect deletes**
  (deleted rows linger in the destination), misses changes when the cursor is not updated, and can
  miss late-arriving rows with a smaller cursor value.
- **CDC** reads the database change log (e.g. MySQL binlog) directly, capturing **inserts, updates,
  and deletes in order**. It catches deletes but requires source-side setup (binlog enabled, etc.).

In short: use **CDC** when deletes must be reflected; a **cursor** is enough for append- or
update-only tables.

### Namespaces

A stream's namespace maps to a StarRocks database. Streams without a namespace use the configured
**Database**.

## Change Data Capture (CDC)

For CDC sources synced with Append + Dedup, the **CDC Deletion Mode** controls how deletes land:

- **Hard delete** (default): the row is removed from the destination (`__op=1`).
- **Soft delete**: the row is kept and marked via the `_ab_cdc_deleted_at` column (loaded as
  `__op=0`). Query live rows with `WHERE _ab_cdc_deleted_at IS NULL`.

How each change type lands, by mode (CDC enabled):

| Mode                        | INSERT        | UPDATE                       | DELETE                                       |
| --------------------------- | ------------- | ---------------------------- | -------------------------------------------- |
| CDC + Append                | new row       | new row (history kept)       | tombstone row added (history kept)           |
| CDC + Dedup, hard delete    | upsert latest | overwrite with latest        | row removed                                  |
| CDC + Dedup, soft delete    | upsert latest | overwrite with latest        | row kept, `_ab_cdc_deleted_at` set           |

With **CDC + Append**, every insert/update/delete is retained as its own row, so the full change
history of a key is preserved — useful for audit logs and change analysis.

> Note: `__op` is a reserved column name in StarRocks 3.3.6+. If a source stream already has an
> `__op` column it must be renamed upstream to avoid a collision.

## Load format and compression

The **Load Format** parameter is a choice between two Stream Load body formats:

- **CSV** (default): compact and high-throughput. Caveats:
  - A literal `\N` string is stored as `NULL` (it is StarRocks' CSV null marker, even inside an
    enclosure).
  - Very large `BIGINT` / `DECIMAL` values can lose precision.
- **JSON**: avoids the CSV escaping edge cases above, and preserves full integer/decimal precision
  by emitting numbers as JSON strings (a JSON number would be parsed as a double and overflow).
  JSON additionally supports request-body **compression**:
  - `none`, `gzip`, or `zstd` (`zstd` compresses better at similar or lower CPU cost).
  - Compression requires a cluster **>= 3.3.2** and is honored by StarRocks for JSON Stream Load
    only. If compression is requested on an older cluster, the connection check fails.

Stream Load batches use a content-addressed label (a hash of the batch body), so retrying the same
batch is idempotent: StarRocks rejects the re-load as "Label Already Exists", which the connector
treats as success to prevent duplicate rows.

## SSH tunnel and load method

When the Airbyte worker cannot reach the cluster directly, set **SSH Tunnel Method** to route the
connection through a jump server (bastion). The tunnel carries **both** planes — the JDBC control
plane and the Stream Load data plane (the FE→BE redirect is followed through a SOCKS forward). Because
every byte of a sync flows through the bastion, it becomes a throughput bottleneck for high-volume
loads; prefer direct connectivity (VPN / peering) at scale.

The **Load Method** parameter chooses how records reach StarRocks:

- **Stream Load** (default): StarRocks' high-throughput HTTP bulk load. The HTTP data plane does not
  speak SSL and is awkward to tunnel on its own.
- **SQL**: loads over the JDBC connection with batched `INSERT` / `DELETE`. Throughput is lower, but
  it works over an **SSH tunnel** and **end-to-end SSL**, which the Stream Load HTTP data plane does
  not. Use `SQL` when an SSH tunnel is configured. (The **Load Format** option above applies to
  Stream Load only.)

## Output schema

### Airbyte metadata columns

Every table includes these four Airbyte metadata columns (all `NOT NULL`):

| Column                    | StarRocks type |
| ------------------------- | -------------- |
| `_airbyte_raw_id`         | STRING         |
| `_airbyte_extracted_at`   | DATETIME       |
| `_airbyte_meta`           | STRING         |
| `_airbyte_generation_id`  | BIGINT         |

### Type mapping

Airbyte schema types map to StarRocks SQL column types as follows:

| Airbyte type                       | StarRocks type      |
| ---------------------------------- | ------------------- |
| Boolean                            | BOOLEAN             |
| Integer                            | BIGINT              |
| Number                             | DECIMAL(38, 9)      |
| Date                               | DATE                |
| Timestamp (with/without timezone)  | DATETIME            |
| Time (with/without timezone)       | STRING              |
| String                             | STRING              |
| Array                              | STRING              |
| Union                              | STRING              |
| Object                             | JSON or STRING      |

Notes:

- **Object** fields map to the StarRocks `JSON` type when **Enable JSON** is on, otherwise to a
  JSON-encoded `STRING`. Enable JSON for sources with rich JSON columns (for example Postgres
  `jsonb`).
- Timestamps are normalized to UTC and written in `yyyy-MM-dd HH:mm:ss` format (no `T`, no offset).

### Out-of-range value handling

Values that fall outside the range of their target StarRocks column are set to `NULL` and recorded
in `_airbyte_meta` with a `DESTINATION_FIELD_SIZE_LIMITATION` change, rather than failing the load.
This applies to:

| Target column   | Accepted range                                  |
| --------------- | ----------------------------------------------- |
| BIGINT          | signed 64-bit (the Long range)                  |
| DECIMAL(38, 9)  | absolute value < 10^29 (29 integer digits)      |
| DATE            | 0000-01-01 .. 9999-12-31                        |
| DATETIME        | 0000-01-01 00:00:00 .. 9999-12-31 23:59:59      |

## Schema evolution

When a source column is added, dropped, or retyped, the connector evolves the destination table to
match. Adding a column and dropping a non-key column are applied in place, as a single
`ALTER TABLE` statement per sync (`ADD COLUMN` — always nullable, since StarRocks cannot add a
`NOT NULL` column to a populated table — and `DROP COLUMN`). StarRocks runs the change as an
asynchronous schema-change job; the connector waits for it to finish before loading, so consecutive
syncs that each evolve the schema do not collide.

**Type changes** are applied by **rebuilding the table**. StarRocks cannot `ALTER ... MODIFY COLUMN`
between many types in place (for example `integer` ⇄ `number`, i.e. `BIGINT` ⇄ `DECIMAL`), so the
connector creates a new table with the updated schema, copies the data through per-column `CAST`s, and
atomically swaps it in. Widenings such as `integer` → `number` are applied **losslessly** — the
existing rows are converted, not truncated. This is a one-time full-table copy per type change (it
mirrors how the BigQuery and Snowflake destinations handle the same limitation), and the original
table is untouched until the final swap, so a failed rebuild leaves the data intact.

One case still fails the sync: **dropping a primary-key column** (the source removed/renamed its
primary key), since StarRocks cannot drop a key column — recreate the table with a **Refresh**.
(Removing a primary-key field is a breaking change, so Airbyte pauses the connection for review first.)

## StarRocks version compatibility

The connector detects the cluster version with `SELECT current_version()` (at connection check and
again at write start) and gates behavior on it:

- **Floor:** shared-data **3.3.x**. Older clusters are rejected at the connection check.
- **Ceiling (tested):** **4.1.x**.
- **JSON request-body compression:** requires **>= 3.3.2**.

Higher versions improve throughput and operational efficiency (for example Merge Commit at 3.4+ and
PK-load parallelism at 4.1) rather than unlocking new connector features. The full feature matrix is
in the connector's
[`CONTRIBUTING.md`](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/destination-starrocks/CONTRIBUTING.md).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                                                   |
| :------ | :--------- | :-------------------------------------------------------- | :-------------------------------------------------------- |
| 0.1.0   | 2026-09-18 | [86475](https://github.com/airbytehq/airbyte/pull/86475) | New destination: StarRocks (Kotlin, Bulk CDK, Stream Load) |

</details>
