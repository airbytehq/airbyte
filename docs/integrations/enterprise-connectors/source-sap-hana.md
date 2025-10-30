---
dockerRepository: airbyte/source-sap-hana-enterprise
enterprise-connector: true
---

# Source SAP HANA

The Enterprise SAP HANA source connector reads data from your SAP HANA database. To use CDC, your database must have triggers and tracking tables provisioned in advance by your DBA. During CDC syncs, the connector reads from these tracking tables and deletes processed change rows.

## Features

| Feature                       | Supported | Notes |
| :---------------------------- |:----------|:------|
| Full Refresh Sync             | Yes       |       |
| Incremental Sync - Append     | Yes       |       |
| Replicate Incremental Deletes | Yes       | Available when using CDC |
| Change Data Capture (CDC)     | Yes       | Trigger-based CDC implementation |
| SSL Support                   | Yes       |       |
| SSH Tunnel Connection         | Yes       |       |
| Namespaces                    | Yes       |       |

## Getting Started

#### 1. Make sure your database is accessible from the machine running Airbyte

This is dependent on your networking setup. The easiest way to verify if Airbyte is able to connect to your SAP HANA instance is by testing the connection in the UI.

#### 2. Create a dedicated read-only user with access to the relevant tables

This step is optional but highly recommended to allow for better permission control and auditing. Alternatively, you can use Airbyte with an existing user in your database.

## Change Data Capture (CDC)

The SAP HANA Enterprise connector supports Change Data Capture using a trigger-based approach. This allows the connector to capture INSERT, UPDATE, and DELETE operations on your source tables.

### How trigger-based CDC works

Unlike log-based CDC systems, this connector implements CDC using database triggers and tracking tables:

1. For each source table you want to replicate with CDC, a tracking table is created in the `_ab_cdc` schema
2. Three database triggers (INSERT, UPDATE, DELETE) are created on each source table
3. When data changes occur, the triggers automatically capture the changes into the tracking tables
4. During sync, the connector reads changes from the tracking tables and replicates them to your destination
5. After processing, the connector automatically deletes old change records to prevent unbounded growth

### CDC prerequisites

Work with your DBA to provision the following in your SAP HANA instance before enabling CDC:

- The CDC schema `_ab_cdc`
- Tracking tables in `_ab_cdc`
- Three triggers (INSERT, UPDATE, DELETE) on each source table you plan to replicate
- The connector's user with the required runtime permissions (see "Runtime permissions" under "Important considerations" below)

### Provision CDC objects using the setup script

You can use the provided Python script to automate the creation of CDC tracking tables and triggers.

#### Prerequisites for running the script

- Python 3.7 or later
- pip (Python package installer)
- Install dependencies from requirements.txt (installs hdbcli)
- Network access to your SAP HANA host and port

#### Safety and permissions

**Important notes before running the script:**

- Test in a non-production environment first
- The connector requires the fixed CDC schema `_ab_cdc` and this is not configurable
- The setup user needs setup-time permissions: `CREATE TABLE` privilege in the CDC schema and `CREATE TRIGGER` privilege on source tables
- The connector's runtime user needs different permissions: `SELECT` on source tables and `SELECT`/`DELETE` on tracking tables (setup and runtime users can be different)

#### Script files

<details>
<summary>requirements.txt</summary>

```text
hdbcli
```

</details>

<details>
<summary>cdc_setup_sap_hana.py</summary>

