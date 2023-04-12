# MySQL

## Features

| Feature                       | Supported | Notes                             |
|:------------------------------|:----------|:----------------------------------|
| Full Refresh Sync             | Yes       |                                   |
| Incremental - Append Sync     | Yes       |                                   |
| Replicate Incremental Deletes | Yes       |                                   |
| CDC                           | Yes       |                                   |
| SSL Support                   | Yes       |                                   |
| SSH Tunnel Connection         | Yes       |                                   |
| Namespaces                    | Yes       | Enabled by default                |
| Arrays                        | Yes       | Byte arrays are not supported yet |

The MySQL source does not alter the schema present in your database. Depending on the destination connected to this source, however, the schema may be altered. See the destination's documentation for more details.

## Troubleshooting

There may be problems with mapping values in MySQL's datetime field to other relational data stores. MySQL permits zero values for date/time instead of NULL which may not be accepted by other data stores. To work around this problem, you can pass the following key value pair in the JDBC connector of the source setting `zerodatetimebehavior=Converttonull`.

Some users reported that they could not connect to Amazon RDS MySQL or MariaDB. This can be diagnosed with the error message: `Cannot create a PoolableConnectionFactory`.
To solve this issue add `enabledTLSProtocols=TLSv1.2` in the JDBC parameters.

