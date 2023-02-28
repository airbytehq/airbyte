# MySQL

This page contains the setup guide and reference information for MySQL.

## Prerequisites

* MySQL Server `8.0`, `5.7`, or `5.6`.
* Create a dedicated read-only Daspire user with access to all tables needed for replication.
* Host
* Port
* Database
* Username
* Password

## Features

| Feature | Supported | Notes |
| --- | --- | --- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |
| Replicate Incremental Deletes | Yes |
| CDC | Yes |
| SSL Support | Yes |
| SSH Tunnel Connection | Yes |
| Namespaces | Yes | Enabled by default |
| Arrays | Yes | Byte arrays are not supported yet |

The MySQL source does not alter the schema present in your database. Depending on the destination connected to this source, however, the schema may be altered. See the destination's documentation for more details.

## Setup guide

**1. Make sure your database is accessible from the machine running Daspire**

This is dependent on your networking setup. The easiest way to verify if Daspire is able to connect to your MySQL instance is via the check connection tool in the UI.

**2. Create a dedicated read-only user with access to the relevant tables (recommended but optional)**

This step is optional but highly recommended to allow for better permission control and auditing. Alternatively, you can use Daspire with an existing user in your database.

To create a dedicated database user, run the following commands against your database:

```
CREATE USER 'daspire'@'%' IDENTIFIED BY 'your_password_here'; 
```

The right set of permissions differ between the `STANDARD` and `CDC` replication method. For `STANDARD` replication method, only `SELECT` permission is required.

```
GRANT SELECT ON <database name>.* TO 'daspire'@'%';
``` 

For `CDC` replication method, `SELECT`, `RELOAD`, `SHOW DATABASES`, `REPLICATION SLAVE`, `REPLICATION CLIENT` permissions are required.

```
GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'daspire'@'%'; 
```

**3. Set up CDC**

