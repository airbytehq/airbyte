# SAP HANA (Community)

<HideInUI>

This page contains the setup guide and reference information for the community [SAP HANA](https://www.sap.com/products/data-cloud/hana.html) source connector.

</HideInUI>

This community connector (not to be confused with the discontinued
[SAP HANA Enterprise connector](/integrations/enterprise-connectors/source-sap-hana)) reads tables and views from SAP HANA (on-premise, including S/4HANA and BW/4HANA, and SAP HANA Cloud)
with SAP's native `hdbcli` driver. It supports full refresh (resumable, for tables with a primary key)
and cursor-based incremental syncs.

## Prerequisites

- SAP HANA 2.0 or SAP HANA Cloud
- The SQL port of the tenant database (`3<instance>15` for single-tenant, `3<instance>41+` for tenant databases, `443` for HANA Cloud)
- A database user with `SELECT` on the tables to replicate
- Network access from Airbyte to HANA, directly or through an SSH bastion host

## Setup guide

### Step 1: Create a read-only user in SAP HANA

```sql
CREATE USER AIRBYTE_READER PASSWORD "<strong password>" NO FORCE_FIRST_PASSWORD_CHANGE;
-- whole schema…
GRANT SELECT ON SCHEMA SAPHANADB TO AIRBYTE_READER;
-- …or single tables
GRANT SELECT ON SAPHANADB.ACDOCA TO AIRBYTE_READER;
```

Catalog views (`SYS.TABLES`, `SYS.TABLE_COLUMNS`, `SYS.CONSTRAINTS`, `SYS.SCHEMAS`, `SYS.M_TABLES`) are public.
They only show objects the user is allowed to read.

### Step 2: Set up the source in Airbyte

1. Go to **Sources → + New source** and select **SAP HANA (Community)**.
2. Enter **Host**, **Port**, **Username**, **Password** and the **Schemas** to replicate (e.g. `SAPHANADB`).
3. **Strongly recommended for SAP ERP schemas:** restrict discovery with **Table Name Patterns** (SQL `LIKE`, e.g. `ACDOCA`, `MAR%`).
   An S/4HANA schema has more than 100,000 tables.
4. Optional:
   - **Stream Settings**: a row filter per table, a default cursor, and a primary key override (see below).
   - **SSH Tunnel Method**: when HANA is only reachable through a bastion host.
   - **Encrypt Connection (TLS)**: required for SAP HANA Cloud.
5. Click **Set up source**. The connection check also validates every row filter against HANA.

## Supported sync modes

| Feature | Supported | Notes |
|---|---|---|
| Full Refresh Sync | Yes | Resumable (keyset pagination on the primary key) for tables with a primary key |
| Incremental Sync - Append | Yes | User-defined cursor |
| Incremental Sync - Append + Deduped | Yes | Uses the table's primary key, or the `primary_key` override |
| Namespaces | Yes | The HANA schema is the stream namespace |
| SSH Tunnel | Yes | Key or password authentication |
| Column selection | Yes | Only selected columns are queried |

### Stream settings

| Field | Description |
|---|---|
| `stream` | `TABLE` (any configured schema) or `SCHEMA.TABLE` |
| `condition` | SQL predicate applied as `WHERE (condition)` in every sync mode, e.g. `RCLNT = '100' AND GJAHR >= '2025'` |
| `cursor_field` | Default cursor for incremental syncs |
| `primary_key` | Primary key override for tables without a primary key constraint. The columns must be unique together. |

Example for the S/4HANA Universal Journal:

```json
{
  "stream": "ACDOCA",
  "condition": "RCLNT = '100'",
  "cursor_field": "TIMESTAMP",
  "primary_key": ["RCLNT", "RLDNR", "RBUKRS", "GJAHR", "BELNR", "DOCLN"]
}
```

### Incremental syncs

The connector runs `SELECT … WHERE cursor > <last value> ORDER BY cursor`.
A checkpoint is only emitted once every row sharing a cursor value has been read.
After a lost connection, only rows with the last, partially read cursor value are read again.
Deleted rows, and updates that do not change the cursor, are not captured.

### Resilience

Transient HANA errors (`-10807 Connection down`, `-10709 Connection failed`, …) trigger a reconnect after
`retry_wait_seconds`, up to `max_retries` times. The retry budget resets whenever the stream makes progress.
Resumable full refresh and incremental streams continue from their last checkpoint. A plain full refresh
(no primary key) restarts only if the failure happens before its first record.

## Data type mapping

| SAP HANA type | Airbyte type | Notes |
|---|---|---|
| `TINYINT`, `SMALLINT`, `INTEGER`, `BIGINT` | `integer` | |
| `DECIMAL`, `SMALLDECIMAL` | `number` | `string` with `decimal_handling = string` (full precision) |
| `REAL`, `DOUBLE`, `FLOAT` | `number` | |
| `BOOLEAN` | `boolean` | |
| `DATE` | `date` | |
| `TIME` | `time_without_timezone` | |
| `TIMESTAMP`, `SECONDDATE` | `timestamp_without_timezone` | |
| `VARCHAR`, `NVARCHAR`, `ALPHANUM`, `SHORTTEXT`, `CLOB`, `NCLOB`, `TEXT` | `string` | NUL characters are stripped by default |
| `VARBINARY`, `BLOB`, `ST_GEOMETRY`, `ST_POINT` | `string` (base64) | |

## Performance tips

- Keep **Compress Network Traffic** on (default) when Airbyte and HANA are not on the same LAN.
  On a VPN link it cut a 941k-row full refresh from 86 s to 23 s.
- Increase **Max Concurrent Streams** (2–4) to read several tables in parallel. With 3 workers, 7 tables
  synced 2.5× faster. Keep it at 1 on systems that struggle under load.
- Use a **Row Filter** to restrict very large tables (e.g. by fiscal year), and a primary key override so
  full refreshes can resume.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject |
|:--------|:-----------|:-------------|:--------|
| 0.4.1   | 2026-09-23 | [86928](https://github.com/airbytehq/airbyte/pull/86928) | Initial community release: resumable full refresh, cursor-based incremental, per-stream settings, SSH tunnel, concurrent streams |

</details>
