# Postgres

## Features

| Feature | Supported | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | Yes |  |
| Replicating Views | Yes |  |
| Replicate Incremental Deletes | Yes |  |
| Logical Replication \(WAL\) | Yes |  |
| SSL Support | Yes |  |
| SSH Tunnel Connection | Yes |  |
| Namespaces | Yes | Enabled by default. |
| Custom Types | Yes |  |
| Arrays | Yes | Byte-arrays are not supported yet. |
| Generating an RSA Private Key | No | Coming Soon. |
| Schema Selection | Yes | The 'public' schema is set by default. Multiple schemas may be used at one time. No schemas set explicitly - will sync all of existing. |

The Postgres source does not alter the schema present in your database. Depending on the destination connected to this source, however, the schema may be altered. See the destination's documentation for more details.

## Getting Started \(Airbyte Cloud\)

On Airbyte Cloud, only TLS connections to your Postgres instance are supported. Other than that, you can proceed with the open-source instructions below.

## Getting Started \(Airbyte Open-Source\)

### Requirements

1. Postgres `v9.3.x` or above
2. Allow connections from Airbyte to your Postgres database \(if they exist in separate VPCs\)
3. Create a dedicated read-only Airbyte user with access to all tables needed for replication

### 1. Make sure your database is accessible from the machine running Airbyte

This is dependent on your networking setup. The easiest way to verify if Airbyte is able to connect to your Postgres instance is via the check connection tool in the UI.

### 2. Create a dedicated read-only user with access to the relevant tables \(Recommended but optional\)

This step is optional but highly recommended for better permission control and auditing. Alternatively, you can use Airbyte with an existing user in your database.

To create a dedicated database user, run the following commands against your database:

```sql
CREATE USER <username> PASSWORD 'your_password_here';
```

Then give it access to the relevant schema:

```sql
GRANT USAGE ON SCHEMA <schema_name> TO <username>
```

Note that to replicate data from multiple Postgres schemas, you can re-run the command above to grant access to all the relevant schemas, but you'll need to set up multiple sources connecting to the same db on multiple schemas.

Next, grant the user read-only access to the relevant tables. The simplest way is to grant read access to all tables in the schema as follows:

```sql
GRANT SELECT ON ALL TABLES IN SCHEMA <schema_name> TO airbyte;

-- Allow user to see tables created in the future
ALTER DEFAULT PRIVILEGES IN SCHEMA <schema_name> GRANT SELECT ON TABLES TO <username>;
```
#### Syncing a subset of columns
Currently, there is no way to sync a subset of columns using the Postgres source connector.
- When setting up a connection, you can only choose which tables to sync, but not columns.
- If the user can only access a subset of columns, the connection check will pass. However, the data sync will fail with a `permission denied` exception.

The short-term workaround for partial table syncing is to create a view on the specific columns, and grant the user read access to that view:

```sql
CREATE VIEW <view_name> as SELECT <columns> FROM <table>;
GRANT SELECT ON TABLE <view_name> IN SCHEMA <schema_name> to <user_name>;
```

