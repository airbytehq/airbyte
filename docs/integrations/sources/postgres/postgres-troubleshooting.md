import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Troubleshooting Postgres Sources

## Connector Limitations

### General Limitations

- The Postgres source connector does not alter the schema present in your database. Depending on the destination connected to this source, however, the schema may be altered. See the destination's documentation for more details.
- The following two schema evolution actions are currently supported:
  - Adding/removing tables without resetting the entire connection at the destination
    Caveat: In the CDC mode, adding a new table to a connection may become a temporary bottleneck. When a new table is added, the next sync job takes a full snapshot of the new table before it proceeds to handle any changes.
  - Resetting a single table within the connection without resetting the rest of the destination tables in that connection
- Changing a column data type or removing a column might break connections.

### Xmin Limitations

There are some notable shortcomings associated with the Xmin replication method:

- Unsupported DDL operations : This replication method cannot support row deletions.
- Performance : Requires a full table scan, so can lead to poor performance.
- Row-level granularity : The xmin column is stored at the row level. This means that a row will still be synced if it had been modified, regardless of whether the modification corresponded to the subset of columns the user is interested in.
- Transaction ID (XID) wraparound : the transaction ID (aka xid) is represented by a 32-bit integer and has an upper limit value of 4,294,967,295. Once this value is reached, the xid wraps around and stops increasing monotonically. At this point, the xmin column cannot be reliably used as a cursor, which can lead to resyncing data that had already been synced. Also see the trouble-shooting section on Xmin wraparound below.

### Version Requirements