```python
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import argparse
import csv
import json
import os

from hdbcli import dbapi


# ===============================================
# command to run this script:
# python cdc_setup_sap_hana.py --host <HOST> --port <PORT> --user <USER> --password <PASSWORD> --schema <SOURCE_SCHEMA>
# ===============================================


def get_connection(host, port, user, password, database=None):
    """Establishes a connection to SAP HANA."""
    conn = dbapi.connect(
        address=host,
        port=port,
        user=user,
        password=password,
        databaseName=database if database else None
    )
    return conn


def check_cdc_schema_exists(conn, cdc_schema):
    """Checks if the CDC schema exists."""
    cursor = conn.cursor()
    query = "SELECT COUNT(*) FROM SYS.SCHEMAS WHERE SCHEMA_NAME = ?"
    count = 0
    try:
        cursor.execute(query, (cdc_schema,))
        count = cursor.fetchone()[0]
    except Exception as e:
        print(f"Warning: Error checking if schema exists {cdc_schema}: {e}")
    finally:
        cursor.close()
    return count > 0


def create_cdc_schema(conn, cdc_schema):
    """Creates the CDC schema."""
    cursor = conn.cursor()
    try:
        cursor.execute(f'CREATE SCHEMA "{cdc_schema}"')
        conn.commit()
        print(f"Successfully created CDC schema {cdc_schema}")
    except Exception as e:
        print(f"Error creating CDC schema {cdc_schema}: {e}")
        conn.rollback()
    finally:
        cursor.close()


def check_cdc_table_exists(conn, cdc_schema, cdc_table):
    """Checks if the specific CDC table exists."""
    cursor = conn.cursor()
    query = "SELECT COUNT(*) FROM SYS.TABLES WHERE SCHEMA_NAME = ? AND TABLE_NAME = ?"
    count = 0
    try:
        cursor.execute(query, (cdc_schema, cdc_table))
        count = cursor.fetchone()[0]
    except Exception as e:
        print(f"Warning: Error checking if table exists {cdc_schema}.{cdc_table}: {e}")
    finally:
        cursor.close()
    return count > 0


def create_cdc_table(conn, cdc_schema, cdc_table, columns_with_types):
    """Creates the CDC table with before/after columns for each source column."""
    cursor = conn.cursor()
    columns = [
        '"_ab_trigger_change_id" BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY',
        '"_ab_trigger_change_time" TIMESTAMP',
        '"_ab_trigger_operation_type" NVARCHAR(10)',
    ]

    for col in columns_with_types:
        col_name = col["name"]
        data_type = col["type"]
        safe_col_name = col_name.replace('"', '""')
        columns.append(f'"_ab_trigger_{safe_col_name}_before" {data_type}')
        columns.append(f'"_ab_trigger_{safe_col_name}_after" {data_type}')

    ddl = f'CREATE COLUMN TABLE "{cdc_schema}"."{cdc_table}" (\n    {",\n    ".join(columns)}\n)'

    try:
        cursor.execute(ddl)
        conn.commit()
        print(f"Successfully created CDC table {cdc_schema}.{cdc_table}")
    except Exception as e:
        print(f"Error creating CDC table {cdc_schema}.{cdc_table}: {e}")
        conn.rollback()
    finally:
        cursor.close()


def get_table_columns_with_types(conn, schema, table):
    """Gets column names and their full data types."""
    cursor = conn.cursor()
    query = """
        SELECT COLUMN_NAME, DATA_TYPE_NAME, LENGTH, SCALE
        FROM SYS.TABLE_COLUMNS
        WHERE SCHEMA_NAME = ? AND TABLE_NAME = ?
        ORDER BY POSITION
    """
    columns = []
    try:
        cursor.execute(query, (schema, table))
        for row in cursor.fetchall():
            col_name, data_type, length, scale = row
            full_type = data_type

            # Handle type-specific attributes
            if data_type in ["VARCHAR", "NVARCHAR", "CHAR", "NCHAR", "BINARY", "VARBINARY"]:
                if length is not None:
                    full_type += f"({length})"
            elif data_type in ["DECIMAL", "DEC"]:
                if scale is not None and scale > 0:
                    full_type += f"({length},{scale})"
                elif length is not None:
                    full_type += f"({length})"

            columns.append({"name": col_name, "type": full_type})
    except Exception as e:
        print(f"Error getting columns for {schema}.{table}: {e}")
    finally:
        cursor.close()
    return columns


def check_trigger_exists(conn, schema_name, trigger_name):
    """Checks if a trigger exists."""
    cursor = conn.cursor()
    query = "SELECT COUNT(*) FROM SYS.TRIGGERS WHERE SCHEMA_NAME = ? AND TRIGGER_NAME = ?"
    count = 0
    try:
        cursor.execute(query, (schema_name, trigger_name))
        count = cursor.fetchone()[0]
    except Exception as e:
        print(f"Warning: Error checking trigger {schema_name}.{trigger_name}: {e}")
    finally:
        cursor.close()
    return count > 0


def create_single_trigger(conn, recreate_trigger, operation_type, source_schema, source_table, cdc_schema, cdc_table, columns_with_types):
    """Creates a single trigger for the specified operation."""
    trigger_name = f"TRG_{source_schema}_{source_table}_CDC_{operation_type[:3].upper()}"
    if check_trigger_exists(conn, source_schema, trigger_name):
        if recreate_trigger:
            drop_trigger(conn, source_schema, trigger_name)
            print(f'Dropped trigger "{source_schema}"."{trigger_name}"')
        else:
            print(f"Trigger {trigger_name} exists. Skipping.")
            return

    columns = ['"_ab_trigger_change_time"', '"_ab_trigger_operation_type"']
    values = ["CURRENT_TIMESTAMP", f"'{operation_type}'"]

    if operation_type == "INSERT":
        referencing = "REFERENCING NEW AS N"
    elif operation_type == "UPDATE":
        referencing = "REFERENCING OLD AS O NEW AS N"
    elif operation_type == "DELETE":
        referencing = "REFERENCING OLD AS O"
    else:
        print(f"Invalid operation type: {operation_type}")
        return

    for col in columns_with_types:
        col_name = col["name"]
        safe_col = col_name.replace('"', '""')
        if operation_type in ["INSERT", "UPDATE"]:
            columns.append(f'"_ab_trigger_{safe_col}_after"')
            values.append(f'N."{safe_col}"')
        if operation_type in ["UPDATE", "DELETE"]:
            columns.append(f'"_ab_trigger_{safe_col}_before"')
            values.append(f'O."{safe_col}"')

    columns_str = ", ".join(columns)
    values_str = ", ".join(values)

    ddl = f"""
        CREATE TRIGGER "{source_schema}"."{trigger_name}"
        AFTER {operation_type} ON "{source_schema}"."{source_table}"
        {referencing}
        FOR EACH ROW
        BEGIN
            INSERT INTO "{cdc_schema}"."{cdc_table}" (
                {columns_str}
            )
            VALUES (
                {values_str}
            );
        END
    """

    cursor = conn.cursor()
    try:
        cursor.execute(ddl)
        conn.commit()
        print(f"Created trigger {trigger_name}")
    except Exception as e:
        print(f"Error creating trigger {trigger_name}: {e}")
        conn.rollback()
    finally:
        cursor.close()


def drop_trigger(conn, schema_name, trigger_name):
    """Drops a trigger."""
    cursor = conn.cursor()
    query = f'DROP TRIGGER "{schema_name}"."{trigger_name}"'
    try:
        cursor.execute(query)
        conn.commit()
    except Exception as e:
        print(f"Error dropping trigger {schema_name}.{trigger_name}: {e}")
        conn.rollback()
    finally:
        cursor.close()


def get_tables_from_schema(conn, schema):
    """Retrieves tables from a schema."""
    cursor = conn.cursor()
    query = "SELECT TABLE_NAME FROM SYS.TABLES WHERE SCHEMA_NAME = ? AND IS_USER_DEFINED_TYPE = 'FALSE'"
    tables = []
    try:
        cursor.execute(query, (schema,))
        tables = [{"schema": schema, "table": row[0]} for row in cursor.fetchall()]
    except Exception as e:
        print(f"Error fetching tables for schema {schema}: {e}")
    finally:
        cursor.close()
    return tables


def get_tables_from_file(input_file):
    """Reads tables from CSV/JSON file."""
    tables = []
    ext = os.path.splitext(input_file)[1].lower()
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            if ext == ".csv":
                reader = csv.DictReader(f)
                for row in reader:
                    tables.append({"schema": row["schema"], "table": row["table"]})
            elif ext == ".json":
                data = json.load(f)
                tables = [{"schema": item["schema"], "table": item["table"]} for item in data]
    except Exception as e:
        print(f"Error reading input file: {e}")
        exit(1)
    return tables


def main():
    parser = argparse.ArgumentParser(description="Create CDC triggers in SAP HANA")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--schema", help="Process all tables in a schema")
    group.add_argument("--input-file", help="CSV/JSON file with tables")
    parser.add_argument("--tables", nargs="+", help="List of table names to process (requires --schema)")
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", required=True, type=int)
    parser.add_argument("--user", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--database", help="Database name (for multi-tenant systems)")
    parser.add_argument("--cdc-schema", default="_ab_cdc")
    parser.add_argument("--recreate-triggers", action="store_true", default=False)
    args = parser.parse_args()
    print(args)

    try:
        conn = get_connection(args.host, args.port, args.user, args.password, args.database)
    except Exception as e:
        print(f"Connection failed: {e}")
        exit(1)

    # Ensure CDC schema exists
    if not check_cdc_schema_exists(conn, args.cdc_schema):
        create_cdc_schema(conn, args.cdc_schema)

    tables = []
    if args.schema and args.tables:
        # Process specific tables in the given schema
        tables = [{"schema": args.schema, "table": table} for table in args.tables]
    elif args.schema:
        # Process all tables in the schema
        tables = get_tables_from_schema(conn, args.schema)
    elif args.input_file:
        # Process tables from the input file
        tables = get_tables_from_file(args.input_file)

    for table in tables:
        source_schema = table["schema"]
        source_table = table["table"]
        cdc_table = f"_ab_trigger_{source_schema}_{source_table}"

        columns = get_table_columns_with_types(conn, source_schema, source_table)
        if not columns:
            continue

        if not check_cdc_table_exists(conn, args.cdc_schema, cdc_table):
            create_cdc_table(conn, args.cdc_schema, cdc_table, columns)

        for op in ["INSERT", "UPDATE", "DELETE"]:
            create_single_trigger(conn, args.recreate_triggers, op, source_schema, source_table, args.cdc_schema, cdc_table, columns)

    print("done")
    conn.close()


if __name__ == "__main__":
    main()
```