This issue is tracked in [\#9771](https://github.com/airbytehq/airbyte/issues/9771).
### <a name="jdbc-url-params"></a>3. (Advanced) Configure Additional JDBC URL Parameters

This is an advanced configuration option. Users are advised to use it with caution. If you need to customize the JDBC connection beyond common options you can specify additional JDBC URL parameters in `JDBC URL Params` field. The value of `JDBC URL Params` field
should have the form of key-value pairs separated by the symbol `&`. 

E.g. `key1=value1&key2=value2&key3=value3`

These parameters will be added at the end of the JDBC URL that the AirByte will use to connect to your Postgres database.

Do not use any of the following keys in `JDBC URL Params` field, because they will be overwritten by Airbyte:
 * currentSchema
 * user
 * password
 * ssl
 * sslmode

You can read about JDBC URL parameters supported by [Postgres in Postgres JDBC Driver Documentation](https://jdbc.postgresql.org/documentation/head/connect.html).

### 4. Optionally, set up CDC. Follow the guide [below](#setting-up-cdc-for-postgres) to do so.

### 5. That's it!

Your database user should now be ready for use with Airbyte.

## Change Data Capture \(CDC\) / Logical Replication / WAL Replication

We use [logical replication](https://www.postgresql.org/docs/10/logical-replication.html) of the Postgres write-ahead log \(WAL\) to incrementally capture deletes using a replication plugin.

We use `pgoutput` as a default plugin, which is included in Postgres 10+. Also `wal2json` plugin is supported, please read [the section on replication plugins below](postgres.md#select-replication-plugin) for more information.

Please read the [CDC docs](../../understanding-airbyte/cdc.md) for an overview of how Airbyte approaches CDC.

### Should I use CDC for Postgres?

* If you need a record of deletions and can accept the limitations posted below, you should to use CDC for Postgres.
* If your data set is small and you just want snapshot of your table in the destination, consider using Full Refresh replication for your table instead of CDC.
* If the limitations prevent you from using CDC and your goal is to maintain a snapshot of your table in the destination, consider using non-CDC incremental and occasionally reset the data and re-sync.
* If your table has a primary key but doesn't have a reasonable cursor field for incremental syncing \(i.e. `updated_at`\), CDC allows you to sync your table incrementally.

#### CDC Limitations

* Make sure to read our [CDC docs](../../understanding-airbyte/cdc.md) to see limitations that impact all databases using CDC replication.
* CDC is only available for Postgres 10+.
* Airbyte requires a replication slot configured only for its use. Only one source should be configured that uses this replication slot. Instructions on how to set up a replication slot can be found below.
* Log-based replication only works for master instances of Postgres.
* Using logical replication increases disk space used on the database server. The additional data is stored until it is consumed.
  * We recommend setting frequent syncs for CDC in order to ensure that this data doesn't fill up your disk space.
  * If you stop syncing a CDC-configured Postgres instance to Airbyte, you should delete the replication slot. Otherwise, it may fill up your disk space.
* Our CDC implementation uses at least once delivery for all change records.

### Setting up CDC for Postgres

#### 1. Enable logical replication

Follow one of these guides to enable logical replication:

* [Bare Metal, VMs \(EC2/GCE/etc\), Docker, etc.](#cdc-on-bare-metal-vms-ec2-gce-etc-docker-etc)
* [AWS Postgres RDS or Aurora](#cdc-on-aws-postgres-rds-or-aurora)
* [Azure Database for Postgres](#cdc-on-azure-database-for-postgres)

#### 2. Add user-level permissions

We recommend using a user specifically for Airbyte's replication so you can minimize access. This Airbyte user for your instance needs to be granted `REPLICATION` and `LOGIN` permissions. You can create a role with `CREATE ROLE <name> REPLICATION LOGIN;` and grant that role to the user. You still need to make sure the user can connect to the database, use the schema, and to use `SELECT` on tables \(the same are required for non-CDC incremental syncs and all full refreshes\).

#### <a name="replication-plugin"></a>3. Select replication plugin

We recommend using a `pgoutput` plugin as it is the standard logical decoding plugin in Postgres. In case the replication table contains a lot of big JSON blobs and table size exceeds 1 GB, we recommend using a `wal2json` instead. Please note that `wal2json` may require additional installation for Bare Metal, VMs \(EC2/GCE/etc\), Docker, etc. For more information read [wal2json documentation](https://github.com/eulerto/wal2json).

#### <a name="replication-slot"></a>4. Create replication slot

Next, you will need to create a replication slot. Here is the query used to create a replication slot called `airbyte_slot`:

```text
SELECT pg_create_logical_replication_slot('airbyte_slot', 'pgoutput');
```

If you would like to use `wal2json` plugin, please change `pgoutput` to `wal2json` value in the above query.

#### <a name="publications-replication"></a>5. Create publications and replication identities for tables

For each table you want to replicate with CDC, you should add the replication identity \(the method of distinguishing between rows\) first. We recommend using `ALTER TABLE tbl1 REPLICA IDENTITY DEFAULT;` to use primary keys to distinguish between rows. After setting the replication identity, you will need to run `CREATE PUBLICATION airbyte_publication FOR TABLE <tbl1, tbl2, tbl3>;`. This publication name is customizable. Please refer to the [Postgres docs](https://www.postgresql.org/docs/10/sql-alterpublication.html) if you need to add or remove tables from your publication in the future.

Please note that:
- You must **add the replication identity before creating the publication**. Otherwise, `ALTER`/`UPDATE`/`DELETE` statements may fail if Postgres cannot determine how to uniquely identify rows.
- The publication should **include all the tables and only the tables that need to be synced**. Otherwise, data from these tables may not be replicated correctly.

The UI currently allows selecting any tables for CDC. If a table is selected that is not part of the publication, it will not replicate even though it is selected. If a table is part of the publication but does not have a replication identity, that replication identity will be created automatically on the first run if the Airbyte user has the necessary permissions.

#### 5. Create replication slot

Next, you will need to create a replication slot. It's important to create the publication first (as in step 4) before creating the replication slot. Otherwise, you can run into exceptions if there is any update to the database between the creation of the two.

Here is the query used to create a replication slot called `airbyte_slot`:

```text
SELECT pg_create_logical_replication_slot('airbyte_slot', 'pgoutput');
```

If you would like to use `wal2json` plugin, please change `pgoutput` to `wal2json` value in the above query.

#### 6. Start syncing

When configuring the source, select CDC and provide the replication slot and publication you just created. You should be ready to sync data with CDC!

### CDC on Bare Metal, VMs \(EC2/GCE/etc\), Docker, etc.

Some settings must be configured in the `postgresql.conf` file for your database. You can find the location of this file using `psql -U postgres -c 'SHOW config_file'` withe the correct `psql` credentials specified. Alternatively, a custom file can be specified when running postgres with the `-c` flag. For example `postgres -c config_file=/etc/postgresql/postgresql.conf` runs Postgres with the config file at `/etc/postgresql/postgresql.conf`.

If you are syncing data from a server using the `postgres` Docker image, you will need to mount a file and change the command to run Postgres with the set config file. If you're just testing CDC behavior, you may want to use a modified version of a [sample `postgresql.conf`](https://github.com/postgres/postgres/blob/master/src/backend/utils/misc/postgresql.conf.sample).

* `wal_level` is the type of coding used within the Postgres write-ahead log. This must be set to `logical` for Airbyte CDC.
* `max_wal_senders` is the maximum number of processes used for handling WAL changes. This must be at least one.
* `max_replication_slots` is the maximum number of replication slots that are allowed to stream WAL changes. This must one if Airbyte will be the only service reading subscribing to WAL changes or more if other services are also reading from the WAL.

Here is what these settings would look like in `postgresql.conf`:

```text
wal_level = logical
max_wal_senders = 1
max_replication_slots = 1
```

After setting these values you will need to restart your instance.

Finally, [follow the rest of steps above](#setting-up-cdc-for-postgres).

### CDC on AWS Postgres RDS or Aurora

* Go to the `Configuration` tab for your DB cluster.
* Find your cluster parameter group. You will either edit the parameters for this group or create a copy of this parameter group to edit. If you create a copy you will need to change your cluster's parameter group before restarting.
* Within the parameter group page, search for `rds.logical_replication`. Select this row and click on the `Edit parameters` button. Set this value to `1`.
* Wait for a maintenance window to automatically restart the instance or restart it manually.
* Finally, [follow the rest of steps above](#setting-up-cdc-for-postgres).

### CDC on Azure Database for Postgres

Use either the Azure CLI to:

```text
az postgres server configuration set --resource-group group --server-name server --name azure.replication_support --value logical
az postgres server restart --resource-group group --name server
```

Finally, [follow the rest of steps above](#setting-up-cdc-for-postgres).

## <a name="ssh-tunnel"></a>Connection via SSH Tunnel

Airbyte has the ability to connect to a Postgres instance via an SSH Tunnel. The reason you might want to do this because it is not possible \(or against security policy\) to connect to the database directly \(e.g. it does not have a public IP address\).

When using an SSH tunnel, you are configuring Airbyte to connect to an intermediate server \(a.k.a. a bastion sever\) that _does_ have direct access to the database. Airbyte connects to the bastion and then asks the bastion to connect directly to the server.

Using this feature requires additional configuration, when creating the source. We will talk through what each piece of configuration means.

1. Configure all fields for the source as you normally would, except `SSH Tunnel Method`.
2. `SSH Tunnel Method` defaults to `No Tunnel` \(meaning a direct connection\). If you want to use an SSH Tunnel choose `SSH Key Authentication` or `Password Authentication`.
   1. Choose `Key Authentication` if you will be using an RSA Private as your secrets for establishing the SSH Tunnel \(see below for more information on generating this key\).
   2. Choose `Password Authentication` if you will be using a password as your secret for establishing the SSH Tunnel.
3. `SSH Tunnel Jump Server Host` refers to the intermediate \(bastion\) server that Airbyte will connect to. This should be a hostname or an IP Address.
4. `SSH Connection Port` is the port on the bastion server with which to make the SSH connection. The default port for SSH connections is `22`, so unless you have explicitly changed something, go with the default.
5. `SSH Login Username` is the username that Airbyte should use when connection to the bastion server. This is NOT the Postgres username.
6. If you are using `Password Authentication`, then `SSH Login Username` should be set to the password of the User from the previous step. If you are using `SSH Key Authentication` leave this blank. Again, this is not the Postgres password, but the password for the OS-user that Airbyte is using to perform commands on the bastion.
7. If you are using `SSH Key Authentication`, then `SSH Private Key` should be set to the RSA Private Key that you are using to create the SSH connection. This should be the full contents of the key file starting with `-----BEGIN RSA PRIVATE KEY-----` and ending with `-----END RSA PRIVATE KEY-----`.

### Generating an RSA Private Key

The connector expects an RSA key in PEM format. To generate this key:

```text
ssh-keygen -t rsa -m PEM -f myuser_rsa
```

This produces the private key in pem format, and the public key remains in the standard format used by the `authorized_keys` file on your bastion host. The public key should be added to your bastion host to whichever user you want to use with Airbyte. The private key is provided via copy-and-paste to the Airbyte connector configuration screen, so it may log in to the bastion.

## Data type mapping

According to Postgres [documentation](https://www.postgresql.org/docs/14/datatype.html), Postgres data types are mapped to the following data types when synchronizing data. You can check the test values examples [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-postgres/src/test-integration/java/io/airbyte/integrations/io/airbyte/integration_tests/sources/PostgresSourceDatatypeTest.java). If you can't find the data type you are looking for or have any problems feel free to add a new test!

| Postgres Type                         | Resulting Type | Notes                                                                                                                                           |
|:--------------------------------------|:---------------|:------------------------------------------------------------------------------------------------------------------------------------------------|
| `bigint`                              | number         |                                                                                                                                                 |
| `bigserial`, `serial8`                | number         |                                                                                                                                                 |
| `bit`                                 | string         | Fixed-length bit string (e.g. "0100").                                                                                                          |
| `bit varying`, `varbit`               | string         | Variable-length bit string (e.g. "0100").                                                                                                       |
| `boolean`, `bool`                     | boolean        |                                                                                                                                                 |
| `box`                                 | string         |                                                                                                                                                 |
| `bytea`                               | string         | Variable length binary string with hex output format prefixed with "\x" (e.g. "\x6b707a").                                                      |
| `character`, `char`                   | string         |                                                                                                                                                 |
| `character varying`, `varchar`        | string         |                                                                                                                                                 |
| `cidr`                                | string         |                                                                                                                                                 |
| `circle`                              | string         |                                                                                                                                                 |
| `date`                                | string         | Parsed as ISO8601 date time at midnight                                                                                                         |
| `double precision`, `float`, `float8` | number         | `Infinity`, `-Infinity`, and `NaN` are not supported and converted to `null`. Issue: [#8902](https://github.com/airbytehq/airbyte/issues/8902). |
| `hstore`                              | string         |                                                                                                                                                 |
| `inet`                                | string         |                                                                                                                                                 |
| `integer`, `int`, `int4`              | number         |                                                                                                                                                 |
| `interval`                            | string         |                                                                                                                                                 |
| `json`                                | string         |                                                                                                                                                 |
| `jsonb`                               | string         |                                                                                                                                                 |
| `line`                                | string         |                                                                                                                                                 |
| `lseg`                                | string         |                                                                                                                                                 |
| `macaddr`                             | string         |                                                                                                                                                 |
| `macaddr8`                            | string         |                                                                                                                                                 |
| `money`                               | number         |                                                                                                                                                 |
| `numeric`, `decimal`                  | number         | `Infinity`, `-Infinity`, and `NaN` are not supported and converted to `null`. Issue: [#8902](https://github.com/airbytehq/airbyte/issues/8902). |
| `path`                                | string         |                                                                                                                                                 |
| `pg_lsn`                              | string         |                                                                                                                                                 |
| `point`                               | string         |                                                                                                                                                 |
| `polygon`                             | string         |                                                                                                                                                 |
| `real`, `float4`                      | number         |                                                                                                                                                 |
| `smallint`, `int2`                    | number         |                                                                                                                                                 |
| `smallserial`, `serial2`              | number         |                                                                                                                                                 |
| `serial`, `serial4`                   | number         |                                                                                                                                                 |
| `text`                                | string         |                                                                                                                                                 |
| `time`                                | string         | Parsed as a time string without a time-zone in the ISO-8601 calendar system.                                                                    |
| `timetz`                              | string         | Parsed as a time string with time-zone in the ISO-8601 calendar system.                                                                       |
| `timestamp`                           | string         | Parsed as a date-time string without a time-zone in the ISO-8601 calendar system.                                                               |
| `timestamptz`                         | string         | Parsed as a date-time string with time-zone in the ISO-8601 calendar system.                                                                  |
| `tsquery`                             | string         |                                                                                                                                                 |
| `tsvector`                            | string         |                                                                                                                                                 |
| `uuid`                                | string         |                                                                                                                                                 |
| `xml`                                 | string         |                                                                                                                                                 |
| `enum`                                | string         |                                                                                                                                                 |
| `tsrange`                             | string         |                                                                                                                                                 |
| `array`                               | array          | E.g. "[\"10001\",\"10002\",\"10003\",\"10004\"]".                                                                                               |
| composite type                        | string         |                                                                                                                                                 |

## Troubleshooting

### Sync data from Postgres hot standby server

when the connector is reading from a Postgres replica that is configured as a Hot Standby, any update from the primary server will terminate queries on the replica after a certain amount of time, default to 30 seconds. This default waiting time is obviously not enough to sync any meaning amount of data. See the `Handling Query Conflicts` section in the Postgres [documentation](https://www.postgresql.org/docs/14/hot-standby.html#HOT-STANDBY-CONFLICT) for detailed explanations.

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

One optimization on the Airbyte side is to break one large and long sync into multiple small ones. This improvement is tracked in https://github.com/airbytehq/airbyte/issues/13783.

## Changelog

| Version | Date       | Pull Request                                           | Subject                                                                                                         |
|:--------|:-----------|:-------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------|
| 0.4.29  | 2022-06-29 | [14265](https://github.com/airbytehq/airbyte/pull/14265) | Upgrade postgresql JDBC version to 42.3.5                                                                       |
| 0.4.26 | 2022-06-17 | [13864](https://github.com/airbytehq/airbyte/pull/13864) | Updated stacktrace format for any trace message errors |
| 0.4.25  | 2022-06-15 | [13823](https://github.com/airbytehq/airbyte/pull/13823) | Publish adaptive postgres source that enforces ssl on cloud + Debezium version upgrade to 1.9.2 from 1.4.2  |
| 0.4.24  | 2022-06-14 | [13549](https://github.com/airbytehq/airbyte/pull/13549) | Fixed truncated precision if the value of microseconds or seconds is 0 |
| 0.4.23  | 2022-06-13 | [13655](https://github.com/airbytehq/airbyte/pull/13745) | Fixed handling datetime cursors when upgrading from older versions of the connector |
| 0.4.22  | 2022-06-09 | [13655](https://github.com/airbytehq/airbyte/pull/13655) | Fixed bug with unsupported date-time datatypes during incremental sync |
| 0.4.21  | 2022-06-06 | [13435](https://github.com/airbytehq/airbyte/pull/13435) | Adjust JDBC fetch size based on max memory and max row size |
| 0.4.20  | 2022-06-02 | [13367](https://github.com/airbytehq/airbyte/pull/13367) | Added convertion hstore to json format |
| 0.4.19  | 2022-05-25 | [13166](https://github.com/airbytehq/airbyte/pull/13166) | Added timezone awareness and handle BC dates |
| 0.4.18  | 2022-05-25 | [13083](https://github.com/airbytehq/airbyte/pull/13083) | Add support for tsquey type |
| 0.4.17  | 2022-05-19 | [13016](https://github.com/airbytehq/airbyte/pull/13016) | CDC modify schema to allow null values |
| 0.4.16  | 2022-05-14 | [12840](https://github.com/airbytehq/airbyte/pull/12840) | Added custom JDBC parameters field |
| 0.4.15  | 2022-05-13 | [12834](https://github.com/airbytehq/airbyte/pull/12834) | Fix the bug that the connector returns empty catalog for Azure Postgres database |
| 0.4.14  | 2022-05-08 | [12689](https://github.com/airbytehq/airbyte/pull/12689) | Add table retrieval according to role-based `SELECT` privilege |
| 0.4.13  | 2022-05-05 | [10230](https://github.com/airbytehq/airbyte/pull/10230) | Explicitly set null value for field in json  |
| 0.4.12  | 2022-04-29 | [12480](https://github.com/airbytehq/airbyte/pull/12480) | Query tables with adaptive fetch size to optimize JDBC memory consumption |
| 0.4.11  | 2022-04-11 | [11729](https://github.com/airbytehq/airbyte/pull/11729) | Bump mina-sshd from 2.7.0 to 2.8.0  |
| 0.4.10  | 2022-04-08 | [11798](https://github.com/airbytehq/airbyte/pull/11798) | Fixed roles for fetching materialized view processing |
| 0.4.8   | 2022-02-21 | [10242](https://github.com/airbytehq/airbyte/pull/10242) | Fixed cursor for old connectors that use non-microsecond format. Now connectors work with both formats |
| 0.4.7   | 2022-02-18 | [10242](https://github.com/airbytehq/airbyte/pull/10242) | Updated timestamp transformation with microseconds |
| 0.4.6   | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256) | (unpublished) Add `-XX:+ExitOnOutOfMemoryError` JVM option |
| 0.4.5   | 2022-02-08 | [10173](https://github.com/airbytehq/airbyte/pull/10173) | Improved  discovering tables in case if user does not have permissions to any table |
| 0.4.4   | 2022-01-26 | [9807](https://github.com/airbytehq/airbyte/pull/9807) | Update connector fields title/description                                                                       |
| 0.4.3   | 2022-01-24 | [9554](https://github.com/airbytehq/airbyte/pull/9554) | Allow handling of java sql date in CDC                                                                          |
| 0.4.2   | 2022-01-13 | [9360](https://github.com/airbytehq/airbyte/pull/9360) | Added schema selection                                                                                          |
| 0.4.1   | 2022-01-05 | [9116](https://github.com/airbytehq/airbyte/pull/9116) | Added materialized views processing                                                                             |
| 0.4.0   | 2021-12-13 | [8726](https://github.com/airbytehq/airbyte/pull/8726) | Support all Postgres types                                                                                      |
| 0.3.17  | 2021-12-01 | [8371](https://github.com/airbytehq/airbyte/pull/8371) | Fixed incorrect handling "\n" in ssh key                                                                        |
| 0.3.16  | 2021-11-28 | [7995](https://github.com/airbytehq/airbyte/pull/7995) | Fixed money type with amount > 1000                                                                             |
| 0.3.15  | 2021-11-26 | [8066](https://github.com/airbytehq/airbyte/pull/8266) | Fixed the case, when Views are not listed during schema discovery                                               |
| 0.3.14  | 2021-11-17 | [8010](https://github.com/airbytehq/airbyte/pull/8010) | Added checking of privileges before table internal discovery                                                    |
| 0.3.13  | 2021-10-26 | [7339](https://github.com/airbytehq/airbyte/pull/7339) | Support or improve support for Interval, Money, Date, various geometric data types, inventory_items, and others |
| 0.3.12  | 2021-09-30 | [6585](https://github.com/airbytehq/airbyte/pull/6585) | Improved SSH Tunnel key generation steps                                                                        |
| 0.3.11  | 2021-09-02 | [5742](https://github.com/airbytehq/airbyte/pull/5742) | Add SSH Tunnel support                                                                                          |
| 0.3.9   | 2021-08-17 | [5304](https://github.com/airbytehq/airbyte/pull/5304) | Fix CDC OOM issue                                                                                               |
| 0.3.8   | 2021-08-13 | [4699](https://github.com/airbytehq/airbyte/pull/4699) | Added json config validator                                                                                     |
| 0.3.4   | 2021-06-09 | [3973](https://github.com/airbytehq/airbyte/pull/3973) | Add `AIRBYTE_ENTRYPOINT` for Kubernetes support                                                                 |
| 0.3.3   | 2021-06-08 | [3960](https://github.com/airbytehq/airbyte/pull/3960) | Add method field in specification parameters                                                                    |
| 0.3.2   | 2021-05-26 | [3179](https://github.com/airbytehq/airbyte/pull/3179) | Remove `isCDC` logging                                                                                          |
| 0.3.1   | 2021-04-21 | [2878](https://github.com/airbytehq/airbyte/pull/2878) | Set defined cursor for CDC                                                                                      |
| 0.3.0   | 2021-04-21 | [2990](https://github.com/airbytehq/airbyte/pull/2990) | Support namespaces                                                                                              |
| 0.2.7   | 2021-04-16 | [2923](https://github.com/airbytehq/airbyte/pull/2923) | SSL spec as optional                                                                                            |
| 0.2.6   | 2021-04-16 | [2757](https://github.com/airbytehq/airbyte/pull/2757) | Support SSL connection                                                                                          |
| 0.2.5   | 2021-04-12 | [2859](https://github.com/airbytehq/airbyte/pull/2859) | CDC bugfix                                                                                                      |
| 0.2.4   | 2021-04-09 | [2548](https://github.com/airbytehq/airbyte/pull/2548) | Support CDC                                                                                                     |
| 0.2.3   | 2021-03-28 | [2600](https://github.com/airbytehq/airbyte/pull/2600) | Add NCHAR and NVCHAR support to DB and cursor type casting                                                      |
| 0.2.2   | 2021-03-26 | [2460](https://github.com/airbytehq/airbyte/pull/2460) | Destination supports destination sync mode                                                                      |
| 0.2.1   | 2021-03-18 | [2488](https://github.com/airbytehq/airbyte/pull/2488) | Sources support primary keys                                                                                    |
| 0.2.0   | 2021-03-09 | [2238](https://github.com/airbytehq/airbyte/pull/2238) | Protocol allows future/unknown properties                                                                       |
| 0.1.13  | 2021-02-02 | [1887](https://github.com/airbytehq/airbyte/pull/1887) | Migrate AbstractJdbcSource to use iterators                                                                     |
| 0.1.12  | 2021-01-25 | [1746](https://github.com/airbytehq/airbyte/pull/1746) | Fix NPE in State Decorator                                                                                      |
| 0.1.11  | 2021-01-25 | [1765](https://github.com/airbytehq/airbyte/pull/1765) | Add field titles to specification                                                                               |
| 0.1.10  | 2021-01-19 | [1724](https://github.com/airbytehq/airbyte/pull/1724) | Fix JdbcSource handling of tables with same names in different schemas                                          |
| 0.1.9   | 2021-01-14 | [1655](https://github.com/airbytehq/airbyte/pull/1655) | Fix JdbcSource OOM                                                                                              |
| 0.1.8   | 2021-01-13 | [1588](https://github.com/airbytehq/airbyte/pull/1588) | Handle invalid numeric values in JDBC source                                                                    |
| 0.1.7   | 2021-01-08 | [1307](https://github.com/airbytehq/airbyte/pull/1307) | Migrate Postgres and MySql to use new JdbcSource                                                                |
| 0.1.6   | 2020-12-09 | [1172](https://github.com/airbytehq/airbyte/pull/1172) | Support incremental sync                                                                                        |
| 0.1.5   | 2020-11-30 | [1038](https://github.com/airbytehq/airbyte/pull/1038) | Change JDBC sources to discover more than standard schemas                                                      |
| 0.1.4   | 2020-11-30 | [1046](https://github.com/airbytehq/airbyte/pull/1046) | Add connectors using an index YAML file                                                                         |**