- For Airbyte Open Source users, [upgrade](https://docs.airbyte.com/operator-guides/upgrading-airbyte/) your Airbyte platform to version `v0.58.0` or newer
- Use Postgres v9.3.x or above for non-CDC workflows and Postgres v10 or above for CDC workflows
- For Airbyte Cloud (and optionally for Airbyte Open Source), ensure SSL is enabled in your environment

### CDC Requirements

- Incremental sync is only supported for tables with primary keys. For tables without primary keys, use [Full Refresh sync](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite).
- Data must be in tables and not views. If you require data synchronization from a view, you would need to create a new connection with `Standard` as `Replication Method`.
- The modifications you want to capture must be made using `DELETE`/`INSERT`/`UPDATE`. For example, changes made using `TRUNCATE`/`ALTER` will not appear in logs and therefore in your destination.
- Schema changes are not supported automatically for CDC sources. Reset and resync data if you make a schema change.
- The records produced by `DELETE` statements only contain primary keys. All other data fields are unset.
- Log-based replication only works for master instances of Postgres. CDC cannot be run from a read-replica of your primary database.
- An Airbyte database source using CDC replication can only be used with a single Airbyte destination. This is due to how Postgres CDC is implemented - each destination would receive only part of the data available in the replication slot.
- Using logical replication increases disk space used on the database server. The additional data is stored until it is consumed.
  - Set frequent syncs for CDC to ensure that the data doesn't fill up your disk space.
  - If you stop syncing a CDC-configured Postgres instance with Airbyte, delete the replication slot. Otherwise, it may fill up your disk space.

### Supported cursors

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

### Vendor-Specific Connector Limitations

:::warning

Not all implementations or deployments of a database will be the same. This section lists specific limitations and known issues with the connector based on _how_ or
_where_ it is deployed.

:::

#### AWS Aurora

AWS Aurora implements a [CDC caching layer](https://aws.amazon.com/blogs/database/achieve-up-to-17x-lower-replication-lag-with-the-new-write-through-cache-for-aurora-postgresql/) that is incompatible with Airbyte's CDC implementation. To use Airbyte with AWS Aurora, disable the CDC caching layer. Disable CDC caching by setting the [`rds.logical_wal_cache`](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/AuroraPostgreSQL.Replication.Logical.html) parameter to `0` in the AWS Aurora parameter group.

In addition, if you are seeing timeout errors, set [`apg_write_forward.idle_session_timeout`](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database-write-forwarding-apg.html#aurora-global-database-write-forwarding-params-apg) to 1200000 (20 minutes) in the AWS Aurora parameter group.

#### TimescaleDB

While postgres compatible, TimescaleDB does not support CDC replication.

In some cases with a highly-compressed database, you may receive an error like `transparent decompression only supports tableoid system column`. This error indicates that the cursor column chosen for the sync is compressed and cannot be used. To resolve this issue, you can change the cursor column to a non-compressed column.

#### Azure PG Flex

When using CDC with Azure PG Flex, if a failover to a new leader happens, your CDC replication slot will not be re-created automatically. You will need to manually re-create the replication slot on the new leader, and initiate a reset of the connection in Airbyte.

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

- Recommended: Set [`hot_standby_feedback`](https://www.postgresql.org/docs/14/runtime-config-replication.html#GUC-HOT-STANDBY-FEEDBACK) to `true` on the replica server. This parameter will prevent the primary server from deleting the write-ahead logs when the replica is busy serving user queries. However, the downside is that the write-ahead log will increase in size.
- Recommended: Sync data when there is no update running in the primary server, or sync data from the primary server.
- Not Recommended: Increase [`max_standby_archive_delay`](https://www.postgresql.org/docs/14/runtime-config-replication.html#GUC-MAX-STANDBY-ARCHIVE-DELAY) and [`max_standby_streaming_delay`](https://www.postgresql.org/docs/14/runtime-config-replication.html#GUC-MAX-STANDBY-STREAMING-DELAY) to be larger than the amount of time needed to complete the data sync. However, it is usually hard to tell how much time it will take to sync all the data. This approach is not very practical.

### Under CDC incremental mode, there are still full refresh syncs

Normally under the CDC mode, the Postgres source will first run a full refresh sync to read the snapshot of all the existing data, and all subsequent runs will only be incremental syncs reading from the write-ahead logs (WAL). However, occasionally, you may see full refresh syncs after the initial run. When this happens, you will see the following log:

> Saved offset is before Replication slot's confirmed_flush_lsn, Airbyte will trigger sync from scratch

The root causes is that the WALs needed for the incremental sync has been removed by Postgres. This can occur under the following scenarios:

- When there are lots of database updates resulting in more WAL files than allowed in the `pg_wal` directory, Postgres will purge or archive the WAL files. This scenario is preventable. Possible solutions include:
  - Sync the data source more frequently.
  - Set a higher `wal_keep_size`. If no unit is provided, it is in megabytes, and the default is `0`. See detailed documentation [here](https://www.postgresql.org/docs/current/runtime-config-replication.html#GUC-WAL-KEEP-SIZE). The downside of this approach is that more disk space will be needed.
- When the Postgres connector successfully reads the WAL and acknowledges it to Postgres, but the destination connector fails to consume the data, the Postgres connector will try to read the same WAL again, which may have been removed by Postgres, since the WAL record is already acknowledged. This scenario is rare, because it can happen, and currently there is no way to prevent it. The correct behavior is to perform a full refresh.

### Temporary File Size Limit

Some larger tables may encounter an error related to the temporary file size limit such as `temporary file size exceeds temp_file_limit`. To correct this error increase the [temp_file_limit](https://postgresqlco.nf/doc/en/param/temp_file_limit/).

### Xmin Wraparound

When a database experiences Xmin wraparound, the replication performance will be degraded. Furthermore, data that has already been synced may be resynced again. When setting up a Postgres source connector or at the beginning of the sync, the connector will check if an Xmin wraparound exists. If so, the connector returns a config error, reminding the user to switch to the CDC replication method.

### (Advanced) Custom JDBC Connection Strings

To customize the JDBC connection beyond common options, specify additional supported [JDBC URL parameters](https://jdbc.postgresql.org/documentation/head/connect.html) as key-value pairs separated by the symbol & in the **JDBC URL Parameters (Advanced)** field.

Example: key1=value1&key2=value2&key3=value3

These parameters will be added at the end of the JDBC URL that the AirByte will use to connect to your Postgres database.

The connector now supports `connectTimeout` and defaults to 60 seconds. Setting connectTimeout to 0 seconds will set the timeout to the longest time available.

**Note:** Do not use the following keys in JDBC URL Params field as they will be overwritten by Airbyte:
`currentSchema`, `user`, `password`, `ssl`, and `sslmode`.

### (Advanced) Setting up initial CDC waiting time

The Postgres connector may need some time to start processing the data in the CDC mode in the following scenarios:

- When the connection is set up for the first time and a snapshot is needed
- When the connector has a lot of change logs to process

The connector waits for the default initial wait time of 5 minutes (300 seconds). Setting the parameter to a longer duration will result in slower syncs, while setting it to a shorter duration may cause the connector to not have enough time to create the initial snapshot or read through the change logs. The valid range is 120 seconds to 1200 seconds.

If you know there are database changes to be synced, but the connector cannot read those changes, the root cause may be insufficient waiting time. In that case, you can increase the waiting time (example: set to 600 seconds) to test if it is indeed the root cause. On the other hand, if you know there are no database changes, you can decrease the wait time to speed up the zero record syncs.

### (Advanced) Resolving sync failures due to WAL disk consumption {#advanced-wal-disk-consumption-and-heartbeat-action-query}

When using the `Read Changes using Write-Ahead Log (CDC)` update method, you might encounter a situation where your initial sync is successful, but further syncs fail. You may also notice that the `confirmed_flush_lsn` column of the server's `pg_replication_slots` view doesn't advance as expected.

This is a general issue that affects databases, schemas, and tables with small transaction volumes. There are complexities in the way PostgreSQL disk space can be consumed by WAL files, and these can cause issues for the connector when dealing with low transaction volumes. Airbyte's connector depends on Debezium. These complexities are outlined in [their documentation](https://debezium.io/documentation/reference/stable/connectors/postgresql.html#postgresql-wal-disk-space), if you want to learn more.

#### Simple fix (read-only)

The easiest way to fix this issue is to add one or more tables with high transaction volumes to the Airbyte publication. You do not need to actually sync these tables, but adding them to the publication will advance the log sequence number (LSN), ensuring the sync can succeed without you giving Airbyte write access to the database. However, this may greatly increase disk consumption.

```sql
ALTER PUBLICATION <publicationName> ADD TABLE <high_volume_table>;
```

If you do not want to increase disk consumption, use the following solutions, which require write access.

#### Fix when reading against a primary or standalone (write)

To fix the issue when reading against primary or standalone, artificially add events to a heartbeat table the Airbyte user can write to.

1. Create an `airbyte_heartbeat` table in the database and schema being tracked.

	```sql
	CREATE TABLE airbyte_heartbeat (
		id SERIAL PRIMARY KEY,
		timestamp TIMESTAMP NOT NULL DEFAULT current_timestamp,
		text TEXT
	);
	```

2. Add this table to the airbyte publication.

	```sql
	ALTER PUBLICATION <publicationName> ADD TABLE airbyte_heartbeat;
	```

3. In the Postgres source connector in Airbyte, configure the `Debezium heartbeat query` property. For example:

	```sql
	INSERT INTO airbyte_heartbeat (text) VALUES ('heartbeat')
	```

Airbyte periodically executes this query on the `airbyte_heartbeat` table.

#### Fix when reading against a read replica (write)

To fix the issue when reading against a read replica:

1. [Add pg_cron as an extension](#wal-pg-cron).
2. [Periodically add events](#wal-heartbeat-table) to a heartbeat table your Airbyte user can write to.

##### Add the pg_cron extension {#wal-pg-cron}

[pg_cron](https://github.com/citusdata/pg_cron) is a cron-based job scheduler for PostgreSQL that runs inside the database as an extension so you can schedule PostgreSQL commands directly from the database.

<Tabs>
  <TabItem value="Google Cloud" label="Google Cloud" default>
    
1. Ensure your PostgreSQL instance is version 10 or higher. Version 10 is the minimum version that supports pg_cron.

    ```sql
    SELECT version();
    ```

2. Configure your database flags to enable pg_cron. For help with this, see [Google Cloud's docs](https://cloud.google.com/sql/docs/postgres/flags).

	1. Set the `cloudsql.enable_pg_cron` flag to `on`. For more information, see [Google Cloud's docs](https://cloud.google.com/sql/docs/postgres/extensions#pg_cron).

	2. Set the `shared_preload_libraries` flag to include `pg_cron`.

		```
		shared_preload_libraries = 'pg_cron'
		```

		If you already have other libraries in this parameter, add `pg_cron` to the list, separating each library with a comma.

		```
		shared_preload_libraries = 'pg_cron,pg_stat_statements'
		```

	3. Restart your PostgreSQL instance. For help with this, see [Google Cloud's docs](https://cloud.google.com/sql/docs/postgres/start-stop-restart-instance#restart).

PostgreSQL now preloads the `pg_cron` extension when the instance starts.

  </TabItem>
  <TabItem value="Amazon RDS" label="Amazon RDS">

1. Ensure your RDS for PostgreSQL instance is version 12.5 or later. pg_cron requires version 12.5 and later.

    ```sql
    SELECT version();
    ```

2. Modify the parameter group associated with your PostgreSQL database instance to enable pg_cron. For help modifying parameter groups, see the [AWS docs](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithParamGroups.Modifying.html).

	1. If your RDS for PostgreSQL database instance uses the `rds.allowed_extensions` parameter to spcify which extensions can be installed, add `pg_cron` to that list.
	
	2. Edit the custom parameter group associated with your PostgreSQL DB instance. Modify the `shared_preload_libraries` parameter to include the value `pg_cron`.

	3. Reboot your PostgreSQL database instance. For help, see the [AWS docs](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_RebootInstance.html#USER_RebootInstance.steps).

PostgreSQL now preloads the `pg_cron` extension when the instance starts.

  </TabItem>
</Tabs>

##### Enable the pg_cron extension, create a heartbeat table, and schedule a cron job {#wal-heartbeat-table}

1. Verify pg_cron was successfully added to `shared_preload_libraries`.

	```
	show shared_preload_libraries
	```

2. Enable the pg_cron extension, create a `periodic_log` (heartbeat) table, and schedule a cron job.

	```sql
	CREATE EXTENSION IF NOT EXISTS pg_cron;

	CREATE TABLE periodic_log (
		log_id SERIAL PRIMARY KEY,
		log_time TIMESTAMP DEFAULT current_timestamp
	);

	SELECT cron.schedule(
		'periodic_logger',               -- job name
		'*/1 * * * *',                   -- cron expression (every minute)
		$$INSERT INTO periodic_log DEFAULT VALUES$$ -- the SQL statement to run
	);
	```

3. Verify the scheduled job.

	```sql
	SELECT * FROM cron.job;
	```

4. Verify the periodic update.

	```sql
	SELECT * FROM periodic_log ORDER BY log_time DESC;
	```

5. Alter the publication to include this table on the primary.

	```sql
	ALTER PUBLICATION airbyte_publication ADD TABLE periodic_log;
	```

6. Sync normally from the primary to the replica.

##### Stop the sync

If you need to stop syncing later, unschedule the cron job.

```sql
SELECT cron.unschedule('periodic_logger');
```
