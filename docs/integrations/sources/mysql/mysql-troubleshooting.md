# Troubleshooting MySQL Sources

### General Limitations

- Use MySQL Server versions `8.0`, `5.7`, or `5.6`.
- For Airbyte Open Source users, [upgrade](https://docs.airbyte.com/operator-guides/upgrading-airbyte/) your Airbyte platform to version `v0.58.0` or newer
- For Airbyte Cloud (and optionally for Airbyte Open Source), ensure SSL is enabled in your environment

### CDC Requirements

- Make sure to read our [CDC docs](../../../understanding-airbyte/cdc.md) to see limitations that impact all databases using CDC replication.
- Our CDC implementation uses at least once delivery for all change records.

### Vendor-Specific Connector Limitations

:::warning

Not all implementations or deployments of a database will be the same. This section lists specific limitations and known issues with the connector based on _how_ or
_where_ it is deployed.

:::

#### Digital Ocean MySQL

Digital Ocean's managed MySQL servers, by default, will clear the binary logs periodically, outside of the replication settings within the MySQL server.. Contact Digital Ocean support to disable this feature if you wish to use CDC replication with Airbyte.

#### PlanetScale

Planetscale has a maximum number of records per query set to 100K by default. Airbyte typically queries in batches of 500K for faster replication.

#### MariaDB

MariaDB is a fork of MySQL that adds many new features. The MySQL source connector is compatible with MariaDB, but there may be some limitations, specifically around CDC replication. If you encounter errors with CDC replication, please switch to other replication methods, which may be more compatible with MariaDB.

## Troubleshooting

### Common Config Errors

- Mapping MySQL's DateTime field: There may be problems with mapping values in MySQL's datetime field to other relational data stores. MySQL permits zero values for date/time instead of NULL which may not be accepted by other data stores. To work around this problem, you can pass the following key value pair in the JDBC connector of the source setting `zerodatetimebehavior=Converttonull`.
- Amazon RDS MySQL or MariaDB connection issues: If you see the following `Cannot create a PoolableConnectionFactory` error, please add `enabledTLSProtocols=TLSv1.2` in the JDBC parameters.
- Amazon RDS MySQL connection issues: If you see `Error: HikariPool-1 - Connection is not available, request timed out after 30001ms.`, many times this due to your VPC not allowing public traffic. We recommend going through [this AWS troubleshooting checklist](https://aws.amazon.com/premiumsupport/knowledge-center/rds-cannot-connect/) to ensure the correct permissions/settings have been granted to allow Airbyte to connect to your database.

### Under CDC incremental mode, there are still full refresh syncs

Normally under the CDC mode, the MySQL source will first run a full refresh sync to read the snapshot of all the existing data, and all subsequent runs will only be incremental syncs reading from the binlogs. However, occasionally, you may see full refresh syncs after the initial run. When this happens, you will see the following log:

> Saved offset no longer present on the server, Airbyte is going to trigger a sync from scratch

The root causes is that the binglogs needed for the incremental sync have been removed by MySQL. This can occur under the following scenarios:

- When there are lots of database updates resulting in more WAL files than allowed in the `pg_wal` directory, Postgres will purge or archive the WAL files. This scenario is preventable. Possible solutions include:
  - Sync the data source more frequently.
  - Set a higher `binlog_expire_logs_seconds`. It's recommended to set this value to a time period of 7 days. See detailed documentation [here](https://dev.mysql.com/doc/refman/8.0/en/replication-options-binary-log.html#sysvar_binlog_expire_logs_seconds). The downside of this approach is that more disk space will be needed.

### EventDataDeserializationException errors during initial snapshot

When a sync runs for the first time using CDC, Airbyte performs an initial consistent snapshot of your database. Airbyte doesn't acquire any table locks \(for tables defined with MyISAM engine, the tables would still be locked\) while creating the snapshot to allow writes by other database clients. But in order for the sync to work without any error/unexpected behaviour, it is assumed that no schema changes are happening while the snapshot is running.

If seeing `EventDataDeserializationException` errors intermittently with root cause `EOFException` or `SocketException`, you may need to extend the following _MySql server_ timeout values by running:

```
set global slave_net_timeout = 120;
set global thread_pool_idle_timeout = 120;
```

### (Advanced) Enable GTIDs

Global transaction identifiers \(GTIDs\) uniquely identify transactions that occur on a server within a cluster. Though not required for a Airbyte MySQL connector, using GTIDs simplifies replication and enables you to more easily confirm if primary and replica servers are consistent. For more information refer [mysql doc](https://dev.mysql.com/doc/refman/8.0/en/replication-options-gtids.html#option_mysqld_gtid-mode)

- Enable gtid_mode : Boolean that specifies whether GTID mode of the MySQL server is enabled or not. Enable it via `mysql> gtid_mode=ON`
- Enable enforce_gtid_consistency : Boolean that specifies whether the server enforces GTID consistency by allowing the execution of statements that can be logged in a transactionally safe manner. Required when using GTIDs. Enable it via `mysql> enforce_gtid_consistency=ON`

### (Advanced) Setting up initial CDC waiting time

The MySQl connector may need some time to start processing the data in the CDC mode in the following scenarios:

- When the connection is set up for the first time and a snapshot is needed
- When the connector has a lot of change logs to process

The connector waits for the default initial wait time of 5 minutes (300 seconds). Setting the parameter to a longer duration will result in slower syncs, while setting it to a shorter duration may cause the connector to not have enough time to create the initial snapshot or read through the change logs. The valid range is 300 seconds to 1200 seconds.

If you know there are database changes to be synced, but the connector cannot read those changes, the root cause may be insufficient waiting time. In that case, you can increase the waiting time (example: set to 600 seconds) to test if it is indeed the root cause. On the other hand, if you know there are no database changes, you can decrease the wait time to speed up the zero record syncs.

### (Advanced) Set up server timezone

In CDC mode, the MySQl connector may need a timezone configured if the existing MySQL database been set up with a system timezone that is not recognized by the [IANA Timezone Database](https://www.iana.org/time-zones).

In this case, you can configure the server timezone to the equivalent IANA timezone compliant timezone. (e.g. CEST -> Europe/Berlin).

## Upgrading from 0.6.8 and older versions to 0.6.9 and later versions

There is a backwards incompatible spec change between MySQL Source connector versions 0.6.8 and 0.6.9. As part of that spec change
`replication_method` configuration parameter was changed to `object` from `string`.

In MySQL source connector versions 0.6.8 and older, `replication_method` configuration parameter was saved in the configuration database as follows:

```
"replication_method": "STANDARD"
```

Starting with version 0.6.9, `replication_method` configuration parameter is saved as follows:

```
"replication_method": {
    "method": "STANDARD"
}
```

After upgrading MySQL Source connector from 0.6.8 or older version to 0.6.9 or newer version you need to fix source configurations in the `actor` table
in Airbyte database. To do so, you need to run the following two SQL queries. Follow the instructions in [Airbyte documentation](https://docs.airbyte.com/operator-guides/configuring-airbyte-db/#accessing-the-default-database-located-in-docker-airbyte-db) to
run SQL queries on Airbyte database.

If you have connections with MySQL Source using _Standard_ replication method, run this SQL:

```sql
update public.actor set configuration =jsonb_set(configuration, '{replication_method}', '{"method": "STANDARD"}', true)
WHERE actor_definition_id ='435bb9a5-7887-4809-aa58-28c27df0d7ad' AND (configuration->>'replication_method' = 'STANDARD');
```

If you have connections with MySQL Source using _Logical Replication (CDC)_ method, run this SQL:

```sql
update public.actor set configuration =jsonb_set(configuration, '{replication_method}', '{"method": "CDC"}', true)
WHERE actor_definition_id ='435bb9a5-7887-4809-aa58-28c27df0d7ad' AND (configuration->>'replication_method' = 'CDC');
```
