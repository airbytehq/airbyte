# MySQL

## Overview

The MySQL source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Resulting schema

The MySQL source does not alter the schema present in your database. Depending on the destination connected to this source, however, the schema may be altered. See the destination's documentation for more details.

### Data type mapping

MySQL data types are mapped to the following data types when synchronizing data.
You can check the test values examples [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-mysql/src/test-integration/java/io/airbyte/integrations/source/mysql/MySqlSourceComprehensiveTest.java).
If you can't find the data type you are looking for or have any problems feel free to add a new test!

| MySQL Type | Resulting Type | Notes |
| :--- | :--- | :--- |
| `array` | array |  |
| `bigint` | number |  |
| `binary` | string |  |
| `blob` | string |  |
| `date` | string |  |
| `datetime` | string |  |
| `decimal` | number |  |
| `decimal(19, 2)` | number |  |
| `double` | number |  |
| `enum` | string |  |
| `float` | number |  |
| `int` | number |  |
| `int unsigned` | number |  |
| `int zerofill` | number |  |
| `json` | text |  |
| `mediumint` | number |  |
| `mediumint zerofill` | number |  |
| `mediumint` | number |  |
| `numeric` | number |  |
| `point` | object |  |
| `smallint` | number |  |
| `smallint zerofill` | number |  |
| `string` | string |  |
| `tinyint` | number |  |
| `text` | string |  |
| `time` | string |  |
| `timestamp` | string |  |
| `tinytext` | string |  |
| `varbinary(256)` | string |  |
| `varchar` | string |  |
| `varchar(256) character set cp1251` | string |  |
| `varchar(256) character set utf16` | string |  |

If you do not see a type in this list, assume that it is coerced into a string. We are happy to take feedback on preferred mappings.

**Note:** arrays for all the above types as well as custom types are supported, although they may be de-nested depending on the destination. Byte arrays are currently unsupported.

### Features

| Feature | Supported | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | Yes |  |
| Replicate Incremental Deletes | Yes |  |
| CDC | Yes |  |
| SSL Support | Yes |  |
| SSH Tunnel Connection | Coming soon |  |
| Namespaces | Yes | Enabled by default |

## Getting started

### Requirements

1. MySQL Server `8.0`, `5.7`, or `5.6`.
2. Create a dedicated read-only Airbyte user with access to all tables needed for replication

### Setup guide

#### 1. Make sure your database is accessible from the machine running Airbyte

This is dependent on your networking setup. The easiest way to verify if Airbyte is able to connect to your MySQL instance is via the check connection tool in the UI.

#### 2. Create a dedicated read-only user with access to the relevant tables \(Recommended but optional\)

This step is optional but highly recommended to allow for better permission control and auditing. Alternatively, you can use Airbyte with an existing user in your database.

To create a dedicated database user, run the following commands against your database:

```sql
CREATE USER 'airbyte'@'%' IDENTIFIED BY 'your_password_here';
```

The right set of permissions differ between the `STANDARD` and `CDC` replication method. 
For `STANDARD` replication method, only `SELECT` permission is required.

```sql
GRANT SELECT ON <database name>.* TO 'airbyte'@'%';
```
For `CDC` replication method, `SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT` permissions are required.
```sql
GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'airbyte'@'%';
```

Your database user should now be ready for use with Airbyte.

#### 3. Set up CDC