</details>

#### Options

- `--schema`: Process all tables in a specific schema
- `--tables`: Process only specific tables (requires `--schema`)
- `--input-file`: Process tables listed in a CSV or JSON file
- `--host`: Database host (required)
- `--port`: Database port (required)
- `--user`: Database user with setup-time permissions (required)
- `--password`: Database password (required)
- `--database`: Database name for multi-tenant systems (optional)
- `--recreate-triggers`: Drop and recreate existing triggers

#### Usage examples

##### Example: set up CDC for all tables in a schema

```bash
python cdc_setup_sap_hana.py \
  --host 01234abce-1234-56fg.us-01-hanacloud.ondemand.com \
  --port 443 \
  --user airbyte_setup_user \
  --password setup_password \
  --schema SALES
```

##### Example: set up CDC for specific tables

```bash
python cdc_setup_sap_hana.py \
  --host 01234abce-1234-56fg.us-01-hanacloud.ondemand.com \
  --port 443 \
  --user airbyte_setup_user \
  --password setup_password \
  --schema SALES \
  --tables ORDERS CUSTOMERS PRODUCTS
```

### Configuring CDC in Airbyte

After your SAP HANA server has been configured for CDC, create your SAP HANA Enterprise source in Airbyte:

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

**CDC metadata fields:** when using CDC, the connector adds the following metadata fields to each record:

