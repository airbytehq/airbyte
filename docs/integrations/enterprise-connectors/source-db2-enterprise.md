---
dockerRepository: airbyte/source-db2
enterprise-connector: true
---
# Source Db2

The Enterprise Db2 source connector reads data from your Db2 database. When CDC is not enabled, the connector operates in a read-only fashion. When CDC is enabled, the connector creates database triggers and tracking tables to capture changes.

## Features

| Feature                       | Supported | Notes |
| :---------------------------- |:----------|:------|
| Full Refresh Sync             | Yes       |       |
| Incremental Sync - Append     | Yes       |       |
| Replicate Incremental Deletes | Yes       | Available when using CDC |
| Change Data Capture (CDC)     | Yes       | Trigger-based CDC implementation |
| SSL Support                   | No        |       |
| SSH Tunnel Connection         | No        |       |
| Namespaces                    | Yes       |       |

## Getting Started

#### 1. Make sure your database is accessible from the machine running Airbyte

This is dependent on your networking setup. The easiest way to verify if Airbyte is able to connect
to your Db2 instance is by testing the connection in the UI.

#### 2. Create a dedicated read-only user with access to the relevant tables

This step is optional but highly recommended to allow for better permission control and auditing.
Alternatively, you can use Airbyte with an existing user in your database.

## Change Data Capture (CDC)

The Db2 Enterprise connector supports Change Data Capture using a trigger-based approach. This allows the connector to capture INSERT, UPDATE, and DELETE operations on your source tables.

### How trigger-based CDC works

Unlike log-based CDC systems (such as IBM InfoSphere Change Data Capture), this connector implements CDC using database triggers and tracking tables:

1. For each source table you want to replicate with CDC, a tracking table is created in the `_ab_cdc` schema
2. Three database triggers (INSERT, UPDATE, DELETE) are created on each source table
3. When data changes occur, the triggers automatically capture the changes into the tracking tables
4. During sync, the connector reads changes from the tracking tables and replicates them to your destination
5. After processing, the connector automatically deletes old change records to prevent unbounded growth

### CDC setup requirements

Before you can use CDC with the Db2 Enterprise connector, you must run a Python setup script to create the necessary triggers and tracking tables.

#### Prerequisites

- Python 3.7 or later
- The `ibm_db_dbi` Python package
- Database user with permissions to create tables in the `_ab_cdc` schema and create triggers on source tables

#### Running the CDC setup script

The setup script is located in the connector's repository at `python/trigger/cdc_setup_db2.py`. Run it using the following command:

```bash
python cdc_setup_db2.py \
  --database <DATABASE> \
  --host <HOST> \
  --port <PORT> \
  --user <USER> \
  --password <PASSWORD> \
  --schema <SOURCE_SCHEMA>
```

##### Options

- `--schema`: Process all tables in a specific schema
- `--tables`: Process only specific tables (requires `--schema`)
- `--input-file`: Process tables listed in a CSV or JSON file
- `--cdc-schema`: Custom schema for CDC tracking tables (default: `_ab_cdc`)
- `--recreate-triggers`: Drop and recreate existing triggers
- `--dry-run`: Preview changes without executing them

##### Example: set up CDC for all tables in a schema

```bash
python cdc_setup_db2.py \
  --database MYDB \
  --host db2.example.com \
  --port 50000 \
  --user airbyte_user \
  --password secret123 \
  --schema SALES
```

##### Example: set up CDC for specific tables

```bash
python cdc_setup_db2.py \
  --database MYDB \
  --host db2.example.com \
  --port 50000 \
  --user airbyte_user \
  --password secret123 \
  --schema SALES \
  --tables ORDERS CUSTOMERS PRODUCTS
```

### Configuring CDC in Airbyte

After running the setup script, configure your Db2 Enterprise source in Airbyte:

1. In the connector configuration, select "Read Changes using Change Data Capture (CDC)" as the cursor method
2. Set the "Initial Load Timeout in Hours" (default: 8 hours) - this controls how long the initial snapshot phase can run before switching to incremental CDC mode
3. Complete the rest of the configuration and test the connection

