# AlloyDB for PostgreSQL

This page contains the setup guide and reference information for the AlloyDB for PostgreSQL.

## Prerequisites

- For Airbyte Open Source users, [upgrade](https://docs.airbyte.com/operator-guides/upgrading-airbyte/) your Airbyte platform to version `v0.40.0-alpha` or newer
- For Airbyte Cloud (and optionally for Airbyte Open Source), ensure SSL is enabled in your environment

## Setup guide

## When to use AlloyDB with CDC

Configure AlloyDB with CDC if:

- You need a record of deletions
- Your table has a primary key but doesn't have a reasonable cursor field for incremental syncing (`updated_at`). CDC allows you to sync your table incrementally

If your goal is to maintain a snapshot of your table in the destination but the limitations prevent you from using CDC, consider using [non-CDC incremental sync](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append) and occasionally reset the data and re-sync.

If your dataset is small and you just want a snapshot of your table in the destination, consider using [Full Refresh replication](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite) for your table instead of CDC.


### Step 1: (Optional) Create a dedicated read-only user

We recommend creating a dedicated read-only user for better permission control and auditing. Alternatively, you can use an existing AlloyDB user in your database.

To create a dedicated user, run the following command:

```
CREATE USER <user_name> PASSWORD 'your_password_here';
```

Grant access to the relevant schema:

```
GRANT USAGE ON SCHEMA <schema_name> TO <user_name>
```

:::note
To replicate data from multiple AlloyDB schemas, re-run the command to grant access to all the relevant schemas. Note that you'll need to set up multiple Airbyte sources connecting to the same AlloyDB database on multiple schemas.
:::

Grant the user read-only access to the relevant tables:

```
GRANT SELECT ON ALL TABLES IN SCHEMA <schema_name> TO <user_name>;
```

Allow user to see tables created in the future:

```
ALTER DEFAULT PRIVILEGES IN SCHEMA <schema_name> GRANT SELECT ON TABLES TO <user_name>;
```

Additionally, if you plan to configure CDC for the AlloyDB source connector, grant `REPLICATION` permissions to the user:

```
ALTER USER <user_name> REPLICATION;
```

**Syncing a subset of columns​**

Currently, there is no way to sync a subset of columns using the AlloyDB source connector:

- When setting up a connection, you can only choose which tables to sync, but not columns.
- If the user can only access a subset of columns, the connection check will pass. However, the data sync will fail with a permission denied exception.

The workaround for partial table syncing is to create a view on the specific columns, and grant the user read access to that view:

```
CREATE VIEW <view_name> as SELECT <columns> FROM <table>;
```
```
GRANT SELECT ON TABLE <view_name> IN SCHEMA <schema_name> to <user_name>;
```

**Note:** The workaround works only for non-CDC setups since CDC requires data to be in tables and not views.
This issue is tracked in [#9771](https://github.com/airbytehq/airbyte/issues/9771).

### Step 2: Set up the AlloyDB connector in Airbyte

1. Log into your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) or Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **AlloyDB** from the Source type dropdown.
4. Enter a name for your source.
5. For the **Host**, **Port**, and **DB Name**, enter the hostname, port number, and name for your AlloyDB database.
6. List the **Schemas** you want to sync.
   :::note
   The schema names are case sensitive. The 'public' schema is set by default. Multiple schemas may be used at one time. No schemas set explicitly - will sync all of existing.
   :::
7. For **User** and **Password**, enter the username and password you created in [Step 1](#step-1-optional-create-a-dedicated-read-only-user).
8. To customize the JDBC connection beyond common options, specify additional supported [JDBC URL parameters](https://jdbc.postgresql.org/documentation/head/connect.html) as key-value pairs separated by the symbol & in the **JDBC URL Parameters (Advanced)** field.

   Example: key1=value1&key2=value2&key3=value3

   These parameters will be added at the end of the JDBC URL that the AirByte will use to connect to your AlloyDB database.

   The connector now supports `connectTimeout` and defaults to 60 seconds. Setting connectTimeout to 0 seconds will set the timeout to the longest time available.

   **Note:** Do not use the following keys in JDBC URL Params field as they will be overwritten by Airbyte:
   `currentSchema`, `user`, `password`, `ssl`, and `sslmode`.

   :::warning
   This is an advanced configuration option. Users are advised to use it with caution.
   :::

9. For Airbyte Open Source, toggle the switch to connect using SSL. Airbyte Cloud uses SSL by default.
10. For Replication Method, select Standard or [Logical CDC](https://www.postgresql.org/docs/10/logical-replication.html) from the dropdown. Refer to [Configuring AlloyDB connector with Change Data Capture (CDC)](#configuring-alloydb-connector-with-change-data-capture-cdc) for more information.
11. For SSH Tunnel Method, select:
    - No Tunnel for a direct connection to the database
    - SSH Key Authentication to use an RSA Private as your secret for establishing the SSH tunnel
    - Password Authentication to use a password as your secret for establishing the SSH tunnel
      Refer to [Connect via SSH Tunnel](#connect-via-ssh-tunnel​) for more information.
12. Click **Set up source**.

### Connect via SSH Tunnel​

You can connect to a AlloyDB instance via an SSH tunnel.

When using an SSH tunnel, you are configuring Airbyte to connect to an intermediate server (also called a bastion server) that has direct access to the database. Airbyte connects to the bastion and then asks the bastion to connect directly to the server.

To connect to a AlloyDB instance via an SSH tunnel:

1. While [setting up](#setup-guide) the AlloyDB source connector, from the SSH tunnel dropdown, select:
    - SSH Key Authentication to use an RSA Private as your secret for establishing the SSH tunnel
    - Password Authentication to use a password as your secret for establishing the SSH Tunnel
2. For **SSH Tunnel Jump Server Host**, enter the hostname or IP address for the intermediate (bastion) server that Airbyte will connect to.
3. For **SSH Connection Port**, enter the port on the bastion server. The default port for SSH connections is 22.
4. For **SSH Login Username**, enter the username to use when connecting to the bastion server. **Note:** This is the operating system username and not the AlloyDB username.
5. For authentication:
    - If you selected **SSH Key Authentication**, set the **SSH Private Key** to the [RSA Private Key](#generating-an-rsa-private-key​) that you are using to create the SSH connection.
    - If you selected **Password Authentication**, enter the password for the operating system user to connect to the bastion server. **Note:** This is the operating system password and not the AlloyDB password.

#### Generating an RSA Private Key​
The connector expects an RSA key in PEM format. To generate this key, run:

```
ssh-keygen -t rsa -m PEM -f myuser_rsa
```

The command produces the private key in PEM format and the public key remains in the standard format used by the `authorized_keys` file on your bastion server. Add the public key to your bastion host to the user you want to use with Airbyte. The private key is provided via copy-and-paste to the Airbyte connector configuration screen to allow it to log into the bastion server.

## Configuring AlloyDB connector with Change Data Capture (CDC)

Airbyte uses [logical replication](https://www.postgresql.org/docs/10/logical-replication.html) of the Postgres write-ahead log (WAL) to incrementally capture deletes using a replication plugin. To learn more how Airbyte implements CDC, refer to [Change Data Capture (CDC)](https://docs.airbyte.com/understanding-airbyte/cdc/)

### CDC Considerations

- Incremental sync is only supported for tables with primary keys. For tables without primary keys, use [Full Refresh sync](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite).
- Data must be in tables and not views.
- The modifications you want to capture must be made using `DELETE`/`INSERT`/`UPDATE`. For example, changes made using `TRUNCATE`/`ALTER` will not appear in logs and therefore in your destination.
- Schema changes are not supported automatically for CDC sources. Reset and resync data if you make a schema change.
- The records produced by `DELETE` statements only contain primary keys. All other data fields are unset.
- Log-based replication only works for master instances of AlloyDB.
- Using logical replication increases disk space used on the database server. The additional data is stored until it is consumed.
    - Set frequent syncs for CDC to ensure that the data doesn't fill up your disk space.
    - If you stop syncing a CDC-configured AlloyDB instance with Airbyte, delete the replication slot. Otherwise, it may fill up your disk space.

### Setting up CDC for AlloyDB

Airbyte requires a replication slot configured only for its use. Only one source should be configured that uses this replication slot. See Setting up CDC for AlloyDB for instructions.

#### Step 2: Select a replication plugin​

We recommend using a [pgoutput](https://www.postgresql.org/docs/9.6/logicaldecoding-output-plugin.html) plugin (the standard logical decoding plugin in AlloyDB). If the replication table contains multiple JSON blobs and the table size exceeds 1 GB, we recommend using a [wal2json](https://github.com/eulerto/wal2json) instead. Note that wal2json may require additional installation for Bare Metal, VMs (EC2/GCE/etc), Docker, etc. For more information read the [wal2json documentation](https://github.com/eulerto/wal2json).

#### Step 3: Create replication slot​

To create a replication slot called `airbyte_slot` using pgoutput, run:

```
SELECT pg_create_logical_replication_slot('airbyte_slot', 'pgoutput');
```

To create a replication slot called `airbyte_slot` using wal2json, run:

```
SELECT pg_create_logical_replication_slot('airbyte_slot', 'wal2json');
```

#### Step 4: Create publications and replication identities for tables​

For each table you want to replicate with CDC, add the replication identity (the method of distinguishing between rows) first:

To use primary keys to distinguish between rows, run:

```
ALTER TABLE tbl1 REPLICA IDENTITY DEFAULT;
```

After setting the replication identity, run:

```
CREATE PUBLICATION airbyte_publication FOR TABLE <tbl1, tbl2, tbl3>;`
```

The publication name is customizable. Refer to the [Postgres docs](https://www.postgresql.org/docs/10/sql-alterpublication.html) if you need to add or remove tables from your publication in the future.

:::note
You must add the replication identity before creating the publication. Otherwise, `ALTER`/`UPDATE`/`DELETE` statements may fail if AlloyDB cannot determine how to uniquely identify rows.
Also, the publication should include all the tables and only the tables that need to be synced. Otherwise, data from these tables may not be replicated correctly.
:::

:::warning
The Airbyte UI currently allows selecting any tables for CDC. If a table is selected that is not part of the publication, it will not be replicated even though it is selected. If a table is part of the publication but does not have a replication identity, that replication identity will be created automatically on the first run if the Airbyte user has the necessary permissions.
:::

#### Step 5: [Optional] Set up initial waiting time

:::warning
This is an advanced feature. Use it if absolutely necessary.
:::

The AlloyDB connector may need some time to start processing the data in the CDC mode in the following scenarios:

- When the connection is set up for the first time and a snapshot is needed
- When the connector has a lot of change logs to process

The connector waits for the default initial wait time of 5 minutes (300 seconds). Setting the parameter to a longer duration will result in slower syncs, while setting it to a shorter duration may cause the connector to not have enough time to create the initial snapshot or read through the change logs. The valid range is 120 seconds to 1200 seconds.

If you know there are database changes to be synced, but the connector cannot read those changes, the root cause may be insufficient waiting time. In that case, you can increase the waiting time (example: set to 600 seconds) to test if it is indeed the root cause. On the other hand, if you know there are no database changes, you can decrease the wait time to speed up the zero record syncs.

#### Step 6: Set up the AlloyDB source connector

In [Step 2](#step-2-set-up-the-alloydb-connector-in-airbyte) of the connector setup guide, enter the replication slot and publication you just created.

## Supported sync modes

The AlloyDB source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental Sync - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental Sync - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history)

## Supported cursors

- `TIMESTAMP`
- `TIMESTAMP_WITH_TIMEZONE`
- `TIME`
- `TIME_WITH_TIMEZONE`
- `DATE`
- `BIT`
- `BOOLEAN`
- `TINYINT/SMALLINT`
- `INTEGER`
- `BIGINT`
- `FLOAT/DOUBLE`
- `REAL`
- `NUMERIC/DECIMAL`
- `CHAR/NCHAR/NVARCHAR/VARCHAR/LONGVARCHAR`
- `BINARY/BLOB`

## Data type mapping
The AlloyDb is a fully managed PostgreSQL-compatible database service.

According to Postgres [documentation](https://www.postgresql.org/docs/14/datatype.html), Postgres data types are mapped to the following data types when synchronizing data. You can check the test values examples [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-postgres/src/test-integration/java/io/airbyte/integrations/io/airbyte/integration_tests/sources/PostgresSourceDatatypeTest.java). If you can't find the data type you are looking for or have any problems feel free to add a new test!

| Postgres Type                         | Resulting Type | Notes                                                                                                                                                                                           |
|:--------------------------------------|:---------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `bigint`                              | number         |                                                                                                                                                                                                 |
| `bigserial`, `serial8`                | number         |                                                                                                                                                                                                 |
| `bit`                                 | string         | Fixed-length bit string (e.g. "0100").                                                                                                                                                          |
| `bit varying`, `varbit`               | string         | Variable-length bit string (e.g. "0100").                                                                                                                                                       |
| `boolean`, `bool`                     | boolean        |                                                                                                                                                                                                 |
| `box`                                 | string         |                                                                                                                                                                                                 |
| `bytea`                               | string         | Variable length binary string with hex output format prefixed with "\x" (e.g. "\x6b707a").                                                                                                      |
| `character`, `char`                   | string         |                                                                                                                                                                                                 |
| `character varying`, `varchar`        | string         |                                                                                                                                                                                                 |
| `cidr`                                | string         |                                                                                                                                                                                                 |
| `circle`                              | string         |                                                                                                                                                                                                 |
| `date`                                | string         | Parsed as ISO8601 date time at midnight. CDC mode doesn't support era indicators. Issue: [#14590](https://github.com/airbytehq/airbyte/issues/14590)                                            |
| `double precision`, `float`, `float8` | number         | `Infinity`, `-Infinity`, and `NaN` are not supported and converted to `null`. Issue: [#8902](https://github.com/airbytehq/airbyte/issues/8902).                                                 |
| `hstore`                              | string         |                                                                                                                                                                                                 |
| `inet`                                | string         |                                                                                                                                                                                                 |
| `integer`, `int`, `int4`              | number         |                                                                                                                                                                                                 |
| `interval`                            | string         |                                                                                                                                                                                                 |
| `json`                                | string         |                                                                                                                                                                                                 |
| `jsonb`                               | string         |                                                                                                                                                                                                 |
| `line`                                | string         |                                                                                                                                                                                                 |
| `lseg`                                | string         |                                                                                                                                                                                                 |
| `macaddr`                             | string         |                                                                                                                                                                                                 |
| `macaddr8`                            | string         |                                                                                                                                                                                                 |
| `money`                               | number         |                                                                                                                                                                                                 |
| `numeric`, `decimal`                  | number         | `Infinity`, `-Infinity`, and `NaN` are not supported and converted to `null`. Issue: [#8902](https://github.com/airbytehq/airbyte/issues/8902).                                                 |
| `path`                                | string         |                                                                                                                                                                                                 |
| `pg_lsn`                              | string         |                                                                                                                                                                                                 |
| `point`                               | string         |                                                                                                                                                                                                 |
| `polygon`                             | string         |                                                                                                                                                                                                 |
| `real`, `float4`                      | number         |                                                                                                                                                                                                 |
| `smallint`, `int2`                    | number         |                                                                                                                                                                                                 |
| `smallserial`, `serial2`              | number         |                                                                                                                                                                                                 |
| `serial`, `serial4`                   | number         |                                                                                                                                                                                                 |
| `text`                                | string         |                                                                                                                                                                                                 |
| `time`                                | string         | Parsed as a time string without a time-zone in the ISO-8601 calendar system.                                                                                                                    |
| `timetz`                              | string         | Parsed as a time string with time-zone in the ISO-8601 calendar system.                                                                                                                         |
| `timestamp`                           | string         | Parsed as a date-time string without a time-zone in the ISO-8601 calendar system.                                                                                                               |
| `timestamptz`                         | string         | Parsed as a date-time string with time-zone in the ISO-8601 calendar system.                                                                                                                    |
| `tsquery`                             | string         |                                                                                                                                                                                                 |
| `tsvector`                            | string         |                                                                                                                                                                                                 |
| `uuid`                                | string         |                                                                                                                                                                                                 |
| `xml`                                 | string         |                                                                                                                                                                                                 |
| `enum`                                | string         |                                                                                                                                                                                                 |
| `tsrange`                             | string         |                                                                                                                                                                                                 |
| `array`                               | array          | E.g. "[\"10001\",\"10002\",\"10003\",\"10004\"]".                                                                                                                                               |
| composite type                        | string         |                                                                                                                                                                                                 |

## Limitations

- The AlloyDB source connector currently does not handle schemas larger than 4MB.
- The AlloyDB source connector does not alter the schema present in your database. Depending on the destination connected to this source, however, the schema may be altered. See the destination's documentation for more details.
- The following two schema evolution actions are currently supported:
    - Adding/removing tables without resetting the entire connection at the destination
      Caveat: In the CDC mode, adding a new table to a connection may become a temporary bottleneck. When a new table is added, the next sync job takes a full snapshot of the new table before it proceeds to handle any changes.
    - Resetting a single table within the connection without resetting the rest of the destination tables in that connection
- Changing a column data type or removing a column might break connections.


## Changelog

| Version | Date       | Pull Request                                               | Subject                                                                                                                                   |
|:--------|:-----------|:-----------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------|
| 2.0.28  | 2023-04-26 | [25401](https://github.com/airbytehq/airbyte/pull/25401)   | CDC : Upgrade Debezium to version 2.2.0                                                                                                   |
| 2.0.23  | 2023-04-19 | [24582](https://github.com/airbytehq/airbyte/pull/24582)   | CDC : Enable frequent state emission during incremental syncs + refactor for performance improvement                                      |
| 2.0.22  | 2023-04-17 | [25220](https://github.com/airbytehq/airbyte/pull/25220)   | Logging changes : Log additional metadata & clean up noisy logs                                                                           |
| 2.0.21  | 2023-04-12 | [25131](https://github.com/airbytehq/airbyte/pull/25131)   | Make Client Certificate and Client Key always show                                                                                        |
| 2.0.19  | 2023-04-11 | [24656](https://github.com/airbytehq/airbyte/pull/24656)   | CDC minor refactor                                                                                                                        |
| 2.0.17  | 2023-04-05 | [24622](https://github.com/airbytehq/airbyte/pull/24622)   | Allow streams not in CDC publication to be synced in Full-refresh mode                                                                    |
| 2.0.15  | 2023-04-04 | [24833](https://github.com/airbytehq/airbyte/pull/24833)   | Disallow the "disable" SSL Modes; fix Debezium retry policy configuration                                                                 |
| 2.0.13  | 2023-03-28 | [24166](https://github.com/airbytehq/airbyte/pull/24166)   | Fix InterruptedException bug during Debezium shutdown                                                                                     |
| 2.0.11  | 2023-03-27 | [24529](https://github.com/airbytehq/airbyte/pull/24373)   | Preparing the connector for CDC checkpointing                                                                                             |
| 2.0.10  | 2023-03-24 | [24529](https://github.com/airbytehq/airbyte/pull/24529)   | Set SSL Mode to required on strict-encrypt variant                                                                                        |
| 2.0.9   | 2023-03-22 | [20760](https://github.com/airbytehq/airbyte/pull/20760)   | Removed redundant date-time datatypes formatting                                                                                          |
| 2.0.6   | 2023-03-21 | [24271](https://github.com/airbytehq/airbyte/pull/24271)   | Fix NPE in CDC mode                                                                                                                       |
| 2.0.3   | 2023-03-21 | [24147](https://github.com/airbytehq/airbyte/pull/24275)   | Fix error with CDC checkpointing                                                                                                          |
| 2.0.2   | 2023-03-13 | [23112](https://github.com/airbytehq/airbyte/pull/21727)   | Add state checkpointing for CDC sync.                                                                                                     |
| 2.0.1   | 2023-03-08 | [23596](https://github.com/airbytehq/airbyte/pull/23596)   | For network isolation, source connector accepts a list of hosts it is allowed to connect                                                  |
| 2.0.0   | 2023-03-06 | [23112](https://github.com/airbytehq/airbyte/pull/23112)   | Upgrade Debezium version to 2.1.2                                                                                                         |
| 1.0.51  | 2023-03-02 | [23642](https://github.com/airbytehq/airbyte/pull/23642)   | Revert : Support JSONB datatype for Standard sync mode                                                                                    |
| 1.0.49  | 2023-02-27 | [21695](https://github.com/airbytehq/airbyte/pull/21695)   | Support JSONB datatype for Standard sync mode                                                                                             |
| 1.0.48  | 2023-02-24 | [23383](https://github.com/airbytehq/airbyte/pull/23383)   | Fixed bug with non readable double-quoted values within a database name or column name                                                    |
| 1.0.47  | 2023-02-22 | [22221](https://github.com/airbytehq/airbyte/pull/23138)   | Fix previous versions which doesn't verify privileges correctly, preventing CDC syncs to run.                                             |
| 1.0.46  | 2023-02-21 | [23105](https://github.com/airbytehq/airbyte/pull/23105)   | Include log levels and location information (class, method and line number) with source connector logs published to Airbyte Platform.     |
| 1.0.45  | 2023-02-09 | [22221](https://github.com/airbytehq/airbyte/pull/22371)   | Ensures that user has required privileges for CDC syncs.                                                                                  |
|         | 2023-02-15 | [23028](https://github.com/airbytehq/airbyte/pull/23028)   |                                                                                                                                           |
| 1.0.44  | 2023-02-06 | [22221](https://github.com/airbytehq/airbyte/pull/22221)   | Exclude new set of system tables when using `pg_stat_statements` extension.                                                               |
| 1.0.43  | 2023-02-06 | [21634](https://github.com/airbytehq/airbyte/pull/21634)   | Improve Standard sync performance by caching objects.                                                                                     |
| 1.0.36  | 2023-01-24 | [21825](https://github.com/airbytehq/airbyte/pull/21825)   | Put back the original change that will cause an incremental sync to error if table contains a NULL value in cursor column.                |
| 1.0.35  | 2022-12-14 | [20436](https://github.com/airbytehq/airbyte/pull/20346)   | Consolidate date/time values mapping for JDBC sources                                                                                     |
| 1.0.34  | 2022-12-13 | [20378](https://github.com/airbytehq/airbyte/pull/20378)   | Improve descriptions                                                                                                                      |
| 1.0.17  | 2022-10-31 | [18538](https://github.com/airbytehq/airbyte/pull/18538)   | Encode database name                                                                                                                      |
| 1.0.16  | 2022-10-25 | [18256](https://github.com/airbytehq/airbyte/pull/18256)   | Disable allow and prefer ssl modes in CDC mode                                                                                            |
|         | 2022-10-13 | [15535](https://github.com/airbytehq/airbyte/pull/16238)   | Update incremental query to avoid data missing when new data is inserted at the same time as a sync starts under non-CDC incremental mode |
| 1.0.15  | 2022-10-11 | [17782](https://github.com/airbytehq/airbyte/pull/17782)   | Align with Postgres source v.1.0.15                                                                                                       |
| 1.0.0   | 2022-09-15 | [16776](https://github.com/airbytehq/airbyte/pull/16776)   | Align with strict-encrypt version                                                                                                         |
| 0.1.0   | 2022-09-05 | [16323](https://github.com/airbytehq/airbyte/pull/16323)   | Initial commit. Based on source-postgres v.1.0.7                                                                                          |
