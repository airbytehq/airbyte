# Postgres

This page contains the setup guide and reference information for the Postgres source connector for CDC and non-CDC workflows.

## When to use Postgres with CDC

Configure Postgres with CDC if:

- You need a record of deletions
- Your table has a primary key but doesn't have a reasonable cursor field for incremental syncing (`updated_at`). CDC allows you to sync your table incrementally

If your goal is to maintain a snapshot of your table in the destination but the limitations prevent you from using CDC, consider using [non-CDC incremental sync](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append) and occasionally reset the data and re-sync.

If your dataset is small and you just want a snapshot of your table in the destination, consider using [Full Refresh replication](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite) for your table instead of CDC.

## Prerequisites

- For Airbyte Open Source users, [upgrade](https://docs.airbyte.com/operator-guides/upgrading-airbyte/) your Airbyte platform to version `v0.40.0-alpha` or newer
- Use Postgres v9.3.x or above for non-CDC workflows and Postgres v10 or above for CDC workflows
- For Airbyte Cloud (and optionally for Airbyte Open Source), ensure SSL is enabled in your environment

## Setup guide

### Step 1: (Optional) Create a dedicated read-only user

We recommend creating a dedicated read-only user for better permission control and auditing. Alternatively, you can use an existing Postgres user in your database.

To create a dedicated user, run the following command:

```
CREATE USER <user_name> PASSWORD 'your_password_here';
```

Grant access to the relevant schema:

```
GRANT USAGE ON SCHEMA <schema_name> TO <user_name>
```

:::note
To replicate data from multiple Postgres schemas, re-run the command to grant access to all the relevant schemas. Note that you'll need to set up multiple Airbyte sources connecting to the same Postgres database on multiple schemas.
:::

Grant the user read-only access to the relevant tables:

```
GRANT SELECT ON ALL TABLES IN SCHEMA <schema_name> TO <user_name>;
```

Allow user to see tables created in the future:

```
ALTER DEFAULT PRIVILEGES IN SCHEMA <schema_name> GRANT SELECT ON TABLES TO <user_name>;
```

Additionally, if you plan to configure CDC for the Postgres source connector, grant `REPLICATION` permissions to the user:

```
ALTER USER <user_name> REPLICATION;
```


**Syncing a subset of columns​**

Currently, there is no way to sync a subset of columns using the Postgres source connector:

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

### Step 2: Set up the Postgres connector in Airbyte

1. Log into your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) or Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Postgres** from the Source type dropdown.
4. Enter a name for your source.
5. For the **Host**, **Port**, and **DB Name**, enter the hostname, port number, and name for your Postgres database.
6. List the **Schemas** you want to sync.
   :::note
   The schema names are case sensitive. The 'public' schema is set by default. Multiple schemas may be used at one time. No schemas set explicitly - will sync all of existing.
   :::