- `_ab_cdc_updated_at`: Timestamp when the change occurred
- `_ab_cdc_deleted_at`: Timestamp when the record was deleted (null for non-deleted records)
- `_ab_trigger_change_time`: Timestamp from the trigger table used as the cursor

**Automatic cleanup:**

To prevent tracking tables from growing indefinitely, the connector automatically deletes processed change records during each sync. Only records older than the current checkpoint are removed.

### Important considerations

- **Setup-time permissions (one-time):** To provision the CDC infrastructure, a privileged database user (typically a DBA) needs:
  - `CREATE SCHEMA` privilege (if the `_ab_cdc` schema doesn't exist)
  - `CREATE TABLE` privilege in the `_ab_cdc` schema
  - `CREATE TRIGGER` privilege on each source table that participates in CDC
  - This setup user can be different from the runtime connector user
- **Runtime permissions (ongoing):** The database user configured in the Airbyte connector needs:
  - `SELECT` on all source tables being replicated
  - `SELECT` and `DELETE` on the CDC tracking tables (used to read and clean up processed change rows)
- Triggers add a small performance overhead to INSERT, UPDATE, and DELETE operations on source tables
- The `_ab_cdc` schema and tracking tables must not be modified manually
- If you drop and recreate a source table, you must recreate the CDC triggers and tracking table for that table

## Data type mapping

SAP HANA data types are mapped to the following data types when synchronizing data.

| SAP HANA Type  | Airbyte Type               | Notes |
| -------------- | -------------------------- | ----- |
| `BOOLEAN`      | boolean                    |       |
| `TINYINT`      | integer                    |       |
| `SMALLINT`     | integer                    |       |
| `INTEGER`      | integer                    |       |
| `BIGINT`       | integer                    |       |
| `SMALLDECIMAL` | number                     |       |
| `DECIMAL`      | number                     |       |
| `DEC`          | number                     |       |
| `REAL`         | number                     |       |
| `FLOAT`        | number                     |       |
| `DOUBLE`       | number                     |       |
| `CHAR`         | string                     |       |
| `VARCHAR`      | string                     |       |
| `NCHAR`        | string                     |       |
| `NVARCHAR`     | string                     |       |
| `ALPHANUM`     | string                     |       |
| `SHORTTEXT`    | string                     |       |
| `CLOB`         | string                     |       |
| `NCLOB`        | string                     |       |
| `TEXT`         | string                     |       |
| `BINTEXT`      | string                     |       |
| `DATE`         | date                       |       |
| `TIME`         | time_without_timezone      |       |
| `SECONDDATE`   | timestamp_without_timezone |       |
| `TIMESTAMP`    | timestamp_without_timezone |       |
| `BINARY`       | binary                     |       |
| `VARBINARY`    | binary                     |       |
| `BLOB`         | binary                     |       |
| `ST_POINT`     | binary                     |       |
| `ST_GEOMETRY`  | binary                     |       |
| `REAL_VECTOR`  | binary                     |       |

## Configuration Reference

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `host` | string | Hostname of the database. | |
| `port` | integer | Port of the database. SAP recommends port 443 for SAP HANA Cloud client connections. | `443` |
| `username` | string | The username which is used to access the database. | |
| `password` | string | The password associated with the username. | |
| `database` | string | The name of the tenant database to connect to. This is required for multi-tenant SAP HANA systems. For single-tenant systems, this can be left empty. | |
| `schemas` | array | The list of schemas to sync from. Defaults to user. Case sensitive. | |
| `filters` | array | Inclusion filters for table selection per schema. If no filters are specified for a schema, all tables in that schema will be synced. | |
| `jdbc_url_params` | string | Additional properties to pass to the JDBC URL string when connecting to the database formatted as 'key=value' pairs separated by the symbol '&'. | |
| `encryption` | object | The encryption method which is used when communicating with the database. | `{"encryption_method": "unencrypted"}` |
| `tunnel_method` | object | Whether to initiate an SSH tunnel before connecting to the database, and if so, which kind of authentication to use. | `{"tunnel_method": "NO_TUNNEL"}` |
| `cursor` | object | Configures how data is extracted from the database. | `{"cursor_method": "user_defined"}` |
| `checkpoint_target_interval_seconds` | integer | How often (in seconds) a stream should checkpoint, when possible. | `300` |
| `concurrency` | integer | Maximum number of concurrent queries to the database. | `1` |
| `check_privileges` | boolean | When enabled, the connector will query each table individually to check access privileges during schema discovery. In large schemas, this might cause schema discovery to take too long, in which case it might be advisable to disable this feature. | `true` |

### Update Method Configuration

**User Defined Cursor**:
```json
{
  "cursor_method": "user_defined"
}
```

**Change Data Capture (CDC)**:
```json
{
  "cursor_method": "cdc",
  "initial_load_timeout_hours": 8,
  "invalid_cdc_cursor_position_behavior": "Fail sync"
}
```