### CDC behavior

**Initial sync:**

The first sync performs a full snapshot of your source tables, reading all existing data. This phase is limited by the initial load timeout setting.

**Subsequent syncs:**

After the initial snapshot completes, the connector switches to incremental mode and reads only changes from the CDC tracking tables.

**Change tracking:** The connector tracks three types of operations:

- INSERT: New records added to source tables
- UPDATE: Modifications to existing records
- DELETE: Records removed from source tables

**CDC metadata fields:** When using CDC, the connector adds the following metadata fields to each record:

- `_ab_cdc_updated_at`: Timestamp when the change occurred
- `_ab_cdc_deleted_at`: Timestamp when the record was deleted (null for non-deleted records)
- `_ab_trigger_change_time`: Timestamp from the trigger table used as the cursor

**Automatic cleanup:**

To prevent tracking tables from growing indefinitely, the connector automatically deletes processed change records during each sync. Only records older than the current checkpoint are removed.

### Important considerations

- **Database permissions for CDC:** The trigger-based CDC approach requires write permissions on your database to create triggers and tracking tables. The database user credentials you enter in the Airbyte connector configuration must have the following permissions:
  - `CREATE TABLE` privilege in the `_ab_cdc` schema (or your custom CDC schema)
  - `CREATE TRIGGER` privilege on all source tables you want to replicate with CDC
  - These permissions are granted by your database administrator using DB2's `GRANT` statements
- Triggers add a small performance overhead to INSERT, UPDATE, and DELETE operations on source tables
- The `_ab_cdc` schema and tracking tables must not be modified manually
- If you drop and recreate a source table, you must rerun the CDC setup script for that table
- CDC is not compatible with IBM InfoSphere Change Data Capture - this connector uses its own trigger-based implementation

## Data type mapping

Db2 data types are mapped to the following data types when synchronizing data.

| Oracle Type              | Airbyte Type               | Notes                                      |
|:-------------------------|:---------------------------|:-------------------------------------------|
| `SMALLINT`               | integer                    |                                            |
| `INT`                    | integer                    |                                            |
| `INTEGER`                | integer                    |                                            |
| `BIGINT`                 | integer                    |                                            |
| `DECIMAL`                | number/integer             | if scale is 0, use integer                 |
| `DEC`                    | number/integer             | if scale is 0, use integer                 |
| `NUMERIC`                | number/integer             | if scale is 0, use integer                 |
| `REAL`                   | number                     |                                            |
| `FLOAT`                  | number                     |                                            |
| `DOUBLE`                 | number                     |                                            |
| `DOUBLE PRECISION`       | number                     |                                            |
| `DECFLOAT`               | number                     | INF, -INF, and NaN values will map to null |
| `CHAR`                   | string                     |                                            |
| `CHARACTER`              | string                     |                                            |
| `VARCHAR`                | string                     |                                            |
| `CHARACTER VARYING`      | string                     |                                            |
| `CHAR VARYING`           | string                     |                                            |
| `CLOB`                   | string                     |                                            |
| `CHARACTER LARGE OBJECT` | string                     |                                            |
| `CHAR LARGE OBJECT`      | string                     |                                            |
| `BLOB`                   | binary                     |                                            |
| `BINARY LARGE OBJECT`    | binary                     |                                            |
| `BINARY`                 | binary                     |                                            |
| `VARBINARY`              | binary                     |                                            |
| `BINARY VARYING`         | binary                     |                                            |
| `DATE`                   | date                       |                                            |
| `TIME`                   | time without timezone      |                                            |
| `TIMESTAMP`              | timestamp without timezone |                                            |
| `BOOLEAN`                | boolean                    |                                            |
| `XML`                    | xml                        |                                            |


## Changelog

<details>
  <summary>Expand to review</summary>

The connector is still incubating, this section only exists to satisfy Airbyte's QA checks.

- 0.0.1

</details>