7. For **User** and **Password**, enter the username and password you created in [Step 1](#step-1-optional-create-a-dedicated-read-only-user).
8. To customize the JDBC connection beyond common options, specify additional supported [JDBC URL parameters](https://jdbc.postgresql.org/documentation/head/connect.html) as key-value pairs separated by the symbol & in the **JDBC URL Parameters (Advanced)** field.

   Example: key1=value1&key2=value2&key3=value3

   These parameters will be added at the end of the JDBC URL that the AirByte will use to connect to your Postgres database.

   The connector now supports `connectTimeout` and defaults to 60 seconds. Setting connectTimeout to 0 seconds will set the timeout to the longest time available.

   **Note:** Do not use the following keys in JDBC URL Params field as they will be overwritten by Airbyte:
   `currentSchema`, `user`, `password`, `ssl`, and `sslmode`.

   :::warning
   This is an advanced configuration option. Users are advised to use it with caution.
   :::

9. For Airbyte Open Source, toggle the switch to connect using SSL. For Airbyte Cloud uses SSL by default.
10. For SSL Modes, select:
    - **disable** to disable encrypted communication between Airbyte and the source
    - **allow** to enable encrypted communication only when required by the source
    - **prefer** to allow unencrypted communication only when the source doesn't support encryption
    - **require** to always require encryption. Note: The connection will fail if the source doesn't support encryption.
    - **verify-ca** to always require encryption and verify that the source has a valid SSL certificate
    - **verify-full** to always require encryption and verify the identity of the source
11. For Replication Method, select Standard or [Logical CDC](https://www.postgresql.org/docs/10/logical-replication.html) from the dropdown. Refer to [Configuring Postgres connector with Change Data Capture (CDC)](#configuring-postgres-connector-with-change-data-capture-cdc) for more information.
12. For SSH Tunnel Method, select:

    - **No Tunnel** for a direct connection to the database
    - **SSH Key Authentication** to use an RSA Private as your secret for establishing the SSH tunnel
    - **Password Authentication** to use a password as your secret for establishing the SSH tunnel

    :::warning
    Since Airbyte Cloud requires encrypted communication, select **SSH Key Authentication** or **Password Authentication** if you selected **disable**, **allow**, or **prefer** as the **SSL Mode**; otherwise, the connection will fail.
    :::

Refer to [Connect via SSH Tunnel](#connect-via-ssh-tunnel​) for more information. 13. Click **Set up source**.

### Connect via SSH Tunnel​

You can connect to a Postgres instance via an SSH tunnel.

When using an SSH tunnel, you are configuring Airbyte to connect to an intermediate server (also called a bastion or a jump server) that has direct access to the database. Airbyte connects to the bastion and then asks the bastion to connect directly to the server.

To connect to a Postgres instance via an SSH tunnel:

1. While [setting up](#setup-guide) the Postgres source connector, from the SSH tunnel dropdown, select:
   - SSH Key Authentication to use a private as your secret for establishing the SSH tunnel
   - Password Authentication to use a password as your secret for establishing the SSH Tunnel
2. For **SSH Tunnel Jump Server Host**, enter the hostname or IP address for the intermediate (bastion) server that Airbyte will connect to.
3. For **SSH Connection Port**, enter the port on the bastion server. The default port for SSH connections is 22.
4. For **SSH Login Username**, enter the username to use when connecting to the bastion server. **Note:** This is the operating system username and not the Postgres username.
5. For authentication:
   - If you selected **SSH Key Authentication**, set the **SSH Private Key** to the [private Key](#generating-a-private-key​) that you are using to create the SSH connection.
   - If you selected **Password Authentication**, enter the password for the operating system user to connect to the bastion server. **Note:** This is the operating system password and not the Postgres password.

#### Generating a private Key​

The connector supports any SSH compatible key format such as RSA or Ed25519. To generate an RSA key, for example, run:

```
ssh-keygen -t rsa -m PEM -f myuser_rsa
```

The command produces the private key in PEM format and the public key remains in the standard format used by the `authorized_keys` file on your bastion server. Add the public key to your bastion host to the user you want to use with Airbyte. The private key is provided via copy-and-paste to the Airbyte connector configuration screen to allow it to log into the bastion server.

## Configuring Postgres connector with Change Data Capture (CDC)

Airbyte uses [logical replication](https://www.postgresql.org/docs/10/logical-replication.html) of the Postgres write-ahead log (WAL) to incrementally capture deletes using a replication plugin. To learn more how Airbyte implements CDC, refer to [Change Data Capture (CDC)](https://docs.airbyte.com/understanding-airbyte/cdc/)

### CDC Considerations

- Incremental sync is only supported for tables with primary keys. For tables without primary keys, use [Full Refresh sync](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite).
- Data must be in tables and not views. If you require data synchronization from a view, you would need to create a new connection with `Standard` as `Replication Method`.
- The modifications you want to capture must be made using `DELETE`/`INSERT`/`UPDATE`. For example, changes made using `TRUNCATE`/`ALTER` will not appear in logs and therefore in your destination.
- Schema changes are not supported automatically for CDC sources. Reset and resync data if you make a schema change.
- The records produced by `DELETE` statements only contain primary keys. All other data fields are unset.
- Log-based replication only works for master instances of Postgres.  CDC cannot be run from a read-replica of your primary database.
- An Airbyte database source using CDC replication can only be used with a single Airbyte destination.  This is due to how Postgres CDC is implemented - each destination would recieve only part of the data available in the replication slot.
- Using logical replication increases disk space used on the database server. The additional data is stored until it is consumed.
  - Set frequent syncs for CDC to ensure that the data doesn't fill up your disk space.
  - If you stop syncing a CDC-configured Postgres instance with Airbyte, delete the replication slot. Otherwise, it may fill up your disk space.

:::note Connector configuration are supported only on primary/master db host/servers. Do not point connector configuration to replica db hosts, it will not work.. :::

### Setting up CDC for Postgres​

Airbyte requires a replication slot configured only for its use. Only one source should be configured that uses this replication slot. See Setting up CDC for Postgres for instructions.

#### Step 1: Enable logical replication​

To enable logical replication on bare metal, VMs (EC2/GCE/etc), or Docker, configure the following parameters in the [postgresql.conf file](https://www.postgresql.org/docs/current/config-setting.html) for your Postgres database:

| Parameter             | Description                                                                    | Set value to                                                                                                                       |
|-----------------------|--------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------|
| wal_level             | Type of coding used within the Postgres write-ahead log                        | logical                                                                                                                            |
| max_wal_senders       | The maximum number of processes used for handling WAL changes                  | Min: 1                                                                                                                             |
| max_replication_slots | The maximum number of replication slots that are allowed to stream WAL changes | 1 (if Airbyte is the only service reading subscribing to WAL changes. More than 1 if other services are also reading from the WAL) |

To enable logical replication on AWS Postgres RDS or Aurora​:

1. Go to the Configuration tab for your DB cluster.
2. Find your cluster parameter group. Either edit the parameters for this group or create a copy of this parameter group to edit. If you create a copy, change your cluster's parameter group before restarting.
3. Within the parameter group page, search for `rds.logical_replication`. Select this row and click Edit parameters. Set this value to 1.
4. Wait for a maintenance window to automatically restart the instance or restart it manually.

To enable logical replication on Azure Database for Postgres​:

Change the replication mode of your Postgres DB on Azure to `logical` using the **Replication** menu of your PostgreSQL instance in the Azure Portal. Alternatively, use the Azure CLI to run the following command:

```
az postgres server configuration set --resource-group group --server-name server --name azure.replication_support --value logical
```

```
az postgres server restart --resource-group group --name server
```

#### Step 2: Create replication slot​

Airbyte currently supports pgoutput plugin only. To create a replication slot called `airbyte_slot` using pgoutput, run:

```
SELECT pg_create_logical_replication_slot('airbyte_slot', 'pgoutput');
```

#### Step 3: Create publications and replication identities for tables​

For each table you want to replicate with CDC, add the replication identity (the method of distinguishing between rows) first:

To use primary keys to distinguish between rows for tables that don't have a large amount of data per row, run:

```
ALTER TABLE tbl1 REPLICA IDENTITY DEFAULT;
```

In case your tables use data types that support [TOAST](https://www.postgresql.org/docs/current/storage-toast.html) and have very large field values, use:

```
ALTER TABLE tbl1 REPLICA IDENTITY FULL;
```

After setting the replication identity, run:

```
CREATE PUBLICATION airbyte_publication FOR TABLE <tbl1, tbl2, tbl3>;`
```

The publication name is customizable. Refer to the [Postgres docs](https://www.postgresql.org/docs/10/sql-alterpublication.html) if you need to add or remove tables from your publication in the future.

:::note
You must add the replication identity before creating the publication. Otherwise, `ALTER`/`UPDATE`/`DELETE` statements may fail if Postgres cannot determine how to uniquely identify rows.
Also, the publication should include all the tables and only the tables that need to be synced. Otherwise, data from these tables may not be replicated correctly.
:::

:::warning
The Airbyte UI currently allows selecting any tables for CDC. If a table is selected that is not part of the publication, it will not be replicated even though it is selected. If a table is part of the publication but does not have a replication identity, that replication identity will be created automatically on the first run if the Airbyte user has the necessary permissions.
:::

#### Step 4: [Optional] Set up initial waiting time

:::warning
This is an advanced feature. Use it if absolutely necessary.
:::

The Postgres connector may need some time to start processing the data in the CDC mode in the following scenarios:

- When the connection is set up for the first time and a snapshot is needed
- When the connector has a lot of change logs to process

The connector waits for the default initial wait time of 5 minutes (300 seconds). Setting the parameter to a longer duration will result in slower syncs, while setting it to a shorter duration may cause the connector to not have enough time to create the initial snapshot or read through the change logs. The valid range is 120 seconds to 1200 seconds.

If you know there are database changes to be synced, but the connector cannot read those changes, the root cause may be insufficient waiting time. In that case, you can increase the waiting time (example: set to 600 seconds) to test if it is indeed the root cause. On the other hand, if you know there are no database changes, you can decrease the wait time to speed up the zero record syncs.

#### Step 5: Set up the Postgres source connector

In [Step 2](#step-2-set-up-the-postgres-connector-in-airbyte) of the connector setup guide, enter the replication slot and publication you just created.

## Supported sync modes

The Postgres source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

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

According to Postgres [documentation](https://www.postgresql.org/docs/14/datatype.html), Postgres data types are mapped to the following data types when synchronizing data. You can check the test values examples [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-postgres/src/test-integration/java/io/airbyte/integrations/io/airbyte/integration_tests/sources/PostgresSourceDatatypeTest.java). If you can't find the data type you are looking for or have any problems feel free to add a new test!

| Postgres Type                         | Resulting Type | Notes                                                                                                                                                 |
|---------------------------------------|----------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| `bigint`                              | number         |                                                                                                                                                       |
| `bigserial`, `serial8`                | number         |                                                                                                                                                       |
| `bit`                                 | string         | Fixed-length bit string (e.g. "0100").                                                                                                                |
| `bit varying`, `varbit`               | string         | Variable-length bit string (e.g. "0100").                                                                                                             |
| `boolean`, `bool`                     | boolean        |                                                                                                                                                       |
| `box`                                 | string         |                                                                                                                                                       |
| `bytea`                               | string         | Variable length binary string with hex output format prefixed with "\x" (e.g. "\x6b707a").                                                            |
| `character`, `char`                   | string         |                                                                                                                                                       |
| `character varying`, `varchar`        | string         |                                                                                                                                                       |
| `cidr`                                | string         |                                                                                                                                                       |
| `circle`                              | string         |                                                                                                                                                       |
| `date`                                | string         | Parsed as ISO8601 date time at midnight. CDC mode doesn't support era indicators. Issue: [#14590](https://github.com/airbytehq/airbyte/issues/14590)  |
| `double precision`, `float`, `float8` | number         | `Infinity`, `-Infinity`, and `NaN` are not supported and converted to `null`. Issue: [#8902](https://github.com/airbytehq/airbyte/issues/8902).       |
| `hstore`                              | string         |                                                                                                                                                       |
| `inet`                                | string         |                                                                                                                                                       |
| `integer`, `int`, `int4`              | number         |                                                                                                                                                       |
| `interval`                            | string         |                                                                                                                                                       |
| `json`                                | string         |                                                                                                                                                       |
| `jsonb`                               | string         |                                                                                                                                                       |
| `line`                                | string         |                                                                                                                                                       |
| `lseg`                                | string         |                                                                                                                                                       |
| `macaddr`                             | string         |                                                                                                                                                       |
| `macaddr8`                            | string         |                                                                                                                                                       |
| `money`                               | number         |                                                                                                                                                       |
| `numeric`, `decimal`                  | number         | `Infinity`, `-Infinity`, and `NaN` are not supported and converted to `null`. Issue: [#8902](https://github.com/airbytehq/airbyte/issues/8902).       |
| `path`                                | string         |                                                                                                                                                       |
| `pg_lsn`                              | string         |                                                                                                                                                       |
| `point`                               | string         |                                                                                                                                                       |
| `polygon`                             | string         |                                                                                                                                                       |
| `real`, `float4`                      | number         |                                                                                                                                                       |
| `smallint`, `int2`                    | number         |                                                                                                                                                       |
| `smallserial`, `serial2`              | number         |                                                                                                                                                       |
| `serial`, `serial4`                   | number         |                                                                                                                                                       |
| `text`                                | string         |                                                                                                                                                       |
| `time`                                | string         | Parsed as a time string without a time-zone in the ISO-8601 calendar system.                                                                          |
| `timetz`                              | string         | Parsed as a time string with time-zone in the ISO-8601 calendar system.                                                                               |
| `timestamp`                           | string         | Parsed as a date-time string without a time-zone in the ISO-8601 calendar system.                                                                     |
| `timestamptz`                         | string         | Parsed as a date-time string with time-zone in the ISO-8601 calendar system.                                                                          |
| `tsquery`                             | string         |                                                                                                                                                       |
| `tsvector`                            | string         |                                                                                                                                                       |
| `uuid`                                | string         |                                                                                                                                                       |
| `xml`                                 | string         |                                                                                                                                                       |
| `enum`                                | string         |                                                                                                                                                       |
| `tsrange`                             | string         |                                                                                                                                                       |
| `array`                               | array          | E.g. "[\"10001\",\"10002\",\"10003\",\"10004\"]".                                                                                                     |
| composite type                        | string         |                                                                                                                                                       |

## Limitations

- The Postgres source connector currently does not handle schemas larger than 4MB.
- The Postgres source connector does not alter the schema present in your database. Depending on the destination connected to this source, however, the schema may be altered. See the destination's documentation for more details.
- The following two schema evolution actions are currently supported:
  - Adding/removing tables without resetting the entire connection at the destination
    Caveat: In the CDC mode, adding a new table to a connection may become a temporary bottleneck. When a new table is added, the next sync job takes a full snapshot of the new table before it proceeds to handle any changes.
  - Resetting a single table within the connection without resetting the rest of the destination tables in that connection
- Changing a column data type or removing a column might break connections.

## Troubleshooting

### Sync data from Postgres hot standby server

When the connector is reading from a Postgres replica that is configured as a Hot Standby, any update from the primary server will terminate queries on the replica after a certain amount of time, default to 30 seconds. This default waiting time is not enough to sync any meaning amount of data. See the `Handling Query Conflicts` section in the Postgres [documentation](https://www.postgresql.org/docs/14/hot-standby.html#HOT-STANDBY-CONFLICT) for detailed explanation.

Here is the typical exception:

```
Caused by: org.postgresql.util.PSQLException: FATAL: terminating connection due to conflict with recovery
    Detail: User query might have needed to see row versions that must be removed.
    Hint: In a moment you should be able to reconnect to the database and repeat your command.
```

Possible solutions include:

- [Recommended] Set [`hot_standby_feedback`](https://www.postgresql.org/docs/14/runtime-config-replication.html#GUC-HOT-STANDBY-FEEDBACK) to `true` on the replica server. This parameter will prevent the primary server from deleting the write-ahead logs when the replica is busy serving user queries. However, the downside is that the write-ahead log will increase in size.
- [Recommended] Sync data when there is no update running in the primary server, or sync data from the primary server.
- [Not Recommended] Increase [`max_standby_archive_delay`](https://www.postgresql.org/docs/14/runtime-config-replication.html#GUC-MAX-STANDBY-ARCHIVE-DELAY) and [`max_standby_streaming_delay`](https://www.postgresql.org/docs/14/runtime-config-replication.html#GUC-MAX-STANDBY-STREAMING-DELAY) to be larger than the amount of time needed to complete the data sync. However, it is usually hard to tell how much time it will take to sync all the data. This approach is not very practical.

### Under CDC incremental mode, there are still full refresh syncs

Normally under the CDC mode, the Postgres source will first run a full refresh sync to read the snapshot of all the existing data, and all subsequent runs will only be incremental syncs reading from the write-ahead logs (WAL). However, occasionally, you may see full refresh syncs after the initial run. When this happens, you will see the following log:

> Saved offset is before Replication slot's confirmed_flush_lsn, Airbyte will trigger sync from scratch

The root causes is that the WALs needed for the incremental sync has been removed by Postgres. This can occur under the following scenarios:
        
- When there are lots of database updates resulting in more WAL files than allowed in the `pg_wal` directory, Postgres will purge or archive the WAL files. This scenario is preventable. Possible solutions include:
  - Sync the data source more frequently. The downside is that more computation resources will be consumed, leading to a higher Airbyte bill.
  - Set a higher `wal_keep_size`. If no unit is provided, it is in megabytes, and the default is `0`. See detailed documentation [here](https://www.postgresql.org/docs/current/runtime-config-replication.html#GUC-WAL-KEEP-SIZE). The downside of this approach is that more disk space will be needed.
- When the Postgres connector successfully reads the WAL and acknowledges it to Postgres, but the destination connector fails to consume the data, the Postgres connector will try to read the same WAL again, which may have been removed by Postgres, since the WAL record is already acknowledged. This scenario is rare, because it can happen, and currently there is no way to prevent it. The correct behavior is to perform a full refresh.

### Temporary File Size Limit

Some larger tables may encounter an error related to the temporary file size limit such as `temporary file size exceeds temp_file_limit`. To correct this error increase the [temp_file_limit](https://postgresqlco.nf/doc/en/param/temp_file_limit/).


## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                                                                                                    |
|:--------|:-----------|:---------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 2.0.33  | 2023-06-01 | [26873](https://github.com/airbytehq/airbyte/pull/26873) | Add prepareThreshold=0 to JDBC url to mitigate PGBouncer prepared statement [X] already exists.                                                                            |
| 2.0.32  | 2023-05-31 | [26810](https://github.com/airbytehq/airbyte/pull/26810) | Remove incremental sync estimate from Postgres to increase performance.                                                                                                    |
| 2.0.31  | 2023-05-25 | [26633](https://github.com/airbytehq/airbyte/pull/26633) | Collect and log information related to full vacuum operation in db                                                                                                         |
| 2.0.30  | 2023-05-25 | [26473](https://github.com/airbytehq/airbyte/pull/26473) | CDC : Limit queue size                                                                                                                                                     |
| 2.0.29  | 2023-05-18 | [25898](https://github.com/airbytehq/airbyte/pull/25898) | Translate Numeric values without decimal, e.g: NUMERIC(38,0), as BigInt instead of Double                                                                                  |
| 2.0.28  | 2023-04-27 | [25401](https://github.com/airbytehq/airbyte/pull/25401) | CDC : Upgrade Debezium to version 2.2.0                                                                                                                                    |
| 2.0.27  | 2023-04-26 | [24971](https://github.com/airbytehq/airbyte/pull/24971) | Emit stream status updates                                                                                                                                                 |
| 2.0.26  | 2023-04-26 | [25560](https://github.com/airbytehq/airbyte/pull/25560) | Revert some logging changes                                                                                                                                                |
| 2.0.25  | 2023-04-24 | [25459](https://github.com/airbytehq/airbyte/pull/25459) | Better logging formatting                                                                                                                                                  |
| 2.0.24  | 2023-04-19 | [25345](https://github.com/airbytehq/airbyte/pull/25345) | Logging : Log database indexes per stream                                                                                                                                  |
| 2.0.23  | 2023-04-19 | [24582](https://github.com/airbytehq/airbyte/pull/24582) | CDC : Enable frequent state emission during incremental syncs + refactor for performance improvement                                                                       |
| 2.0.22  | 2023-04-17 | [25220](https://github.com/airbytehq/airbyte/pull/25220) | Logging changes : Log additional metadata & clean up noisy logs                                                                                                            |
| 2.0.21  | 2023-04-12 | [25131](https://github.com/airbytehq/airbyte/pull/25131) | Make Client Certificate and Client Key always show                                                                                                                         |
| 2.0.20  | 2023-04-11 | [24859](https://github.com/airbytehq/airbyte/pull/24859) | Removed SSL toggle and rely on SSL mode dropdown to enable/disable SSL                                                                                                     |
| 2.0.19  | 2023-04-11 | [24656](https://github.com/airbytehq/airbyte/pull/24656) | CDC minor refactor                                                                                                                                                         |
| 2.0.18  | 2023-04-06 | [24820](https://github.com/airbytehq/airbyte/pull/24820) | Fix data loss bug during an initial failed non-CDC incremental sync                                                                                                        |
| 2.0.17  | 2023-04-05 | [24622](https://github.com/airbytehq/airbyte/pull/24622) | Allow streams not in CDC publication to be synced in Full-refresh mode                                                                                                     |
| 2.0.16  | 2023-04-05 | [24895](https://github.com/airbytehq/airbyte/pull/24895) | Fix spec for cloud                                                                                                                                                         |
| 2.0.15  | 2023-04-04 | [24833](https://github.com/airbytehq/airbyte/pull/24833) | Fix Debezium retry policy configuration                                                                                                                                    |
| 2.0.14  | 2023-04-03 | [24609](https://github.com/airbytehq/airbyte/pull/24609) | Disallow the "disable" SSL Modes                                                                                                                                           |
| 2.0.13  | 2023-03-28 | [24166](https://github.com/airbytehq/airbyte/pull/24166) | Fix InterruptedException bug during Debezium shutdown                                                                                                                      |
| 2.0.12  | 2023-03-27 | [24529](https://github.com/airbytehq/airbyte/pull/24373) | Add CDC checkpoint state messages                                                                                                                                          |
| 2.0.11  | 2023-03-23 | [24446](https://github.com/airbytehq/airbyte/pull/24446) | Set default SSL Mode to require in strict-encrypt                                                                                                                          |
| 2.0.10  | 2023-03-23 | [24417](https://github.com/airbytehq/airbyte/pull/24417) | Add field groups and titles to improve display of connector setup form                                                                                                     |
| 2.0.9   | 2023-03-22 | [20760](https://github.com/airbytehq/airbyte/pull/20760) | Removed redundant date-time datatypes formatting                                                                                                                           |
| 2.0.8   | 2023-03-22 | [24255](https://github.com/airbytehq/airbyte/pull/24255) | Add field groups and titles to improve display of connector setup form                                                                                                     |
| 2.0.7   | 2023-03-21 | [24207](https://github.com/airbytehq/airbyte/pull/24207) | Fix incorrect schema change warning in CDC mode                                                                                                                            |
| 2.0.6   | 2023-03-21 | [24271](https://github.com/airbytehq/airbyte/pull/24271) | Fix NPE in CDC mode                                                                                                                                                        |
| 2.0.5   | 2023-03-21 | [21533](https://github.com/airbytehq/airbyte/pull/21533) | Add integration with datadog                                                                                                                                               |
| 2.0.4   | 2023-03-21 | [24147](https://github.com/airbytehq/airbyte/pull/24275) | Fix error with CDC checkpointing                                                                                                                                           |
| 2.0.3   | 2023-03-14 | [24000](https://github.com/airbytehq/airbyte/pull/24000) | Removed check method call on read.                                                                                                                                         |
| 2.0.2   | 2023-03-13 | [23112](https://github.com/airbytehq/airbyte/pull/21727) | Add state checkpointing for CDC sync.                                                                                                                                      |
| 2.0.0   | 2023-03-06 | [23112](https://github.com/airbytehq/airbyte/pull/23112) | Upgrade Debezium version to 2.1.2                                                                                                                                          |
| 1.0.51  | 2023-03-02 | [23642](https://github.com/airbytehq/airbyte/pull/23642) | Revert : Support JSONB datatype for Standard sync mode                                                                                                                     |
| 1.0.50  | 2023-02-27 | [21695](https://github.com/airbytehq/airbyte/pull/21695) | Support JSONB datatype for Standard sync mode                                                                                                                              |
| 1.0.49  | 2023-02-24 | [23383](https://github.com/airbytehq/airbyte/pull/23383) | Fixed bug with non readable double-quoted values within a database name or column name                                                                                     |
| 1.0.48  | 2023-02-23 | [22623](https://github.com/airbytehq/airbyte/pull/22623) | Increase max fetch size of JDBC streaming mode                                                                                                                             |
| 1.0.47  | 2023-02-22 | [22221](https://github.com/airbytehq/airbyte/pull/23138) | Fix previous versions which doesn't verify privileges correctly, preventing CDC syncs to run.                                                                              |
| 1.0.46  | 2023-02-21 | [23105](https://github.com/airbytehq/airbyte/pull/23105) | Include log levels and location information (class, method and line number) with source connector logs published to Airbyte Platform.                                      |
| 1.0.45  | 2023-02-09 | [22221](https://github.com/airbytehq/airbyte/pull/22371) | Ensures that user has required privileges for CDC syncs.                                                                                                                   |
|         | 2023-02-15 | [23028](https://github.com/airbytehq/airbyte/pull/23028) |                                                                                                                                                                            |
| 1.0.44  | 2023-02-06 | [22221](https://github.com/airbytehq/airbyte/pull/22221) | Exclude new set of system tables when using `pg_stat_statements` extension.                                                                                                |
| 1.0.43  | 2023-02-06 | [21634](https://github.com/airbytehq/airbyte/pull/21634) | Improve Standard sync performance by caching objects.                                                                                                                      |
| 1.0.42  | 2023-01-23 | [21523](https://github.com/airbytehq/airbyte/pull/21523) | Check for null in cursor values before replacing.                                                                                                                          |
| 1.0.41  | 2023-01-25 | [20939](https://github.com/airbytehq/airbyte/pull/20939) | Adjust batch selection memory limits databases.                                                                                                                            |
| 1.0.40  | 2023-01-24 | [21825](https://github.com/airbytehq/airbyte/pull/21825) | Put back the original change that will cause an incremental sync to error if table contains a NULL value in cursor column.                                                 |
| 1.0.39  | 2023-01-20 | [21683](https://github.com/airbytehq/airbyte/pull/21683) | Speed up esmtimates for trace messages in non-CDC mode.                                                                                                                    |
| 1.0.38  | 2023-01-17 | [20436](https://github.com/airbytehq/airbyte/pull/20346) | Consolidate date/time values mapping for JDBC sources                                                                                                                      |
| 1.0.37  | 2023-01-17 | [20783](https://github.com/airbytehq/airbyte/pull/20783) | Emit estimate trace messages for non-CDC mode.                                                                                                                             |
| 1.0.36  | 2023-01-11 | [21003](https://github.com/airbytehq/airbyte/pull/21003) | Handle null values for array data types in CDC mode gracefully.                                                                                                            |
| 1.0.35  | 2023-01-04 | [20469](https://github.com/airbytehq/airbyte/pull/20469) | Introduce feature to make LSN commit behaviour configurable.                                                                                                               |
| 1.0.34  | 2022-12-13 | [20378](https://github.com/airbytehq/airbyte/pull/20378) | Improve descriptions                                                                                                                                                       |
| 1.0.33  | 2022-12-12 | [18959](https://github.com/airbytehq/airbyte/pull/18959) | CDC : Don't timeout if snapshot is not complete.                                                                                                                           |
| 1.0.32  | 2022-12-12 | [20192](https://github.com/airbytehq/airbyte/pull/20192) | Only throw a warning if cursor column contains null values.                                                                                                                |
| 1.0.31  | 2022-12-02 | [19889](https://github.com/airbytehq/airbyte/pull/19889) | Check before each sync and stop if an incremental sync cursor column contains a null value.                                                                                |
|         | 2022-12-02 | [19985](https://github.com/airbytehq/airbyte/pull/19985) | Reenable incorrectly-disabled `wal2json` CDC plugin                                                                                                                        |
| 1.0.30  | 2022-11-29 | [19024](https://github.com/airbytehq/airbyte/pull/19024) | Skip tables from schema where user do not have Usage permission during discovery.                                                                                          |
| 1.0.29  | 2022-11-29 | [19623](https://github.com/airbytehq/airbyte/pull/19623) | Mark PSQLException related to using replica that is configured as a hot standby server as config error.                                                                    |
| 1.0.28  | 2022-11-28 | [19514](https://github.com/airbytehq/airbyte/pull/19514) | Adjust batch selection memory limits databases.                                                                                                                            |
| 1.0.27  | 2022-11-28 | [16990](https://github.com/airbytehq/airbyte/pull/16990) | Handle arrays data types                                                                                                                                                   |
| 1.0.26  | 2022-11-18 | [19551](https://github.com/airbytehq/airbyte/pull/19551) | Fixes bug with ssl modes                                                                                                                                                   |
| 1.0.25  | 2022-11-16 | [19004](https://github.com/airbytehq/airbyte/pull/19004) | Use Debezium heartbeats to improve CDC replication of large databases.                                                                                                     |
| 1.0.24  | 2022-11-07 | [19291](https://github.com/airbytehq/airbyte/pull/19291) | Default timeout is reduced from 1 min to 10sec                                                                                                                             |
| 1.0.23  | 2022-11-07 | [19025](https://github.com/airbytehq/airbyte/pull/19025) | Stop enforce SSL if ssl mode is disabled                                                                                                                                   |
| 1.0.22  | 2022-10-31 | [18538](https://github.com/airbytehq/airbyte/pull/18538) | Encode database name                                                                                                                                                       |
| 1.0.21  | 2022-10-25 | [18256](https://github.com/airbytehq/airbyte/pull/18256) | Disable allow and prefer ssl modes in CDC mode                                                                                                                             |
| 1.0.20  | 2022-10-25 | [18383](https://github.com/airbytehq/airbyte/pull/18383) | Better SSH error handling + messages                                                                                                                                       |
| 1.0.19  | 2022-10-21 | [18263](https://github.com/airbytehq/airbyte/pull/18263) | Fixes bug introduced in [15833](https://github.com/airbytehq/airbyte/pull/15833) and adds better error messaging for SSH tunnel in Destinations                            |
| 1.0.18  | 2022-10-19 | [18087](https://github.com/airbytehq/airbyte/pull/18087) | Better error messaging for configuration errors (SSH configs, choosing an invalid cursor)                                                                                  |
| 1.0.17  | 2022-10-17 | [18041](https://github.com/airbytehq/airbyte/pull/18041) | Fixes bug introduced 2022-09-12 with SshTunnel, handles iterator exception properly                                                                                        |
| 1.0.16  | 2022-10-13 | [15535](https://github.com/airbytehq/airbyte/pull/16238) | Update incremental query to avoid data missing when new data is inserted at the same time as a sync starts under non-CDC incremental mode                                  |
| 1.0.15  | 2022-10-11 | [17782](https://github.com/airbytehq/airbyte/pull/17782) | Handle 24:00:00 value for Time column                                                                                                                                      |
| 1.0.14  | 2022-10-03 | [17515](https://github.com/airbytehq/airbyte/pull/17515) | Fix an issue preventing connection using client certificate                                                                                                                |
| 1.0.13  | 2022-10-01 | [17459](https://github.com/airbytehq/airbyte/pull/17459) | Upgrade debezium version to 1.9.6 from 1.9.2                                                                                                                               |
| 1.0.12  | 2022-09-27 | [17299](https://github.com/airbytehq/airbyte/pull/17299) | Improve error handling for strict-encrypt postgres source                                                                                                                  |
| 1.0.11  | 2022-09-26 | [17131](https://github.com/airbytehq/airbyte/pull/17131) | Allow nullable columns to be used as cursor                                                                                                                                |
| 1.0.10  | 2022-09-14 | [15668](https://github.com/airbytehq/airbyte/pull/15668) | Wrap logs in AirbyteLogMessage                                                                                                                                             |
| 1.0.9   | 2022-09-13 | [16657](https://github.com/airbytehq/airbyte/pull/16657) | Improve CDC record queueing performance                                                                                                                                    |
| 1.0.8   | 2022-09-08 | [16202](https://github.com/airbytehq/airbyte/pull/16202) | Adds error messaging factory to UI                                                                                                                                         |
| 1.0.7   | 2022-08-30 | [16114](https://github.com/airbytehq/airbyte/pull/16114) | Prevent traffic going on an unsecured channel in strict-encryption version of source postgres                                                                              |
| 1.0.6   | 2022-08-30 | [16138](https://github.com/airbytehq/airbyte/pull/16138) | Remove unnecessary logging                                                                                                                                                 |
| 1.0.5   | 2022-08-25 | [15993](https://github.com/airbytehq/airbyte/pull/15993) | Add support for connection over SSL in CDC mode                                                                                                                            |
| 1.0.4   | 2022-08-23 | [15877](https://github.com/airbytehq/airbyte/pull/15877) | Fix temporal data type bug which was causing failure in CDC mode                                                                                                           |
| 1.0.3   | 2022-08-18 | [14356](https://github.com/airbytehq/airbyte/pull/14356) | DB Sources: only show a table can sync incrementally if at least one column can be used as a cursor field                                                                  |
| 1.0.2   | 2022-08-11 | [15538](https://github.com/airbytehq/airbyte/pull/15538) | Allow additional properties in db stream state                                                                                                                             |
| 1.0.1   | 2022-08-10 | [15496](https://github.com/airbytehq/airbyte/pull/15496) | Fix state emission in incremental sync                                                                                                                                     |
|         | 2022-08-10 | [15481](https://github.com/airbytehq/airbyte/pull/15481) | Fix data handling from WAL logs in CDC mode                                                                                                                                |
| 1.0.0   | 2022-08-05 | [15380](https://github.com/airbytehq/airbyte/pull/15380) | Change connector label to generally_available (requires [upgrading](https://docs.airbyte.com/operator-guides/upgrading-airbyte/) your Airbyte platform to `v0.40.0-alpha`) |
| 0.4.44  | 2022-08-05 | [15342](https://github.com/airbytehq/airbyte/pull/15342) | Adjust titles and descriptions in spec.json                                                                                                                                |
| 0.4.43  | 2022-08-03 | [15226](https://github.com/airbytehq/airbyte/pull/15226) | Make connectionTimeoutMs configurable through JDBC url parameters                                                                                                          |
| 0.4.42  | 2022-08-03 | [15273](https://github.com/airbytehq/airbyte/pull/15273) | Fix a bug in `0.4.36` and correctly parse the CDC initial record waiting time                                                                                              |
| 0.4.41  | 2022-08-03 | [15077](https://github.com/airbytehq/airbyte/pull/15077) | Sync data from beginning if the LSN is no longer valid in CDC                                                                                                              |
|         | 2022-08-03 | [14903](https://github.com/airbytehq/airbyte/pull/14903) | Emit state messages more frequently (⛔ this version has a bug; use `1.0.1` instead                                                                                         |
| 0.4.40  | 2022-08-03 | [15187](https://github.com/airbytehq/airbyte/pull/15187) | Add support for BCE dates/timestamps                                                                                                                                       |
|         | 2022-08-03 | [14534](https://github.com/airbytehq/airbyte/pull/14534) | Align regular and CDC integration tests and data mappers                                                                                                                   |
| 0.4.39  | 2022-08-02 | [14801](https://github.com/airbytehq/airbyte/pull/14801) | Fix multiple log bindings                                                                                                                                                  |
| 0.4.38  | 2022-07-26 | [14362](https://github.com/airbytehq/airbyte/pull/14362) | Integral columns are now discovered as int64 fields.                                                                                                                       |
| 0.4.37  | 2022-07-22 | [14714](https://github.com/airbytehq/airbyte/pull/14714) | Clarified error message when invalid cursor column selected                                                                                                                |
| 0.4.36  | 2022-07-21 | [14451](https://github.com/airbytehq/airbyte/pull/14451) | Make initial CDC waiting time configurable (⛔ this version has a bug and will not work; use `0.4.42` instead)                                                              | |
| 0.4.35  | 2022-07-14 | [14574](https://github.com/airbytehq/airbyte/pull/14574) | Removed additionalProperties:false from JDBC source connectors                                                                                                             |
| 0.4.34  | 2022-07-17 | [13840](https://github.com/airbytehq/airbyte/pull/13840) | Added the ability to connect using different SSL modes and SSL certificates.                                                                                               |
| 0.4.33  | 2022-07-14 | [14586](https://github.com/airbytehq/airbyte/pull/14586) | Validate source JDBC url parameters                                                                                                                                        |
| 0.4.32  | 2022-07-07 | [14694](https://github.com/airbytehq/airbyte/pull/14694) | Force to produce LEGACY state if the use stream capable feature flag is set to false                                                                                       |
| 0.4.31  | 2022-07-07 | [14447](https://github.com/airbytehq/airbyte/pull/14447) | Under CDC mode, retrieve only those tables included in the publications                                                                                                    |
| 0.4.30  | 2022-06-30 | [14251](https://github.com/airbytehq/airbyte/pull/14251) | Use more simple and comprehensive query to get selectable tables                                                                                                           |
| 0.4.29  | 2022-06-29 | [14265](https://github.com/airbytehq/airbyte/pull/14265) | Upgrade postgresql JDBC version to 42.3.5                                                                                                                                  |
| 0.4.28  | 2022-06-23 | [14077](https://github.com/airbytehq/airbyte/pull/14077) | Use the new state management                                                                                                                                               |
| 0.4.26  | 2022-06-17 | [13864](https://github.com/airbytehq/airbyte/pull/13864) | Updated stacktrace format for any trace message errors                                                                                                                     |
| 0.4.25  | 2022-06-15 | [13823](https://github.com/airbytehq/airbyte/pull/13823) | Publish adaptive postgres source that enforces ssl on cloud + Debezium version upgrade to 1.9.2 from 1.4.2                                                                 |
| 0.4.24  | 2022-06-14 | [13549](https://github.com/airbytehq/airbyte/pull/13549) | Fixed truncated precision if the value of microseconds or seconds is 0                                                                                                     |
| 0.4.23  | 2022-06-13 | [13655](https://github.com/airbytehq/airbyte/pull/13745) | Fixed handling datetime cursors when upgrading from older versions of the connector                                                                                        |
| 0.4.22  | 2022-06-09 | [13655](https://github.com/airbytehq/airbyte/pull/13655) | Fixed bug with unsupported date-time datatypes during incremental sync                                                                                                     |
| 0.4.21  | 2022-06-06 | [13435](https://github.com/airbytehq/airbyte/pull/13435) | Adjust JDBC fetch size based on max memory and max row size                                                                                                                |
| 0.4.20  | 2022-06-02 | [13367](https://github.com/airbytehq/airbyte/pull/13367) | Added convertion hstore to json format                                                                                                                                     |
| 0.4.19  | 2022-05-25 | [13166](https://github.com/airbytehq/airbyte/pull/13166) | Added timezone awareness and handle BC dates                                                                                                                               |
| 0.4.18  | 2022-05-25 | [13083](https://github.com/airbytehq/airbyte/pull/13083) | Add support for tsquey type                                                                                                                                                |
| 0.4.17  | 2022-05-19 | [13016](https://github.com/airbytehq/airbyte/pull/13016) | CDC modify schema to allow null values                                                                                                                                     |
| 0.4.16  | 2022-05-14 | [12840](https://github.com/airbytehq/airbyte/pull/12840) | Added custom JDBC parameters field                                                                                                                                         |
| 0.4.15  | 2022-05-13 | [12834](https://github.com/airbytehq/airbyte/pull/12834) | Fix the bug that the connector returns empty catalog for Azure Postgres database                                                                                           |
| 0.4.14  | 2022-05-08 | [12689](https://github.com/airbytehq/airbyte/pull/12689) | Add table retrieval according to role-based `SELECT` privilege                                                                                                             |
| 0.4.13  | 2022-05-05 | [10230](https://github.com/airbytehq/airbyte/pull/10230) | Explicitly set null value for field in json                                                                                                                                |
| 0.4.12  | 2022-04-29 | [12480](https://github.com/airbytehq/airbyte/pull/12480) | Query tables with adaptive fetch size to optimize JDBC memory consumption                                                                                                  |
| 0.4.11  | 2022-04-11 | [11729](https://github.com/airbytehq/airbyte/pull/11729) | Bump mina-sshd from 2.7.0 to 2.8.0                                                                                                                                         |
| 0.4.10  | 2022-04-08 | [11798](https://github.com/airbytehq/airbyte/pull/11798) | Fixed roles for fetching materialized view processing                                                                                                                      |
| 0.4.8   | 2022-02-21 | [10242](https://github.com/airbytehq/airbyte/pull/10242) | Fixed cursor for old connectors that use non-microsecond format. Now connectors work with both formats                                                                     |
| 0.4.7   | 2022-02-18 | [10242](https://github.com/airbytehq/airbyte/pull/10242) | Updated timestamp transformation with microseconds                                                                                                                         |
| 0.4.6   | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256) | (unpublished) Add `-XX:+ExitOnOutOfMemoryError` JVM option                                                                                                                 |
| 0.4.5   | 2022-02-08 | [10173](https://github.com/airbytehq/airbyte/pull/10173) | Improved  discovering tables in case if user does not have permissions to any table                                                                                        |
| 0.4.4   | 2022-01-26 | [9807](https://github.com/airbytehq/airbyte/pull/9807)   | Update connector fields title/description                                                                                                                                  |
| 0.4.3   | 2022-01-24 | [9554](https://github.com/airbytehq/airbyte/pull/9554)   | Allow handling of java sql date in CDC                                                                                                                                     |
| 0.4.2   | 2022-01-13 | [9360](https://github.com/airbytehq/airbyte/pull/9360)   | Added schema selection                                                                                                                                                     |
| 0.4.1   | 2022-01-05 | [9116](https://github.com/airbytehq/airbyte/pull/9116)   | Added materialized views processing                                                                                                                                        |
| 0.4.0   | 2021-12-13 | [8726](https://github.com/airbytehq/airbyte/pull/8726)   | Support all Postgres types                                                                                                                                                 |
| 0.3.17  | 2021-12-01 | [8371](https://github.com/airbytehq/airbyte/pull/8371)   | Fixed incorrect handling "\n" in ssh key                                                                                                                                   |
| 0.3.16  | 2021-11-28 | [7995](https://github.com/airbytehq/airbyte/pull/7995)   | Fixed money type with amount > 1000                                                                                                                                        |
| 0.3.15  | 2021-11-26 | [8066](https://github.com/airbytehq/airbyte/pull/8266)   | Fixed the case, when Views are not listed during schema discovery                                                                                                          |
| 0.3.14  | 2021-11-17 | [8010](https://github.com/airbytehq/airbyte/pull/8010)   | Added checking of privileges before table internal discovery                                                                                                               |
| 0.3.13  | 2021-10-26 | [7339](https://github.com/airbytehq/airbyte/pull/7339)   | Support or improve support for Interval, Money, Date, various geometric data types, inventory_items, and others                                                            |
| 0.3.12  | 2021-09-30 | [6585](https://github.com/airbytehq/airbyte/pull/6585)   | Improved SSH Tunnel key generation steps                                                                                                                                   |
| 0.3.11  | 2021-09-02 | [5742](https://github.com/airbytehq/airbyte/pull/5742)   | Add SSH Tunnel support                                                                                                                                                     |
| 0.3.9   | 2021-08-17 | [5304](https://github.com/airbytehq/airbyte/pull/5304)   | Fix CDC OOM issue                                                                                                                                                          |
| 0.3.8   | 2021-08-13 | [4699](https://github.com/airbytehq/airbyte/pull/4699)   | Added json config validator                                                                                                                                                |
| 0.3.4   | 2021-06-09 | [3973](https://github.com/airbytehq/airbyte/pull/3973)   | Add `AIRBYTE_ENTRYPOINT` for Kubernetes support                                                                                                                            |
| 0.3.3   | 2021-06-08 | [3960](https://github.com/airbytehq/airbyte/pull/3960)   | Add method field in specification parameters                                                                                                                               |
| 0.3.2   | 2021-05-26 | [3179](https://github.com/airbytehq/airbyte/pull/3179)   | Remove `isCDC` logging                                                                                                                                                     |
| 0.3.1   | 2021-04-21 | [2878](https://github.com/airbytehq/airbyte/pull/2878)   | Set defined cursor for CDC                                                                                                                                                 |
| 0.3.0   | 2021-04-21 | [2990](https://github.com/airbytehq/airbyte/pull/2990)   | Support namespaces                                                                                                                                                         |
| 0.2.7   | 2021-04-16 | [2923](https://github.com/airbytehq/airbyte/pull/2923)   | SSL spec as optional                                                                                                                                                       |
| 0.2.6   | 2021-04-16 | [2757](https://github.com/airbytehq/airbyte/pull/2757)   | Support SSL connection                                                                                                                                                     |
| 0.2.5   | 2021-04-12 | [2859](https://github.com/airbytehq/airbyte/pull/2859)   | CDC bugfix                                                                                                                                                                 |
| 0.2.4   | 2021-04-09 | [2548](https://github.com/airbytehq/airbyte/pull/2548)   | Support CDC                                                                                                                                                                |
| 0.2.3   | 2021-03-28 | [2600](https://github.com/airbytehq/airbyte/pull/2600)   | Add NCHAR and NVCHAR support to DB and cursor type casting                                                                                                                 |
| 0.2.2   | 2021-03-26 | [2460](https://github.com/airbytehq/airbyte/pull/2460)   | Destination supports destination sync mode                                                                                                                                 |
| 0.2.1   | 2021-03-18 | [2488](https://github.com/airbytehq/airbyte/pull/2488)   | Sources support primary keys                                                                                                                                               |
| 0.2.0   | 2021-03-09 | [2238](https://github.com/airbytehq/airbyte/pull/2238)   | Protocol allows future/unknown properties                                                                                                                                  |
| 0.1.13  | 2021-02-02 | [1887](https://github.com/airbytehq/airbyte/pull/1887)   | Migrate AbstractJdbcSource to use iterators                                                                                                                                |
| 0.1.12  | 2021-01-25 | [1746](https://github.com/airbytehq/airbyte/pull/1746)   | Fix NPE in State Decorator                                                                                                                                                 |
| 0.1.11  | 2021-01-25 | [1765](https://github.com/airbytehq/airbyte/pull/1765)   | Add field titles to specification                                                                                                                                          |
| 0.1.10  | 2021-01-19 | [1724](https://github.com/airbytehq/airbyte/pull/1724)   | Fix JdbcSource handling of tables with same names in different schemas                                                                                                     |
| 0.1.9   | 2021-01-14 | [1655](https://github.com/airbytehq/airbyte/pull/1655)   | Fix JdbcSource OOM                                                                                                                                                         |
| 0.1.8   | 2021-01-13 | [1588](https://github.com/airbytehq/airbyte/pull/1588)   | Handle invalid numeric values in JDBC source                                                                                                                               |
| 0.1.7   | 2021-01-08 | [1307](https://github.com/airbytehq/airbyte/pull/1307)   | Migrate Postgres and MySql to use new JdbcSource                                                                                                                           |
| 0.1.6   | 2020-12-09 | [1172](https://github.com/airbytehq/airbyte/pull/1172)   | Support incremental sync                                                                                                                                                   |
| 0.1.5   | 2020-11-30 | [1038](https://github.com/airbytehq/airbyte/pull/1038)   | Change JDBC sources to discover more than standard schemas                                                                                                                 |
| 0.1.4   | 2020-11-30 | [1046](https://github.com/airbytehq/airbyte/pull/1046)   | Add connectors using an index YAML file                                                                                                                                    |