For `STANDARD` replication method this is not applicable. If you select the `CDC` replication method then only this is required. Please read the [section on CDC](#change-data-capture-cdc) below for more information.

**4. That's it!**

Your database user should now be ready for use with Daspire.

## Change Data Capture (CDC)

* If you need a record of deletions and can accept the limitations posted below, you should be able to use CDC for MySQL.

* If your data set is small, and you just want snapshot of your table in the destination, consider using Full Refresh replication for your table instead of CDC.

* If the limitations prevent you from using CDC and your goal is to maintain a snapshot of your table in the destination, consider using non-CDC incremental and occasionally reset the data and re-sync.

* If your table has a primary key but doesn't have a reasonable cursor field for incremental syncing (i.e. `updated_at`), CDC allows you to sync your table incrementally.

### CDC Limitations

* CDC incremental is only supported for tables with primary keys. A CDC source can still choose to replicate tables without primary keys as Full Refresh or a non-CDC source can be configured for the same database to replicate the tables without primary keys using standard incremental replication.

* Data must be in tables, not views.

* The modifications you are trying to capture must be made using `DELETE`/`INSERT`/`UPDATE`. For example, changes made from `TRUNCATE`/`ALTER` won't appear in logs and therefore in your destination.

* We do not support schema changes automatically for CDC sources. We recommend resetting and resyncing data if you make a schema change.

* There are database-specific limitations. See the documentation pages for individual connectors for more information.

* The records produced by `DELETE` statements only contain primary keys. All other data fields are unset.

* Our CDC implementation uses at least once delivery for all change records.

#### 1. Enable binary logging

You must enable binary logging for MySQL replication. The binary logs record transaction updates for replication tools to propagate changes. You can configure your MySQL server configuration file with the following properties, which are described in below:

```
server-id                  = 223344
log_bin                    = mysql-bin
binlog_format              = ROW
binlog_row_image           = FULL
binlog_expire_log_seconds  = 864000
```

* `server-id`: The value for the server-id must be unique for each server and replication client in the MySQL cluster. The `server-id` should be a non-zero value. If the `server-id` is already set to a non-zero value, you don't need to make any change. You can set the `server-id` to any value between 1 and 4294967295. For more information refer [MySQL doc](https://dev.mysql.com/doc/refman/8.0/en/replication-options.html#sysvar_server_id).

* `log_bin`: The value of `log_bin` is the base name of the sequence of binlog files. If the `log_bin` is already set, you don't need to make any change. For more information refer [MySQL doc](https://dev.mysql.com/doc/refman/8.0/en/replication-options-binary-log.html#option_mysqld_log-bin).

* `binlog_format`: The `binlog_format` must be set to `ROW`. For more information refer [MySQL doc](https://dev.mysql.com/doc/refman/8.0/en/replication-options-binary-log.html#sysvar_binlog_format).

* `binlog_row_image`: The `binlog_row_image` must be set to `FULL`. It determines how row images are written to the binary log. For more information refer [MySQL doc](https://dev.mysql.com/doc/refman/5.7/en/replication-options-binary-log.html#sysvar_binlog_row_image).

* `binlog_expire_log_seconds`: This is the number of seconds for automatic binlog file removal. We recommend 864000 seconds (10 days) so that in case of a failure in sync or if the sync is paused, we still have some bandwidth to start from the last point in incremental sync. We also recommend setting frequent syncs for CDC.

#### 2. Enable GTIDs (optional)

Global transaction identifiers (GTIDs) uniquely identify transactions that occur on a server within a cluster. Though not required for Daspire MySQL setup, using GTIDs simplifies replication and enables you to more easily confirm if primary and replica servers are consistent. For more information refer [MySQL doc](https://dev.mysql.com/doc/refman/8.0/en/replication-options-gtids.html#option_mysqld_gtid-mode).

* Enable `gtid_mode`: Boolean that specifies whether GTID mode of the MySQL server is enabled or not. Enable it via `mysql> gtid_mode=ON`

* Enable `enforce_gtid_consistency`: Boolean that specifies whether the server enforces GTID consistency by allowing the execution of statements that can be logged in a transactionally safe manner. Required when using GTIDs. Enable it via `mysql> enforce_gtid_consistency=ON`

**Note**

When a sync runs for the first time using CDC, Daspire performs an initial consistent snapshot of your database. Daspire doesn't acquire any table locks (for tables defined with MyISAM engine, the tables would still be locked) while creating the snapshot to allow writes by other database clients. But in order for the sync to work without any error/unexpected behaviour, it is assumed that no schema changes are happening while the snapshot is running.

## Connection via SSH Tunnel

Daspire has the ability to connect to a MySQL instance via an SSH Tunnel. The reason you might want to do this because it is not possible (or against security policy) to connect to the database directly (e.g. it does not have a public IP address).

When using an SSH tunnel, you are configuring Daspire to connect to an intermediate server (a.k.a. a bastion server) that does have direct access to the database. Daspire connects to the bastion and then asks the bastion to connect directly to the server.

Using this feature requires additional configuration, when creating the source. We will talk through what each piece of configuration means.

1. Configure all fields for the source as you normally would, except `SSH Tunnel Method`.

2. `SSH Tunnel Method` defaults to `No Tunnel` (meaning a direct connection). If you want to use an SSH Tunnel choose `SSH Key Authentication` or `Password Authentication`.

  * Choose `Key Authentication` if you will be using an RSA private key as your secret for establishing the SSH Tunnel (see below for more information on generating this key).

  * Choose `Password Authentication` if you will be using a password as your secret for establishing the SSH Tunnel.

3. `SSH Tunnel Jump Server Host` refers to the intermediate (bastion) server that Daspire will connect to. This should be a hostname or an IP Address.

4. `SSH Connection Port` is the port on the bastion server with which to make the SSH connection. The default port for SSH connections is `22`, so unless you have explicitly changed something, go with the default.

5. `SSH Login Username` is the username that Daspire should use when connection to the bastion server. This is NOT the MySQL username.

6. If you are using `Password Authentication`, then `SSH Login Username` should be set to the password of the User from the previous step. If you are using `SSH Key Authentication` leave this blank. Again, this is not the MySQL password, but the password for the OS-user that Daspire is using to perform commands on the bastion.

7. If you are using `SSH Key Authentication`, then `SSH Private Key` should be set to the RSA Private Key that you are using to create the SSH connection. This should be the full contents of the key file starting with `-----BEGIN RSA PRIVATE KEY-----` and ending with `-----END RSA PRIVATE KEY-----`.

### Generating an SSH Key Pair

The connector expects an RSA key in PEM format. To generate this key:

```
ssh-keygen -t rsa -m PEM -f myuser_rsa
```

This produces the private key in pem format, and the public key remains in the standard format used by the `authorized_keys` file on your bastion host. The public key should be added to your bastion host to whichever user you want to use with Daspire. The private key is provided via copy-and-paste to the Daspire connection configuration screen, so it may log in to the bastion.

## Data type mapping

| MySQL Type | Daspire Type | Note |
| --- | --- | --- |
| `bit(1)` | boolean |
| `bit(\>1)` | base64 binary string |
| `boolean` | boolean |
| `tinyint(1)` | boolean |
| `tinyint(\>1)` | boolean |
| `smallint` | number |
| `mediumint` | number |
| `int` | number |
| `bigint` | number |
| `float` | number |
| `double` | number |
| `decimal` | number |
| `binary` | string |
| `blob` | string |
| `date` | string | ISO 8601 date string. ZERO-DATE value will be converted to NULL. If column is mandatory, convert to EPOCH. |
| `datetime`, `timestamp` | string | ISO 8601 datetime string. ZERO-DATE value will be converted to NULL. If column is mandatory, convert to EPOCH. |
| `time` | string | ISO 8601 time string. Values are in range between 00:00:00 and 23:59:59. |
| `year` | year string | [Doc](https://dev.mysql.com/doc/refman/8.0/en/year.html) |
| `char`, `varchar` with non-binary charset | string |
| `char`, `varchar` with binary charset | base64 binary string |
| `tinyblob` | base64 binary string |
| `blob` | base64 binary string |
| `mediumblob` | base64 binary string |
| `longblob` | base64 binary string |
| `binary` | base64 binary string |
| `varbinary` | base64 binary string |
| `tinytext` | string |
| `text` | string |
| `mediumtext` | string |
| `longtext` | string |
| `json` | serialized json string | E.g. {"a": 10, "b": 15} |
| `enum` | string |
| `set` | string | E.g. blue,green,yellow |
| `geometry` | base64 binary string |

Note: If you do not see a type in this list, assume that it is coerced into a string.

## Troubleshooting

There may be problems with mapping values in MySQL's datetime field to other relational data stores. MySQL permits zero values for date/time instead of NULL which may not be accepted by other data stores. To work around this problem, you can pass the following key value pair in the JDBC connector of the source setting `zerodatetimebehavior=Converttonull`.

Some users reported that they could not connect to Amazon RDS MySQL or MariaDB. This can be diagnosed with the error message: `Cannot create a PoolableConnectionFactory`. To solve this issue add `enabledTLSProtocols=TLSv1.2` in the JDBC parameters.

Another error that users have reported when trying to connect to Amazon RDS MySQL is `Error: HikariPool-1 - Connection is not available, request timed out after 30001ms.`. Many times this can be due to the VPC not allowing public traffic. However, we recommend going through [this AWS troubleshooting checklist](https://aws.amazon.com/premiumsupport/knowledge-center/rds-cannot-connect/) to the correct permissions/settings have been granted to allow connection to your database.