For `STANDARD` replication method this is not applicable. If you select the `CDC` replication method then only this is required. Please read [the section on CDC below](mysql.md#setting-up-cdc-for-mysql) for more information.

#### 4. That's it!

Your database user should now be ready for use with Airbyte.


## Change Data Capture \(CDC\)

* If you need a record of deletions and can accept the limitations posted below, you should be able to use CDC for MySQL.
* If your data set is small, and you just want snapshot of your table in the destination, consider using Full Refresh replication for your table instead of CDC.
* If the limitations prevent you from using CDC and your goal is to maintain a snapshot of your table in the destination, consider using non-CDC incremental and occasionally reset the data and re-sync.
* If your table has a primary key but doesn't have a reasonable cursor field for incremental syncing \(i.e. `updated_at`\), CDC allows you to sync your table incrementally.

### CDC Limitations

* Make sure to read our [CDC docs](../../understanding-airbyte/cdc.md) to see limitations that impact all databases using CDC replication.
* Our CDC implementation uses at least once delivery for all change records.

### Setting up CDC for MySQL

You must enable binary logging for MySQL replication. The binary logs record transaction updates for replication tools to propagate changes.

#### Enable binary logging

You must enable binary logging for MySQL replication. The binary logs record transaction updates for replication tools to propagate changes. You can configure your MySQL server configuration file with the following properties, which are described in below:
```
server-id         = 223344
log_bin           = mysql-bin
binlog_format     = ROW
binlog_row_image  = FULL
expire_logs_days  = 10
```
* server-id : The value for the server-id must be unique for each server and replication client in the MySQL cluster. The `server-id` should be a non-zero value. If the `server-id` is already set to a non-zero value, you don't need to make any change. You can set the `server-id` to any value between 1 and 4294967295. For more information refer [mysql doc](https://dev.mysql.com/doc/refman/8.0/en/replication-options.html#sysvar_server_id) 
* log_bin :  The value of log_bin is the base name of the sequence of binlog files. If the `log_bin` is already set, you don't need to make any change. For more information refer [mysql doc](https://dev.mysql.com/doc/refman/8.0/en/replication-options-binary-log.html#option_mysqld_log-bin)
* binlog_format : The `binlog_format` must be set to `ROW`. For more information refer [mysql doc](https://dev.mysql.com/doc/refman/8.0/en/replication-options-binary-log.html#sysvar_binlog_format)
* binlog_row_image : The `binlog_row_image` must be set to `FULL`. It determines how row images are written to the binary log. For more information refer [mysql doc](https://dev.mysql.com/doc/refman/5.7/en/replication-options-binary-log.html#sysvar_binlog_row_image)
* expire_logs_days : This is the number of days for automatic binlog file removal. We recommend 10 days so that in case of a failure in sync or if the sync is paused, we still have some bandwidth to start from the last point in incremental sync. We also recommend setting frequent syncs for CDC.

#### Enable GTIDs \(Optional\)

Global transaction identifiers (GTIDs) uniquely identify transactions that occur on a server within a cluster. 
Though not required for a Airbyte MySQL connector, using GTIDs simplifies replication and enables you to more easily confirm if primary and replica servers are consistent.
For more information refer [mysql doc](https://dev.mysql.com/doc/refman/8.0/en/replication-options-gtids.html#option_mysqld_gtid-mode)
* Enable gtid_mode : Boolean that specifies whether GTID mode of the MySQL server is enabled or not. Enable it via `mysql> gtid_mode=ON`
* Enable enforce_gtid_consistency : Boolean that specifies whether the server enforces GTID consistency by allowing the execution of statements that can be logged in a transactionally safe manner. Required when using GTIDs. Enable it via `mysql> enforce_gtid_consistency=ON`

#### Note 

When a sync runs for the first time using CDC, Airbyte performs an initial consistent snapshot of your database. 
Airbyte doesn't acquire any table locks (for tables defined with MyISAM engine, the tables would still be locked) while creating the snapshot to allow writes by other database clients. 
But in order for the sync to work without any error/unexpected behaviour, it is assumed that no schema changes are happening while the snapshot is running.

## Troubleshooting

There may be problems with mapping values in MySQL's datetime field to other relational data stores. MySQL permits zero values for date/time instead of NULL which may not be accepted by other data stores. To work around this problem, you can pass the following key value pair in the JDBC connector of the source setting `zerodatetimebehavior=Converttonull`.

## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.4.1   | 2021-07-23 | [4956](https://github.com/airbytehq/airbyte/pull/4956) | Fix log link |
| 0.3.7   | 2021-06-09 | [3179](https://github.com/airbytehq/airbyte/pull/3973) | Add AIRBYTE_ENTRYPOINT for Kubernetes support |
| 0.3.6   | 2021-06-09 | [3966](https://github.com/airbytehq/airbyte/pull/3966) | Fix excessive logging for CDC method |
| 0.3.5   | 2021-06-07 | [3890](https://github.com/airbytehq/airbyte/pull/3890) | Fix CDC handle tinyint(1) and boolean types |
| 0.3.4   | 2021-06-04 | [3846](https://github.com/airbytehq/airbyte/pull/3846) | Fix max integer value failure |
| 0.3.3   | 2021-06-02 | [3789](https://github.com/airbytehq/airbyte/pull/3789) | MySQL CDC poll wait 5 minutes when not received a single record |
| 0.3.2   | 2021-06-01 | [3757](https://github.com/airbytehq/airbyte/pull/3757) | MySQL CDC poll 5s to 5 min |
| 0.3.1   | 2021-06-01 | [3505](https://github.com/airbytehq/airbyte/pull/3505) | Implemented MySQL CDC |
| 0.3.0   | 2021-04-21 | [2990](https://github.com/airbytehq/airbyte/pull/2990) | Support namespaces |
| 0.2.5   | 2021-04-15 | [2899](https://github.com/airbytehq/airbyte/pull/2899) | Fix bug in tests |
| 0.2.4   | 2021-03-28 | [2600](https://github.com/airbytehq/airbyte/pull/2600) | Add NCHAR and NVCHAR support to DB and cursor type casting |
| 0.2.3   | 2021-03-26 | [2611](https://github.com/airbytehq/airbyte/pull/2611) | Add an optional `jdbc_url_params` in parameters |
| 0.2.2   | 2021-03-26 | [2460](https://github.com/airbytehq/airbyte/pull/2460) | Destination supports destination sync mode |
| 0.2.1   | 2021-03-18 | [2488](https://github.com/airbytehq/airbyte/pull/2488) | Sources support primary keys |
| 0.2.0   | 2021-03-09 | [2238](https://github.com/airbytehq/airbyte/pull/2238) | Protocol allows future/unknown properties |
| 0.1.10  | 2021-02-02 | [1887](https://github.com/airbytehq/airbyte/pull/1887) | Migrate AbstractJdbcSource to use iterators |
| 0.1.9  | 2021-01-25 | [1746](https://github.com/airbytehq/airbyte/pull/1746) | Fix NPE in State Decorator |
| 0.1.8  | 2021-01-19 | [1724](https://github.com/airbytehq/airbyte/pull/1724) | Fix JdbcSource handling of tables with same names in different schemas |
| 0.1.7   | 2021-01-14 | [1655](https://github.com/airbytehq/airbyte/pull/1655) | Fix JdbcSource OOM |
| 0.1.6   | 2021-01-08 | [1307](https://github.com/airbytehq/airbyte/pull/1307) | Migrate Postgres and MySQL to use new JdbcSource |
| 0.1.5   | 2020-12-11 | [1267](https://github.com/airbytehq/airbyte/pull/1267) | Support incremental sync |
| 0.1.4   | 2020-11-30 | [1046](https://github.com/airbytehq/airbyte/pull/1046) | Add connectors using an index YAML file |