Another error that users have reported when trying to connect to Amazon RDS MySQL is `Error: HikariPool-1 - Connection is not available, request timed out after 30001ms.`. Many times this is can be due to the VPC not allowing public traffic, however, we recommend going through [this AWS troubleshooting checklist](https://aws.amazon.com/premiumsupport/knowledge-center/rds-cannot-connect/) to the correct permissions/settings have been granted to allow connection to your database.

## Getting Started \(Airbyte Cloud\)

On Airbyte Cloud, only TLS connections to your MySQL instance are supported. Other than that, you can proceed with the open-source instructions below.

## Getting Started \(Airbyte Open-Source\)

#### Requirements

1. MySQL Server `8.0`, `5.7`, or `5.6`.
2. Create a dedicated read-only Airbyte user with access to all tables needed for replication.

**1. Make sure your database is accessible from the machine running Airbyte**

This is dependent on your networking setup. The easiest way to verify if Airbyte is able to connect to your MySQL instance is via the check connection tool in the UI.

**2. Create a dedicated read-only user with access to the relevant tables \(Recommended but optional\)**

This step is optional but highly recommended to allow for better permission control and auditing. Alternatively, you can use Airbyte with an existing user in your database.

To create a dedicated database user, run the following commands against your database:

```sql
CREATE USER 'airbyte'@'%' IDENTIFIED BY 'your_password_here';
```

The right set of permissions differ between the `STANDARD` and `CDC` replication method. For `STANDARD` replication method, only `SELECT` permission is required.

```sql
GRANT SELECT ON <database name>.* TO 'airbyte'@'%';
```

For `CDC` replication method, `SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT` permissions are required.

```sql
GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'airbyte'@'%';
```

Your database user should now be ready for use with Airbyte.

**3. Set up CDC**

For `STANDARD` replication method this is not applicable. If you select the `CDC` replication method then only this is required. Please read the section on [CDC below](#change-data-capture-cdc) for more information.

**4. That's it!**

Your database user should now be ready for use with Airbyte.

## Change Data Capture \(CDC\)

- If you need a record of deletions and can accept the limitations posted below, you should be able to use CDC for MySQL.
- If your data set is small, and you just want snapshot of your table in the destination, consider using Full Refresh replication for your table instead of CDC.
- If the limitations prevent you from using CDC and your goal is to maintain a snapshot of your table in the destination, consider using non-CDC incremental and occasionally reset the data and re-sync.
- If your table has a primary key but doesn't have a reasonable cursor field for incremental syncing \(i.e. `updated_at`\), CDC allows you to sync your table incrementally.

#### CDC Limitations

- Make sure to read our [CDC docs](../../understanding-airbyte/cdc.md) to see limitations that impact all databases using CDC replication.
- Our CDC implementation uses at least once delivery for all change records.

**1. Enable binary logging**

You must enable binary logging for MySQL replication. The binary logs record transaction updates for replication tools to propagate changes. You can configure your MySQL server configuration file with the following properties, which are described in below:

```text
server-id                  = 223344
log_bin                    = mysql-bin
binlog_format              = ROW
binlog_row_image           = FULL
binlog_expire_log_seconds  = 864000
```

- server-id : The value for the server-id must be unique for each server and replication client in the MySQL cluster. The `server-id` should be a non-zero value. If the `server-id` is already set to a non-zero value, you don't need to make any change. You can set the `server-id` to any value between 1 and 4294967295. For more information refer [mysql doc](https://dev.mysql.com/doc/refman/8.0/en/replication-options.html#sysvar_server_id)
- log_bin : The value of log_bin is the base name of the sequence of binlog files. If the `log_bin` is already set, you don't need to make any change. For more information refer [mysql doc](https://dev.mysql.com/doc/refman/8.0/en/replication-options-binary-log.html#option_mysqld_log-bin)
- binlog_format : The `binlog_format` must be set to `ROW`. For more information refer [mysql doc](https://dev.mysql.com/doc/refman/8.0/en/replication-options-binary-log.html#sysvar_binlog_format)
- binlog_row_image : The `binlog_row_image` must be set to `FULL`. It determines how row images are written to the binary log. For more information refer [mysql doc](https://dev.mysql.com/doc/refman/5.7/en/replication-options-binary-log.html#sysvar_binlog_row_image)
- binlog_expire_log_seconds : This is the number of seconds for automatic binlog file removal. We recommend 864000 seconds (10 days) so that in case of a failure in sync or if the sync is paused, we still have some bandwidth to start from the last point in incremental sync. We also recommend setting frequent syncs for CDC.

**2. Enable GTIDs \(Optional\)**

Global transaction identifiers \(GTIDs\) uniquely identify transactions that occur on a server within a cluster. Though not required for a Airbyte MySQL connector, using GTIDs simplifies replication and enables you to more easily confirm if primary and replica servers are consistent. For more information refer [mysql doc](https://dev.mysql.com/doc/refman/8.0/en/replication-options-gtids.html#option_mysqld_gtid-mode)

- Enable gtid_mode : Boolean that specifies whether GTID mode of the MySQL server is enabled or not. Enable it via `mysql> gtid_mode=ON`
- Enable enforce_gtid_consistency : Boolean that specifies whether the server enforces GTID consistency by allowing the execution of statements that can be logged in a transactionally safe manner. Required when using GTIDs. Enable it via `mysql> enforce_gtid_consistency=ON`

**3. Set up initial waiting time\(Optional\)**

:::warning
This is an advanced feature. Use it if absolutely necessary.
:::

The MySQl connector may need some time to start processing the data in the CDC mode in the following scenarios:

- When the connection is set up for the first time and a snapshot is needed
- When the connector has a lot of change logs to process

The connector waits for the default initial wait time of 5 minutes (300 seconds). Setting the parameter to a longer duration will result in slower syncs, while setting it to a shorter duration may cause the connector to not have enough time to create the initial snapshot or read through the change logs. The valid range is 300 seconds to 1200 seconds.

If you know there are database changes to be synced, but the connector cannot read those changes, the root cause may be insufficient waiting time. In that case, you can increase the waiting time (example: set to 600 seconds) to test if it is indeed the root cause. On the other hand, if you know there are no database changes, you can decrease the wait time to speed up the zero record syncs.

**4. Set up server timezone\(Optional\)**

:::warning
This is an advanced feature. Use it if absolutely necessary.
:::

In CDC mode, the MySQl connector may need a timezone configured if the existing MySQL database been set up with a system timezone that is not recognized by the [IANA Timezone Database](https://www.iana.org/time-zones).

In this case, you can configure the server timezone to the equivalent IANA timezone compliant timezone. (e.g. CEST -> Europe/Berlin).

**Note**

When a sync runs for the first time using CDC, Airbyte performs an initial consistent snapshot of your database. Airbyte doesn't acquire any table locks \(for tables defined with MyISAM engine, the tables would still be locked\) while creating the snapshot to allow writes by other database clients. But in order for the sync to work without any error/unexpected behaviour, it is assumed that no schema changes are happening while the snapshot is running.

If seeing `EventDataDeserializationException` errors intermittently with root cause `EOFException` or `SocketException`, you may need to extend the following *MySql server* timeout values by running:
```
set global slave_net_timeout = 120;
set global thread_pool_idle_timeout = 120;
```
## Connection via SSH Tunnel

Airbyte has the ability to connect to a MySQl instance via an SSH Tunnel. The reason you might want to do this because it is not possible \(or against security policy\) to connect to the database directly \(e.g. it does not have a public IP address\).

When using an SSH tunnel, you are configuring Airbyte to connect to an intermediate server \(a.k.a. a bastion sever\) that _does_ have direct access to the database. Airbyte connects to the bastion and then asks the bastion to connect directly to the server.

Using this feature requires additional configuration, when creating the source. We will talk through what each piece of configuration means.

1. Configure all fields for the source as you normally would, except `SSH Tunnel Method`.
2. `SSH Tunnel Method` defaults to `No Tunnel` \(meaning a direct connection\). If you want to use an SSH Tunnel choose `SSH Key Authentication` or `Password Authentication`.

   1. Choose `Key Authentication` if you will be using an RSA private key as your secret for establishing the SSH Tunnel \(see below for more information on generating this key\).
   2. Choose `Password Authentication` if you will be using a password as your secret for establishing the SSH Tunnel.

   :::warning
   Since Airbyte Cloud requires encrypted communication, select **SSH Key Authentication** or **Password Authentication** if you selected **preferred** as the **SSL Mode**; otherwise, the connection will fail.
   :::

3. `SSH Tunnel Jump Server Host` refers to the intermediate \(bastion\) server that Airbyte will connect to. This should be a hostname or an IP Address.
4. `SSH Connection Port` is the port on the bastion server with which to make the SSH connection. The default port for SSH connections is `22`, so unless you have explicitly changed something, go with the default.
5. `SSH Login Username` is the username that Airbyte should use when connection to the bastion server. This is NOT the MySQl username.
6. If you are using `Password Authentication`, then `SSH Login Username` should be set to the password of the User from the previous step. If you are using `SSH Key Authentication` leave this blank. Again, this is not the MySQl password, but the password for the OS-user that Airbyte is using to perform commands on the bastion.
7. If you are using `SSH Key Authentication`, then `SSH Private Key` should be set to the RSA Private Key that you are using to create the SSH connection. This should be the full contents of the key file starting with `-----BEGIN RSA PRIVATE KEY-----` and ending with `-----END RSA PRIVATE KEY-----`.

### Generating an SSH Key Pair

The connector expects an RSA key in PEM format. To generate this key:

```text
ssh-keygen -t rsa -m PEM -f myuser_rsa
```

This produces the private key in pem format, and the public key remains in the standard format used by the `authorized_keys` file on your bastion host. The public key should be added to your bastion host to whichever user you want to use with Airbyte. The private key is provided via copy-and-paste to the Airbyte connector configuration screen, so it may log in to the bastion.

## Data Type Mapping

MySQL data types are mapped to the following data types when synchronizing data. You can check the test values examples [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-mysql/src/test-integration/java/io/airbyte/integrations/io/airbyte/integration_tests/sources/MySqlSourceDatatypeTest.java). If you can't find the data type you are looking for or have any problems feel free to add a new test!

| MySQL Type                                | Resulting Type         | Notes                                                                                                          |
|:------------------------------------------|:-----------------------|:---------------------------------------------------------------------------------------------------------------|
| `bit(1)`                                  | boolean                |                                                                                                                |
| `bit(>1)`                                 | base64 binary string   |                                                                                                                |
| `boolean`                                 | boolean                |                                                                                                                |
| `tinyint(1)`                              | boolean                |                                                                                                                |
| `tinyint(>1)`                             | number                 |                                                                                                                |
| `tinyint(>=1) unsigned`                   | number                 |                                                                                                                |
| `smallint`                                | number                 |                                                                                                                |
| `mediumint`                               | number                 |                                                                                                                |
| `int`                                     | number                 |                                                                                                                |
| `bigint`                                  | number                 |                                                                                                                |
| `float`                                   | number                 |                                                                                                                |
| `double`                                  | number                 |                                                                                                                |
| `decimal`                                 | number                 |                                                                                                                |
| `binary`                                  | string                 |                                                                                                                |
| `blob`                                    | string                 |                                                                                                                |
| `date`                                    | string                 | ISO 8601 date string. ZERO-DATE value will be converted to NULL. If column is mandatory, convert to EPOCH.     |
| `datetime`, `timestamp`                   | string                 | ISO 8601 datetime string. ZERO-DATE value will be converted to NULL. If column is mandatory, convert to EPOCH. |
| `time`                                    | string                 | ISO 8601 time string. Values are in range between 00:00:00 and 23:59:59.                                       |
| `year`                                    | year string            | [Doc](https://dev.mysql.com/doc/refman/8.0/en/year.html)                                                       |
| `char`, `varchar` with non-binary charset | string                 |                                                                                                                |
| `char`, `varchar` with binary charset     | base64 binary string   |                                                                                                                |
| `tinyblob`                                | base64 binary string   |                                                                                                                |
| `blob`                                    | base64 binary string   |                                                                                                                |
| `mediumblob`                              | base64 binary string   |                                                                                                                |
| `longblob`                                | base64 binary string   |                                                                                                                |
| `binary`                                  | base64 binary string   |                                                                                                                |
| `varbinary`                               | base64 binary string   |                                                                                                                |
| `tinytext`                                | string                 |                                                                                                                |
| `text`                                    | string                 |                                                                                                                |
| `mediumtext`                              | string                 |                                                                                                                |
| `longtext`                                | string                 |                                                                                                                |
| `json`                                    | serialized json string | E.g. `{"a": 10, "b": 15}`                                                                                      |
| `enum`                                    | string                 |                                                                                                                |
| `set`                                     | string                 | E.g. `blue,green,yellow`                                                                                       |
| `geometry`                                | base64 binary string   |                                                                                                                |

If you do not see a type in this list, assume that it is coerced into a string. We are happy to take feedback on preferred mappings.

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

## Changelog

| Version | Date       | Pull Request                                               | Subject                                                                                                                                                               |
|:--------|:-----------|:-----------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 2.0.14  | 2022-04-11 | [24656](https://github.com/airbytehq/airbyte/pull/24656)   | CDC minor refactor                                                                                                                                                    |
| 2.0.13  | 2022-04-06 | [24820](https://github.com/airbytehq/airbyte/pull/24820)   | Fix data loss bug during an initial failed non-CDC incremental sync                                                                                                   |
| 2.0.12  | 2022-04-04 | [24833](https://github.com/airbytehq/airbyte/pull/24833)   | Fix Debezium retry policy configuration                                                                                                                               |
| 2.0.11  | 2022-03-28 | [24166](https://github.com/airbytehq/airbyte/pull/24166)   | Fix InterruptedException bug during Debezium shutdown                                                                                                                 |
| 2.0.10  | 2022-03-27 | [24529](https://github.com/airbytehq/airbyte/pull/24373)   | Preparing the connector for CDC checkpointing                                                                                                                         |
| 2.0.9   | 2022-03-24 | [24529](https://github.com/airbytehq/airbyte/pull/24529)   | Set SSL Mode to required on strict-encrypt variant                                                                                                                    |
| 2.0.8   | 2023-03-22 | [20760](https://github.com/airbytehq/airbyte/pull/20760)   | Removed redundant date-time datatypes formatting                                                                                                                      |
| 2.0.7   | 2022-03-21 | [24207](https://github.com/airbytehq/airbyte/pull/24207)   | Fix incorrect schema change warning in CDC mode                                                                                                                       |
| 2.0.6   | 2023-03-21 | [23984](https://github.com/airbytehq/airbyte/pull/23984)   | Support CDC heartbeats                                                                                                                                                |
| 2.0.5   | 2023-03-21 | [24147](https://github.com/airbytehq/airbyte/pull/24275)   | Fix error with CDC checkpointing                                                                                                                                      |
| 2.0.4   | 2023-03-20 | [24147](https://github.com/airbytehq/airbyte/pull/24147)   | Support different table structure during "DESCRIBE" query                                                                                                             |
| 2.0.3   | 2023-03-15 | [24082](https://github.com/airbytehq/airbyte/pull/24082)   | Fixed NPE during cursor values validation                                                                                                                             |
| 2.0.2   | 2023-03-14 | [23908](https://github.com/airbytehq/airbyte/pull/23908)   | Log warning on null cursor values                                                                                                                                     |
| 2.0.1   | 2023-03-10 | [23939](https://github.com/airbytehq/airbyte/pull/23939)   | For network isolation, source connector accepts a list of hosts it is allowed to connect                                                                              |
| 2.0.0   | 2023-03-06 | [23112](https://github.com/airbytehq/airbyte/pull/23112)   | Upgrade Debezium version to 2.1.2                                                                                                                                     |
| 1.0.21  | 2023-01-25 | [20939](https://github.com/airbytehq/airbyte/pull/20939)   | Adjust batch selection memory limits databases.                                                                                                                       |
| 1.0.20  | 2023-01-24 | [20593](https://github.com/airbytehq/airbyte/pull/20593)   | Handle ssh time out exception                                                                                                                                         |
| 1.0.19  | 2022-12-14 | [20436](https://github.com/airbytehq/airbyte/pull/20346)   | Consolidate date/time values mapping for JDBC sources                                                                                                                 |
| 1.0.18  | 2022-12-14 | [20378](https://github.com/airbytehq/airbyte/pull/20378)   | Improve descriptions                                                                                                                                                  |
| 1.0.17  | 2022-12-13 | [20289](https://github.com/airbytehq/airbyte/pull/20289)   | Mark unknown column exception as config error                                                                                                                         |
| 1.0.16  | 2022-12-12 | [18959](https://github.com/airbytehq/airbyte/pull/18959)   | CDC : Don't timeout if snapshot is not complete.                                                                                                                      |
| 1.0.15  | 2022-12-06 | [20000](https://github.com/airbytehq/airbyte/pull/20000)   | Add check and better messaging when user does not have permission to access binary log in CDC mode                                                                    |
| 1.0.14  | 2022-11-22 | [19514](https://github.com/airbytehq/airbyte/pull/19514)   | Adjust batch selection memory limits databases.                                                                                                                       |
| 1.0.13  | 2022-11-14 | [18956](https://github.com/airbytehq/airbyte/pull/18956)   | Clean up Tinyint Unsigned data type identification                                                                                                                    |
| 1.0.12  | 2022-11-07 | [19025](https://github.com/airbytehq/airbyte/pull/19025)   | Stop enforce SSL if ssl mode is disabled                                                                                                                              |
| 1.0.11  | 2022-11-03 | [18851](https://github.com/airbytehq/airbyte/pull/18851)   | Fix bug with unencrypted CDC connections                                                                                                                              |
| 1.0.10  | 2022-11-02 | [18619](https://github.com/airbytehq/airbyte/pull/18619)   | Fix bug with handling Tinyint(1) Unsigned values as boolean                                                                                                           |
| 1.0.9   | 2022-10-31 | [18538](https://github.com/airbytehq/airbyte/pull/18538)   | Encode database name                                                                                                                                                  |
| 1.0.8   | 2022-10-25 | [18383](https://github.com/airbytehq/airbyte/pull/18383)   | Better SSH error handling + messages                                                                                                                                  |
| 1.0.7   | 2022-10-21 | [18263](https://github.com/airbytehq/airbyte/pull/18263)   | Fixes bug introduced in [15833](https://github.com/airbytehq/airbyte/pull/15833) and adds better error messaging for SSH tunnel in Destinations                       |
| 1.0.6   | 2022-10-19 | [18087](https://github.com/airbytehq/airbyte/pull/18087)   | Better error messaging for configuration errors (SSH configs, choosing an invalid cursor)                                                                             |
| 1.0.5   | 2022-10-17 | [18041](https://github.com/airbytehq/airbyte/pull/18041)   | Fixes bug introduced 2022-09-12 with SshTunnel, handles iterator exception properly                                                                                   |
|         | 2022-10-13 | [15535](https://github.com/airbytehq/airbyte/pull/16238)   | Update incremental query to avoid data missing when new data is inserted at the same time as a sync starts under non-CDC incremental mode                             |
| 1.0.4   | 2022-10-11 | [17815](https://github.com/airbytehq/airbyte/pull/17815)   | Expose setting server timezone for CDC syncs                                                                                                                          |
| 1.0.3   | 2022-10-07 | [17236](https://github.com/airbytehq/airbyte/pull/17236)   | Fix large table issue by fetch size                                                                                                                                   |
| 1.0.2   | 2022-10-03 | [17170](https://github.com/airbytehq/airbyte/pull/17170)   | Make initial CDC waiting time configurable                                                                                                                            |
| 1.0.1   | 2022-10-01 | [17459](https://github.com/airbytehq/airbyte/pull/17459)   | Upgrade debezium version to 1.9.6 from 1.9.2                                                                                                                          |
| 1.0.0   | 2022-09-27 | [17164](https://github.com/airbytehq/airbyte/pull/17164)   | Certify MySQL Source as Beta                                                                                                                                          |
| 0.6.15  | 2022-09-27 | [17299](https://github.com/airbytehq/airbyte/pull/17299)   | Improve error handling for strict-encrypt mysql source                                                                                                                |
| 0.6.14  | 2022-09-26 | [16954](https://github.com/airbytehq/airbyte/pull/16954)   | Implement support for snapshot of new tables in CDC mode                                                                                                              |
| 0.6.13  | 2022-09-14 | [15668](https://github.com/airbytehq/airbyte/pull/15668)   | Wrap logs in AirbyteLogMessage                                                                                                                                        |
| 0.6.12  | 2022-09-13 | [16657](https://github.com/airbytehq/airbyte/pull/16657)   | Improve CDC record queueing performance                                                                                                                               |
| 0.6.11  | 2022-09-08 | [16202](https://github.com/airbytehq/airbyte/pull/16202)   | Adds error messaging factory to UI                                                                                                                                    |
| 0.6.10  | 2022-09-08 | [16007](https://github.com/airbytehq/airbyte/pull/16007)   | Implement per stream state support.                                                                                                                                   |
| 0.6.9   | 2022-09-03 | [16216](https://github.com/airbytehq/airbyte/pull/16216)   | Standardize spec for CDC replication. See upgrade instructions [above](#upgrading-from-0.6.8-and-older-versions-to-0.6.9-and-later-versions).                         |
| 0.6.8   | 2022-09-01 | [16259](https://github.com/airbytehq/airbyte/pull/16259)   | Emit state messages more frequently                                                                                                                                   |
| 0.6.7   | 2022-08-30 | [16114](https://github.com/airbytehq/airbyte/pull/16114)   | Prevent traffic going on an unsecured channel in strict-encryption version of source mysql                                                                            |
| 0.6.6   | 2022-08-25 | [15993](https://github.com/airbytehq/airbyte/pull/15993)   | Improved support for connecting over SSL                                                                                                                              |
| 0.6.5   | 2022-08-25 | [15917](https://github.com/airbytehq/airbyte/pull/15917)   | Fix temporal data type default value bug                                                                                                                              |
| 0.6.4   | 2022-08-18 | [14356](https://github.com/airbytehq/airbyte/pull/14356)   | DB Sources: only show a table can sync incrementally if at least one column can be used as a cursor field                                                             |
| 0.6.3   | 2022-08-12 | [15044](https://github.com/airbytehq/airbyte/pull/15044)   | Added the ability to connect using different SSL modes and SSL certificates                                                                                           |
| 0.6.2   | 2022-08-11 | [15538](https://github.com/airbytehq/airbyte/pull/15538)   | Allow additional properties in db stream state                                                                                                                        |
| 0.6.1   | 2022-08-02 | [14801](https://github.com/airbytehq/airbyte/pull/14801)   | Fix multiple log bindings                                                                                                                                             |
| 0.6.0   | 2022-07-26 | [14362](https://github.com/airbytehq/airbyte/pull/14362)   | Integral columns are now discovered as int64 fields.                                                                                                                  |
| 0.5.17  | 2022-07-22 | [14714](https://github.com/airbytehq/airbyte/pull/14714)   | Clarified error message when invalid cursor column selected                                                                                                           |
| 0.5.16  | 2022-07-14 | [14574](https://github.com/airbytehq/airbyte/pull/14574)   | Removed additionalProperties:false from JDBC source connectors                                                                                                        |
| 0.5.15  | 2022-06-23 | [14077](https://github.com/airbytehq/airbyte/pull/14077)   | Use the new state management                                                                                                                                          |
| 0.5.13  | 2022-06-21 | [13945](https://github.com/airbytehq/airbyte/pull/13945)   | Aligned datatype test                                                                                                                                                 |
| 0.5.12  | 2022-06-17 | [13864](https://github.com/airbytehq/airbyte/pull/13864)   | Updated stacktrace format for any trace message errors                                                                                                                |
| 0.5.11  | 2022-05-03 | [12544](https://github.com/airbytehq/airbyte/pull/12544)   | Prevent source from hanging under certain circumstances by adding a watcher for orphaned threads.                                                                     |
| 0.5.10  | 2022-04-29 | [12480](https://github.com/airbytehq/airbyte/pull/12480)   | Query tables with adaptive fetch size to optimize JDBC memory consumption                                                                                             |
| 0.5.9   | 2022-04-06 | [11729](https://github.com/airbytehq/airbyte/pull/11729)   | Bump mina-sshd from 2.7.0 to 2.8.0                                                                                                                                    |
| 0.5.6   | 2022-02-21 | [10242](https://github.com/airbytehq/airbyte/pull/10242)   | Fixed cursor for old connectors that use non-microsecond format. Now connectors work with both formats                                                                |
| 0.5.5   | 2022-02-18 | [10242](https://github.com/airbytehq/airbyte/pull/10242)   | Updated timestamp transformation with microseconds                                                                                                                    |
| 0.5.4   | 2022-02-11 | [10251](https://github.com/airbytehq/airbyte/issues/10251) | bug Source MySQL CDC: sync failed when has Zero-date value in mandatory column                                                                                        |
| 0.5.2   | 2021-12-14 | [6425](https://github.com/airbytehq/airbyte/issues/6425)   | MySQL CDC sync fails because starting binlog position not found in DB                                                                                                 |
| 0.5.1   | 2021-12-13 | [8582](https://github.com/airbytehq/airbyte/pull/8582)     | Update connector fields title/description                                                                                                                             |
| 0.5.0   | 2021-12-11 | [7970](https://github.com/airbytehq/airbyte/pull/7970)     | Support all MySQL types                                                                                                                                               |
| 0.4.13  | 2021-12-03 | [8335](https://github.com/airbytehq/airbyte/pull/8335)     | Source-MySql: do not check cdc required param binlog_row_image for standard replication                                                                               |
| 0.4.12  | 2021-12-01 | [8371](https://github.com/airbytehq/airbyte/pull/8371)     | Fixed incorrect handling "\n" in ssh key                                                                                                                              |
| 0.4.11  | 2021-11-19 | [8047](https://github.com/airbytehq/airbyte/pull/8047)     | Source MySQL: transform binary data base64 format                                                                                                                     |
| 0.4.10  | 2021-11-15 | [7820](https://github.com/airbytehq/airbyte/pull/7820)     | Added basic performance test                                                                                                                                          |
| 0.4.9   | 2021-11-02 | [7559](https://github.com/airbytehq/airbyte/pull/7559)     | Correctly process large unsigned short integer values which may fall outside java's `Short` data type capability                                                      |
| 0.4.8   | 2021-09-16 | [6093](https://github.com/airbytehq/airbyte/pull/6093)     | Improve reliability of processing various data types like decimals, dates, datetime, binary, and text                                                                 |
| 0.4.7   | 2021-09-30 | [6585](https://github.com/airbytehq/airbyte/pull/6585)     | Improved SSH Tunnel key generation steps                                                                                                                              |
| 0.4.6   | 2021-09-29 | [6510](https://github.com/airbytehq/airbyte/pull/6510)     | Support SSL connection                                                                                                                                                |
| 0.4.5   | 2021-09-17 | [6146](https://github.com/airbytehq/airbyte/pull/6146)     | Added option to connect to DB via SSH                                                                                                                                 |
| 0.4.1   | 2021-07-23 | [4956](https://github.com/airbytehq/airbyte/pull/4956)     | Fix log link                                                                                                                                                          |
| 0.3.7   | 2021-06-09 | [3179](https://github.com/airbytehq/airbyte/pull/3973)     | Add AIRBYTE_ENTRYPOINT for Kubernetes support                                                                                                                         |
| 0.3.6   | 2021-06-09 | [3966](https://github.com/airbytehq/airbyte/pull/3966)     | Fix excessive logging for CDC method                                                                                                                                  |
| 0.3.5   | 2021-06-07 | [3890](https://github.com/airbytehq/airbyte/pull/3890)     | Fix CDC handle tinyint\(1\) and boolean types                                                                                                                         |
| 0.3.4   | 2021-06-04 | [3846](https://github.com/airbytehq/airbyte/pull/3846)     | Fix max integer value failure                                                                                                                                         |
| 0.3.3   | 2021-06-02 | [3789](https://github.com/airbytehq/airbyte/pull/3789)     | MySQL CDC poll wait 5 minutes when not received a single record                                                                                                       |
| 0.3.2   | 2021-06-01 | [3757](https://github.com/airbytehq/airbyte/pull/3757)     | MySQL CDC poll 5s to 5 min                                                                                                                                            |
| 0.3.1   | 2021-06-01 | [3505](https://github.com/airbytehq/airbyte/pull/3505)     | Implemented MySQL CDC                                                                                                                                                 |
| 0.3.0   | 2021-04-21 | [2990](https://github.com/airbytehq/airbyte/pull/2990)     | Support namespaces                                                                                                                                                    |
| 0.2.5   | 2021-04-15 | [2899](https://github.com/airbytehq/airbyte/pull/2899)     | Fix bug in tests                                                                                                                                                      |
| 0.2.4   | 2021-03-28 | [2600](https://github.com/airbytehq/airbyte/pull/2600)     | Add NCHAR and NVCHAR support to DB and cursor type casting                                                                                                            |
| 0.2.3   | 2021-03-26 | [2611](https://github.com/airbytehq/airbyte/pull/2611)     | Add an optional `jdbc_url_params` in parameters                                                                                                                       |
| 0.2.2   | 2021-03-26 | [2460](https://github.com/airbytehq/airbyte/pull/2460)     | Destination supports destination sync mode                                                                                                                            |
| 0.2.1   | 2021-03-18 | [2488](https://github.com/airbytehq/airbyte/pull/2488)     | Sources support primary keys                                                                                                                                          |
| 0.2.0   | 2021-03-09 | [2238](https://github.com/airbytehq/airbyte/pull/2238)     | Protocol allows future/unknown properties                                                                                                                             |
| 0.1.10  | 2021-02-02 | [1887](https://github.com/airbytehq/airbyte/pull/1887)     | Migrate AbstractJdbcSource to use iterators                                                                                                                           |
| 0.1.9   | 2021-01-25 | [1746](https://github.com/airbytehq/airbyte/pull/1746)     | Fix NPE in State Decorator                                                                                                                                            |
| 0.1.8   | 2021-01-19 | [1724](https://github.com/airbytehq/airbyte/pull/1724)     | Fix JdbcSource handling of tables with same names in different schemas                                                                                                |
| 0.1.7   | 2021-01-14 | [1655](https://github.com/airbytehq/airbyte/pull/1655)     | Fix JdbcSource OOM                                                                                                                                                    |
| 0.1.6   | 2021-01-08 | [1307](https://github.com/airbytehq/airbyte/pull/1307)     | Migrate Postgres and MySQL to use new JdbcSource                                                                                                                      |
| 0.1.5   | 2020-12-11 | [1267](https://github.com/airbytehq/airbyte/pull/1267)     | Support incremental sync                                                                                                                                              |
| 0.1.4   | 2020-11-30 | [1046](https://github.com/airbytehq/airbyte/pull/1046)     | Add connectors using an index YAML file                                                                                                                               |
