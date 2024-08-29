# Microsoft SQL Server (MSSQL)

Airbyte's certified MSSQL connector offers the following features:

- Multiple methods of keeping your data fresh, including
  [Change Data Capture (CDC)](https://docs.airbyte.com/understanding-airbyte/cdc) using the
  [binlog](https://dev.mysql.com/doc/refman/8.0/en/binary-log.html).
- Incremental as well as Full Refresh
  [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes), providing
  flexibility in how data is delivered to your destination.
- Reliable replication at any table size with
  [checkpointing](https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/#state--checkpointing)
  and chunking of database reads.

> ⚠️ **Please note the minimum required platform version is v0.58.0 to run source-mssql 4.0.18 and above.**

## Features

| Feature                       | Supported | Notes              |
| :---------------------------- | :-------- | :----------------- |
| Full Refresh Sync             | Yes       |                    |
| Incremental Sync - Append     | Yes       |                    |
| Replicate Incremental Deletes | Yes       |                    |
| CDC \(Change Data Capture\)   | Yes       |                    |
| SSL Support                   | Yes       |                    |
| SSH Tunnel Connection         | Yes       |                    |
| Namespaces                    | Yes       | Enabled by default |

The MSSQL source does not alter the schema present in your database. Depending on the destination
connected to this source, however, the schema may be altered. See the destination's documentation
for more details.

## Getting Started

#### Requirements

1. MSSQL Server `Azure SQL Database`, `Azure Synapse Analytics`, `Azure SQL Managed Instance`,
   `SQL Server 2019`, `SQL Server 2017`, `SQL Server 2016`, `SQL Server 2014`, `SQL Server 2012`,
   `PDW 2008R2 AU34`.
2. Create a dedicated read-only Airbyte user with access to all tables needed for replication
3. If you want to use CDC, please see [the relevant section below](mssql.md#change-data-capture-cdc)
   for further setup requirements

#### 1. Make sure your database is accessible from the machine running Airbyte

This is dependent on your networking setup. The easiest way to verify if Airbyte is able to connect
to your MSSQL instance is via the check connection tool in the UI.

#### 2. Create a dedicated read-only user with access to the relevant tables \(Recommended but optional\)

This step is optional but highly recommended to allow for better permission control and auditing.
Alternatively, you can use Airbyte with an existing user in your database.

#### 3. Your database user should now be ready for use with Airbyte!

#### Airbyte Cloud

On Airbyte Cloud, only secured connections to your MSSQL instance are supported in source
configuration. You may either configure your connection using one of the supported SSL Methods or by
using an SSH Tunnel.

## Change Data Capture \(CDC\)

We use
[SQL Server's change data capture feature](https://docs.microsoft.com/en-us/sql/relational-databases/track-changes/about-change-data-capture-sql-server?view=sql-server-2017)
with transaction logs to capture row-level `INSERT`, `UPDATE` and `DELETE` operations that occur on
CDC-enabled tables.

Some extra setup requiring at least _db_owner_ permissions on the database\(s\) you intend to sync
from will be required \(detailed [below](mssql.md#setting-up-cdc-for-mssql)\).

Please read the [CDC docs](../../understanding-airbyte/cdc.md) for an overview of how Airbyte
approaches CDC.

### Should I use CDC for MSSQL?

- If you need a record of deletions and can accept the limitations posted below, CDC is the way to
  go!
- If your data set is small and/or you just want a snapshot of your table in the destination,
  consider using Full Refresh replication for your table instead of CDC.
- If the limitations below prevent you from using CDC and your goal is to maintain a snapshot of
  your table in the destination, consider using non-CDC incremental and occasionally reset the data
  and re-sync.
- If your table has a primary key but doesn't have a reasonable cursor field for incremental syncing
  \(i.e. `updated_at`\), CDC allows you to sync your table incrementally.

#### CDC Limitations

- Make sure to read our [CDC docs](../../understanding-airbyte/cdc.md) to see limitations that
  impact all databases using CDC replication.
- `hierarchyid` and `sql_variant` types are not processed in CDC migration type (not supported by
  Debezium). For more details please check
  [this ticket](https://github.com/airbytehq/airbyte/issues/14411)
- CDC is only available for SQL Server 2016 Service Pack 1 \(SP1\) and later.
- _db_owner_ \(or higher\) permissions are required to perform the
  [neccessary setup](mssql.md#setting-up-cdc-for-mssql) for CDC.
- On Linux, CDC is not supported on versions earlier than SQL Server 2017 CU18 \(SQL Server 2019 is
  supported\).
- Change data capture cannot be enabled on tables with a clustered columnstore index. \(It can be
  enabled on tables with a _non-clustered_ columnstore index\).
- The SQL Server CDC feature processes changes that occur in user-created tables only. You cannot
  enable CDC on the SQL Server master database.
- Using variables with partition switching on databases or tables with change data capture \(CDC\)
  is not supported for the `ALTER TABLE` ... `SWITCH TO` ... `PARTITION` ... statement
- Our CDC implementation uses at least once delivery for all change records.
- Read more on CDC limitations in the
  [Microsoft docs](https://docs.microsoft.com/en-us/sql/relational-databases/track-changes/about-change-data-capture-sql-server?view=sql-server-2017#limitations).

### Setting up CDC for MSSQL

#### 1. Enable CDC on database and tables

MS SQL Server provides some built-in stored procedures to enable CDC.

- To enable CDC, a SQL Server administrator with the necessary privileges \(_db_owner_ or
  _sysadmin_\) must first run a query to enable CDC at the database level.

  ```text
  USE {database name}
  GO
  EXEC sys.sp_cdc_enable_db
  GO
  ```

- The administrator must then enable CDC for each table that you want to capture. Here's an example:

  ```text
  USE {database name}
  GO

  EXEC sys.sp_cdc_enable_table
  @source_schema = N'{schema name}',
  @source_name   = N'{table name}',
  @role_name     = N'{role name}',  [1]
  @filegroup_name = N'{filegroup name}', [2]
  @supports_net_changes = 0 [3]
  GO
  ```

  - \[1\] Specifies a role which will gain `SELECT` permission on the captured columns of the source
    table. We suggest putting a value here so you can use this role in the next step but you can
    also set the value of @role*name to `NULL` to allow only \_sysadmin* and _db_owner_ to have
    access. Be sure that the credentials used to connect to the source in Airbyte align with this
    role so that Airbyte can access the cdc tables.
  - \[2\] Specifies the filegroup where SQL Server places the change table. We recommend creating a
    separate filegroup for CDC but you can leave this parameter out to use the default filegroup.
  - \[3\] If 0, only the support functions to query for all changes are generated. If 1, the
    functions that are needed to query for net changes are also generated. If supports_net_changes
    is set to 1, index_name must be specified, or the source table must have a defined primary key.

- \(For more details on parameters, see the
  [Microsoft doc page](https://docs.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sys-sp-cdc-enable-table-transact-sql?view=sql-server-ver15)
  for this stored procedure\).
- If you have many tables to enable CDC on and would like to avoid having to run this query
  one-by-one for every table,
  [this script](http://www.techbrothersit.com/2013/06/change-data-capture-cdc-sql-server_69.html)
  might help!

For further detail, see the
[Microsoft docs on enabling and disabling CDC](https://docs.microsoft.com/en-us/sql/relational-databases/track-changes/enable-and-disable-change-data-capture-sql-server?view=sql-server-ver15).

#### 2. Enable snapshot isolation

- When a sync runs for the first time using CDC, Airbyte performs an initial consistent snapshot of
  your database. To avoid acquiring table locks, Airbyte uses _snapshot isolation_, allowing
  simultaneous writes by other database clients. This must be enabled on the database like so:

  ```text
  ALTER DATABASE {database name}
    SET ALLOW_SNAPSHOT_ISOLATION ON;
  ```

#### 3. Create a user and grant appropriate permissions

- Rather than use _sysadmin_ or _db_owner_ credentials, we recommend creating a new user with the
  relevant CDC access for use with Airbyte. First let's create the login and user and add to the
  [db_datareader](https://docs.microsoft.com/en-us/sql/relational-databases/security/authentication-access/database-level-roles?view=sql-server-ver15)
  role:

  ```text
  USE {database name};
  CREATE LOGIN {user name}
    WITH PASSWORD = '{password}';
  CREATE USER {user name} FOR LOGIN {user name};
  EXEC sp_addrolemember 'db_datareader', '{user name}';
  ```

  - Add the user to the role specified earlier when enabling cdc on the table\(s\):

    ```text
    EXEC sp_addrolemember '{role name}', '{user name}';
    ```

  - This should be enough access, but if you run into problems, try also directly granting the user
    `SELECT` access on the cdc schema:

    ```text
    USE {database name};
    GRANT SELECT ON SCHEMA :: [cdc] TO {user name};
    ```

  - If feasible, granting this user 'VIEW SERVER STATE' permissions will allow Airbyte to check
    whether or not the
    [SQL Server Agent](https://docs.microsoft.com/en-us/sql/relational-databases/track-changes/about-change-data-capture-sql-server?view=sql-server-ver15#relationship-with-log-reader-agent)
    is running. This is preferred as it ensures syncs will fail if the CDC tables are not being
    updated by the Agent in the source database.

    ```text
    USE master;
    GRANT VIEW SERVER STATE TO {user name};
    ```

#### 4. Extend the retention period of CDC data

- In SQL Server, by default, only three days of data are retained in the change tables. Unless you
  are running very frequent syncs, we suggest increasing this retention so that in case of a failure
  in sync or if the sync is paused, there is still some bandwidth to start from the last point in
  incremental sync.
- These settings can be changed using the stored procedure
  [sys.sp_cdc_change_job](https://docs.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sys-sp-cdc-change-job-transact-sql?view=sql-server-ver15)
  as below:

  ```text
  -- we recommend 14400 minutes (10 days) as retention period
  EXEC sp_cdc_change_job @job_type='cleanup', @retention = {minutes}
  ```

- After making this change, a restart of the cleanup job is required:

```text
  EXEC sys.sp_cdc_stop_job @job_type = 'cleanup';

  EXEC sys.sp_cdc_start_job @job_type = 'cleanup';
```

#### 5. Ensure the SQL Server Agent is running

- MSSQL uses the SQL Server Agent

  to
  [run the jobs necessary](https://docs.microsoft.com/en-us/sql/relational-databases/track-changes/about-change-data-capture-sql-server?view=sql-server-ver15#agent-jobs)

  for CDC. It is therefore vital that the Agent is operational in order for to CDC to work
  effectively. You can check

  the status of the SQL Server Agent as follows:

```text
  EXEC xp_servicecontrol 'QueryState', N'SQLServerAGENT';
```

- If you see something other than 'Running.' please follow

  the
  [Microsoft docs](https://docs.microsoft.com/en-us/sql/ssms/agent/start-stop-or-pause-the-sql-server-agent-service?view=sql-server-ver15)

  to start the service.

## Connection to MSSQL via an SSH Tunnel

Airbyte has the ability to connect to a MSSQL instance via an SSH Tunnel. The reason you might want
to do this because it is not possible \(or against security policy\) to connect to the database
directly \(e.g. it does not have a public IP address\).

When using an SSH tunnel, you are configuring Airbyte to connect to an intermediate server \(a.k.a.
a bastion sever\) that _does_ have direct access to the database. Airbyte connects to the bastion
and then asks the bastion to connect directly to the server.

Using this feature requires additional configuration, when creating the source. We will talk through
what each piece of configuration means.

1. Configure all fields for the source as you normally would, except `SSH Tunnel Method`.
2. `SSH Tunnel Method` defaults to `No Tunnel` \(meaning a direct connection\). If you want to use
   an

   SSH Tunnel choose `SSH Key Authentication` or `Password Authentication`.

   1. Choose `Key Authentication` if you will be using an RSA private key as your secret for

      establishing the SSH Tunnel \(see below for more information on generating this key\).

   2. Choose `Password Authentication` if you will be using a password as your secret for
      establishing

      the SSH Tunnel.

3. `SSH Tunnel Jump Server Host` refers to the intermediate \(bastion\) server that Airbyte will
   connect to. This should

   be a hostname or an IP Address.

4. `SSH Connection Port` is the port on the bastion server with which to make the SSH connection.
   The default port for

   SSH connections is `22`, so unless you have explicitly changed something, go with the default.

5. `SSH Login Username` is the username that Airbyte should use when connection to the bastion
   server. This is NOT the

   MSSQL username.

6. If you are using `Password Authentication`, then `SSH Login Username` should be set to the

   password of the User from the previous step. If you are using `SSH Key Authentication` leave this

   blank. Again, this is not the MSSQL password, but the password for the OS-user that Airbyte is

   using to perform commands on the bastion.

7. If you are using `SSH Key Authentication`, then `SSH Private Key` should be set to the RSA

   private Key that you are using to create the SSH connection. This should be the full contents of

   the key file starting with `-----BEGIN RSA PRIVATE KEY-----` and ending

   with `-----END RSA PRIVATE KEY-----`.

### Generating an SSH Key Pair

The connector expects an RSA key in PEM format. To generate this key:

```text
ssh-keygen -t rsa -m PEM -f myuser_rsa
```

This produces the private key in pem format, and the public key remains in the standard format used
by the `authorized_keys` file on your bastion host. The public key should be added to your bastion
host to whichever user you want to use with Airbyte. The private key is provided via copy-and-paste
to the Airbyte connector configuration screen, so it may log in to the bastion.

## Data type mapping

MSSQL data types are mapped to the following data types when synchronizing data. You can check the
test values examples
[here](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-mssql/src/test-integration/java/io/airbyte/integrations/source/mssql/MssqlSourceComprehensiveTest.java).
If you can't find the data type you are looking for or have any problems feel free to add a new
test!

| MSSQL Type                                              | Resulting Type          | Notes |
| :------------------------------------------------------ | :---------------------- | :---- |
| `bigint`                                                | number                  |       |
| `binary`                                                | string                  |       |
| `bit`                                                   | boolean                 |       |
| `char`                                                  | string                  |       |
| `date`                                                  | date                    |       |
| `datetime`                                              | timestamp               |       |
| `datetime2`                                             | timestamp               |       |
| `datetimeoffset`                                        | timestamp with timezone |       |
| `decimal`                                               | number                  |       |
| `int`                                                   | number                  |       |
| `float`                                                 | number                  |       |
| `geography`                                             | string                  |       |
| `geometry`                                              | string                  |       |
| `money`                                                 | number                  |       |
| `numeric`                                               | number                  |       |
| `ntext`                                                 | string                  |       |
| `nvarchar`                                              | string                  |       |
| `nvarchar(max)`                                         | string                  |       |
| `real`                                                  | number                  |       |
| `smalldatetime`                                         | timestamp               |       |
| `smallint`                                              | number                  |       |
| `smallmoney`                                            | number                  |       |
| `sql_variant`                                           | string                  |       |
| `uniqueidentifier`                                      | string                  |       |
| `text`                                                  | string                  |       |
| `time`                                                  | time                    |       |
| `tinyint`                                               | number                  |       |
| `varbinary`                                             | string                  |       |
| `varchar`                                               | string                  |       |
| `varchar(max) COLLATE Latin1_General_100_CI_AI_SC_UTF8` | string                  |       |
| `xml`                                                   | string                  |       |

If you do not see a type in this list, assume that it is coerced into a string. We are happy to take
feedback on preferred mappings.

## Upgrading from 0.4.17 and older versions to 0.4.18 and newer versions

There is a backwards incompatible spec change between Microsoft SQL Source connector versions 0.4.17
and 0.4.18. As part of that spec change `replication_method` configuration parameter was changed to
`object` from `string`.

In Microsoft SQL source connector versions 0.4.17 and older, `replication_method` configuration
parameter was saved in the configuration database as follows:

```
"replication_method": "STANDARD"
```

Starting with version 0.4.18, `replication_method` configuration parameter is saved as follows:

```
"replication_method": {
    "method": "STANDARD"
}
```

After upgrading Microsoft SQL Source connector from 0.4.17 or older version to 0.4.18 or newer
version you need to fix source configurations in the `actor` table in Airbyte database. To do so,
you need to run two SQL queries. Follow the instructions in
[Airbyte documentation](https://docs.airbyte.com/operator-guides/configuring-airbyte-db/#accessing-the-default-database-located-in-docker-airbyte-db)
to run SQL queries on Airbyte database.

If you have connections with Microsoft SQL Source using _Standard_ replication method, run this SQL:

```sql
update public.actor set configuration =jsonb_set(configuration, '{replication_method}', '{"method": "STANDARD"}', true)
WHERE actor_definition_id ='b5ea17b1-f170-46dc-bc31-cc744ca984c1' AND (configuration->>'replication_method' = 'STANDARD');
```

If you have connections with Microsoft SQL Source using _Logicai Replication (CDC)_ method, run this
SQL:

```sql
update public.actor set configuration =jsonb_set(configuration, '{replication_method}', '{"method": "CDC"}', true)
WHERE actor_definition_id ='b5ea17b1-f170-46dc-bc31-cc744ca984c1' AND (configuration->>'replication_method' = 'CDC');
```

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                                                                                      | Subject                                                                                                                                         |
|:--------|:-----------|:------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------|
| 4.1.10  | 2024-08-27 | [44759](https://github.com/airbytehq/airbyte/pull/44759)                                                          | Improve null safety in parsing debezium change events.                                                                                          |
| 4.1.9   | 2024-08-27 | [44841](https://github.com/airbytehq/airbyte/pull/44841)                                                          | Adopt latest CDK.                                                                                                                               |
| 4.1.8   | 2024-08-08 | [43410](https://github.com/airbytehq/airbyte/pull/43410)                                                          | Adopt latest CDK.                                                                                                                               |
| 4.1.7   | 2024-08-06 | [42869](https://github.com/airbytehq/airbyte/pull/42869)                                                          | Adopt latest CDK.                                                                                                                               |
| 4.1.6   | 2024-07-30 | [42550](https://github.com/airbytehq/airbyte/pull/42550)                                                          | Correctly report stream states.                                                                                                                 |
| 4.1.5   | 2024-07-29 | [42852](https://github.com/airbytehq/airbyte/pull/42852)                                                          | Bump CDK version to latest to use new bug fixes on error translation.                                                                           |
| 4.1.4   | 2024-07-23 | [42421](https://github.com/airbytehq/airbyte/pull/42421)                                                          | Remove final transient error emitter iterators.                                                                                                 |
| 4.1.3   |            | 2024-07-22                                                                                                        | [42411](https://github.com/airbytehq/airbyte/pull/42411)                                                                                        | Hide the "initial load timeout in hours" field by default in UI |
| 4.1.2   | 2024-07-22 | [42024](https://github.com/airbytehq/airbyte/pull/42024)                                                          | Fix a NPE bug on resuming from a failed attempt.                                                                                                |
| 4.1.1   | 2024-07-19 | [42122](https://github.com/airbytehq/airbyte/pull/42122)                                                          | Improve wass error message + logging.                                                                                                           |
| 4.1.0   | 2024-07-17 | [42078](https://github.com/airbytehq/airbyte/pull/42078)                                                          | WASS analytics + bug fixes.                                                                                                                     |
| 4.0.36  | 2024-07-17 | [41648](https://github.com/airbytehq/airbyte/pull/41648)                                                          | Implement WASS.                                                                                                                                 |
| 4.0.35  | 2024-07-05 | [40570](https://github.com/airbytehq/airbyte/pull/40570)                                                          | Bump debezium-connector-sqlserver from 2.6.1.Final to 2.6.2.Final.                                                                              |
| 4.0.34  | 2024-07-01 | [40516](https://github.com/airbytehq/airbyte/pull/40516)                                                          | Remove dbz hearbeat.                                                                                                                            |
| 4.0.33  | 2024-06-30 | [40638](https://github.com/airbytehq/airbyte/pull/40638)                                                          | Fix a bug that could slow down an initial load of a large table using a different clustered index from the primary key.                         |
| 4.0.32  | 2024-06-26 | [40558](https://github.com/airbytehq/airbyte/pull/40558)                                                          | Handle DatetimeOffset correctly.                                                                                                                |
| 4.0.31  | 2024-06-14 | [39419](https://github.com/airbytehq/airbyte/pull/39419)                                                          | Handle DatetimeOffset correctly.                                                                                                                |
| 4.0.30  | 2024-06-14 | [39349](https://github.com/airbytehq/airbyte/pull/39349)                                                          | Full refresh stream sending internal count metadata.                                                                                            |
| 4.0.29  | 2024-06-14 | [39506](https://github.com/airbytehq/airbyte/pull/39506)                                                          | Adopt latest CDK.                                                                                                                               |
| 4.0.28  | 2024-06-08 | [39342](https://github.com/airbytehq/airbyte/pull/39342)                                                          | Fix custom conversion in CDC for datetimeoffset type.                                                                                           |
| 4.0.27  | 2024-05-29 | [38584](https://github.com/airbytehq/airbyte/pull/38584)                                                          | Set is_resumable flag in discover.                                                                                                              |
| 4.0.26  | 2024-05-16 | [38292](https://github.com/airbytehq/airbyte/pull/38292)                                                          | Improve cursor value query to return only one row                                                                                               |
| 4.0.25  | 2024-05-29 | [38775](https://github.com/airbytehq/airbyte/pull/38775)                                                          | Publish CDK                                                                                                                                     |
| 4.0.24  | 2024-05-23 | [38640](https://github.com/airbytehq/airbyte/pull/38640)                                                          | Sync sending trace status messages indicating progress.                                                                                         |
| 4.0.23  | 2024-05-15 | [38208](https://github.com/airbytehq/airbyte/pull/38208)                                                          | disable counts in full refresh stream in state message.                                                                                         |
| 4.0.22  | 2024-05-14 | [38196](https://github.com/airbytehq/airbyte/pull/38196)                                                          | Bump jdbc driver version to 12.6.1.jre11                                                                                                        |
| 4.0.21  | 2024-05-07 | [38054](https://github.com/airbytehq/airbyte/pull/38054)                                                          | Resumeable refresh should run only if there is source defined pk.                                                                               |
| 4.0.20  | 2024-05-07 | [38042](https://github.com/airbytehq/airbyte/pull/38042)                                                          | Bump debezium version to latest.                                                                                                                |
| 4.0.19  | 2024-05-07 | [38029](https://github.com/airbytehq/airbyte/pull/38029)                                                          | Fix previous release.                                                                                                                           |
| 4.0.18  | 2024-04-30 | [37451](https://github.com/airbytehq/airbyte/pull/37451)                                                          | Resumable full refresh read of tables.                                                                                                          |
| 4.0.17  | 2024-05-02 | [37781](https://github.com/airbytehq/airbyte/pull/37781)                                                          | Adopt latest CDK.                                                                                                                               |
| 4.0.16  | 2024-05-01 | [37742](https://github.com/airbytehq/airbyte/pull/37742)                                                          | Adopt latest CDK. Remove Debezium retries.                                                                                                      |
| 4.0.15  | 2024-04-22 | [37541](https://github.com/airbytehq/airbyte/pull/37541)                                                          | Adopt latest CDK. reduce excessive logs.                                                                                                        |
| 4.0.14  | 2024-04-22 | [37476](https://github.com/airbytehq/airbyte/pull/37476)                                                          | Adopt latest CDK.                                                                                                                               |
| 4.0.13  | 2024-04-16 | [37111](https://github.com/airbytehq/airbyte/pull/37111)                                                          | Populate null values in record message.                                                                                                         |
| 4.0.12  | 2024-04-15 | [37326](https://github.com/airbytehq/airbyte/pull/37326)                                                          | Allow up to 60 minutes of wait for the an initial CDC record.                                                                                   |
| 4.0.11  | 2024-04-15 | [37325](https://github.com/airbytehq/airbyte/pull/37325)                                                          | Populate airbyte_meta.changes + error handling.                                                                                                 |
| 4.0.10  | 2024-04-15 | [37110](https://github.com/airbytehq/airbyte/pull/37110)                                                          | Internal cleanup.                                                                                                                               |
| 4.0.9   | 2024-04-10 | [36919](https://github.com/airbytehq/airbyte/pull/36919)                                                          | Fix a bug in conversion of null values.                                                                                                         |
| 4.0.8   | 2024-04-05 | [36872](https://github.com/airbytehq/airbyte/pull/36872)                                                          | Update to connector's metadat definition.                                                                                                       |
| 4.0.7   | 2024-04-03 | [36772](https://github.com/airbytehq/airbyte/pull/36772)                                                          | Adopt latest CDK.                                                                                                                               |
| 4.0.6   | 2024-03-25 | [36333](https://github.com/airbytehq/airbyte/pull/36333)                                                          | Deprecate Dbz state iterator.                                                                                                                   |
| 4.0.5   | 2024-03-21 | [36364](https://github.com/airbytehq/airbyte/pull/36364)                                                          | Allow up to 40 minutes of wait for the an initial CDC record.                                                                                   |
| 4.0.4   | 2024-03-20 | [36325](https://github.com/airbytehq/airbyte/pull/36325)                                                          | [Refactor] : Remove mssql initial source operations .                                                                                           |
| 4.0.3   | 2024-03-19 | [36263](https://github.com/airbytehq/airbyte/pull/36263)                                                          | Fix a failure seen in CDC with tables containing default values.                                                                                |
| 4.0.2   | 2024-03-06 | [35792](https://github.com/airbytehq/airbyte/pull/35792)                                                          | Initial sync will now send record count in state message.                                                                                       |
| 4.0.1   | 2024-03-12 | [36011](https://github.com/airbytehq/airbyte/pull/36011)                                                          | Read correctly null values of columns with default value in CDC.                                                                                |
| 4.0.0   | 2024-03-06 | [35873](https://github.com/airbytehq/airbyte/pull/35873)                                                          | Terabyte-sized tables support, reliability improvements, bug fixes.                                                                             |
| 3.7.7   | 2024-03-06 | [35816](https://github.com/airbytehq/airbyte/pull/35816)                                                          | Fix query that was failing on a case sensitive server.                                                                                          |
| 3.7.6   | 2024-03-04 | [35721](https://github.com/airbytehq/airbyte/pull/35721)                                                          | Fix tests                                                                                                                                       |
| 3.7.5   | 2024-02-29 | [35739](https://github.com/airbytehq/airbyte/pull/35739)                                                          | Allow configuring the queue size used for cdc events.                                                                                           |
| 3.7.4   | 2024-02-26 | [35566](https://github.com/airbytehq/airbyte/pull/35566)                                                          | Add config to throw an error on invalid CDC position.                                                                                           |
| 3.7.3   | 2024-02-23 | [35596](https://github.com/airbytehq/airbyte/pull/35596)                                                          | Fix a logger issue                                                                                                                              |
| 3.7.2   | 2024-02-21 | [35368](https://github.com/airbytehq/airbyte/pull/35368)                                                          | Change query syntax to make it compatible with Azure SQL Managed Instance.                                                                      |
| 3.7.1   | 2024-02-20 | [35405](https://github.com/airbytehq/airbyte/pull/35405)                                                          | Change query syntax to make it compatible with Azure Synapse.                                                                                   |
| 3.7.0   | 2024-01-30 | [33311](https://github.com/airbytehq/airbyte/pull/33311)                                                          | Source mssql with checkpointing initial sync.                                                                                                   |
| 3.6.1   | 2024-01-26 | [34573](https://github.com/airbytehq/airbyte/pull/34573)                                                          | Adopt CDK v0.16.0.                                                                                                                              |
| 3.6.0   | 2024-01-10 | [33700](https://github.com/airbytehq/airbyte/pull/33700)                                                          | Remove CDC config options for data_to_sync and snapshot isolation.                                                                              |
| 3.5.1   | 2024-01-05 | [33510](https://github.com/airbytehq/airbyte/pull/33510)                                                          | Test-only changes.                                                                                                                              |
| 3.5.0   | 2023-12-19 | [33071](https://github.com/airbytehq/airbyte/pull/33071)                                                          | Fix SSL configuration parameters                                                                                                                |
| 3.4.1   | 2024-01-02 | [33755](https://github.com/airbytehq/airbyte/pull/33755)                                                          | Encode binary to base64 format                                                                                                                  |
| 3.4.0   | 2023-12-19 | [33481](https://github.com/airbytehq/airbyte/pull/33481)                                                          | Remove LEGACY state flag                                                                                                                        |
| 3.3.2   | 2023-12-14 | [33505](https://github.com/airbytehq/airbyte/pull/33505)                                                          | Using the released CDK.                                                                                                                         |
| 3.3.1   | 2023-12-12 | [33225](https://github.com/airbytehq/airbyte/pull/33225)                                                          | extracting MsSql specific files out of the CDK.                                                                                                 |
| 3.3.0   | 2023-12-12 | [33018](https://github.com/airbytehq/airbyte/pull/33018)                                                          | Migrate to Per-stream/Global states and away from Legacy states                                                                                 |
| 3.2.1   | 2023-12-11 | [33330](https://github.com/airbytehq/airbyte/pull/33330)                                                          | Parse DatetimeOffset fields with the correct format when used as cursor                                                                         |
| 3.2.0   | 2023-12-07 | [33225](https://github.com/airbytehq/airbyte/pull/33225)                                                          | CDC : Enable compression of schema history blob in state.                                                                                       |
| 3.1.0   | 2023-11-28 | [32882](https://github.com/airbytehq/airbyte/pull/32882)                                                          | Enforce SSL on Airbyte Cloud.                                                                                                                   |
| 3.0.2   | 2023-11-27 | [32573](https://github.com/airbytehq/airbyte/pull/32573)                                                          | Format Datetime and Datetime2 datatypes to 6-digit microsecond precision                                                                        |
| 3.0.1   | 2023-11-22 | [32656](https://github.com/airbytehq/airbyte/pull/32656)                                                          | Adopt java CDK version 0.5.0.                                                                                                                   |
| 3.0.0   | 2023-11-07 | [31531](https://github.com/airbytehq/airbyte/pull/31531)                                                          | Remapped date, smalldatetime, datetime2, time, and datetimeoffset datatype to their correct Airbyte types                                       |
| 2.0.4   | 2023-11-06 | [#32193](https://github.com/airbytehq/airbyte/pull/32193)                                                         | Adopt java CDK version 0.4.1.                                                                                                                   |
| 2.0.3   | 2023-10-31 | [32024](https://github.com/airbytehq/airbyte/pull/32024)                                                          | Upgrade to Debezium version 2.4.0.                                                                                                              |
| 2.0.2   | 2023-10-30 | [31960](https://github.com/airbytehq/airbyte/pull/31960)                                                          | Adopt java CDK version 0.2.0.                                                                                                                   |
| 2.0.1   | 2023-08-24 | [29821](https://github.com/airbytehq/airbyte/pull/29821)                                                          | Set replication_method display_type to radio, update titles and descriptions, and make CDC the default choice                                   |
| 2.0.0   | 2023-08-22 | [29493](https://github.com/airbytehq/airbyte/pull/29493)                                                          | Set a default cursor for Cdc mode                                                                                                               |
| 1.1.1   | 2023-07-24 | [28545](https://github.com/airbytehq/airbyte/pull/28545)                                                          | Support Read Committed snapshot isolation level                                                                                                 |
| 1.1.0   | 2023-06-26 | [27737](https://github.com/airbytehq/airbyte/pull/27737)                                                          | License Update: Elv2                                                                                                                            |
| 1.0.19  | 2023-06-20 | [27212](https://github.com/airbytehq/airbyte/pull/27212)                                                          | Fix silent exception swallowing in StreamingJdbcDatabase                                                                                        |
| 1.0.18  | 2023-06-14 | [27335](https://github.com/airbytehq/airbyte/pull/27335)                                                          | Remove noisy debug logs                                                                                                                         |
| 1.0.17  | 2023-05-25 | [26473](https://github.com/airbytehq/airbyte/pull/26473)                                                          | CDC : Limit queue size                                                                                                                          |
| 1.0.16  | 2023-05-01 | [25740](https://github.com/airbytehq/airbyte/pull/25740)                                                          | Disable index logging                                                                                                                           |
| 1.0.15  | 2023-04-26 | [25401](https://github.com/airbytehq/airbyte/pull/25401)                                                          | CDC : Upgrade Debezium to version 2.2.0                                                                                                         |
| 1.0.14  | 2023-04-19 | [25345](https://github.com/airbytehq/airbyte/pull/25345)                                                          | Logging : Log database indexes per stream                                                                                                       |
| 1.0.13  | 2023-04-19 | [24582](https://github.com/airbytehq/airbyte/pull/24582)                                                          | CDC : refactor for performance improvement                                                                                                      |
| 1.0.12  | 2023-04-17 | [25220](https://github.com/airbytehq/airbyte/pull/25220)                                                          | Logging changes : Log additional metadata & clean up noisy logs                                                                                 |
| 1.0.11  | 2023-04-11 | [24656](https://github.com/airbytehq/airbyte/pull/24656)                                                          | CDC minor refactor                                                                                                                              |
| 1.0.10  | 2023-04-06 | [24820](https://github.com/airbytehq/airbyte/pull/24820)                                                          | Fix data loss bug during an initial failed non-CDC incremental sync                                                                             |
| 1.0.9   | 2023-04-04 | [24833](https://github.com/airbytehq/airbyte/pull/24833)                                                          | Fix Debezium retry policy configuration                                                                                                         |
| 1.0.8   | 2023-03-28 | [24166](https://github.com/airbytehq/airbyte/pull/24166)                                                          | Fix InterruptedException bug during Debezium shutdown                                                                                           |
| 1.0.7   | 2023-03-27 | [24529](https://github.com/airbytehq/airbyte/pull/24373)                                                          | Preparing the connector for CDC checkpointing                                                                                                   |
| 1.0.6   | 2023-03-22 | [20760](https://github.com/airbytehq/airbyte/pull/20760)                                                          | Removed redundant date-time datatypes formatting                                                                                                |
| 1.0.5   | 2023-03-21 | [24207](https://github.com/airbytehq/airbyte/pull/24207)                                                          | Fix incorrect schema change warning in CDC mode                                                                                                 |
| 1.0.4   | 2023-03-21 | [24147](https://github.com/airbytehq/airbyte/pull/24275)                                                          | Fix error with CDC checkpointing                                                                                                                |
| 1.0.3   | 2023-03-15 | [24082](https://github.com/airbytehq/airbyte/pull/24082)                                                          | Fixed NPE during cursor values validation                                                                                                       |
| 1.0.2   | 2023-03-14 | [23908](https://github.com/airbytehq/airbyte/pull/23908)                                                          | Log warning on null cursor values                                                                                                               |
| 1.0.1   | 2023-03-10 | [23939](https://github.com/airbytehq/airbyte/pull/23939)                                                          | For network isolation, source connector accepts a list of hosts it is allowed to connect                                                        |
| 1.0.0   | 2023-03-06 | [23112](https://github.com/airbytehq/airbyte/pull/23112)                                                          | Upgrade Debezium version to 2.1.2                                                                                                               |
| 0.4.29  | 2023-02-24 | [16798](https://github.com/airbytehq/airbyte/pull/16798)                                                          | Add event_serial_no to cdc metadata                                                                                                             |
| 0.4.28  | 2023-01-18 | [21348](https://github.com/airbytehq/airbyte/pull/21348)                                                          | Fix error introduced in [18959](https://github.com/airbytehq/airbyte/pull/18959) in which option `initial_waiting_seconds` was removed          |
| 0.4.27  | 2022-12-14 | [20436](https://github.com/airbytehq/airbyte/pull/20346)                                                          | Consolidate date/time values mapping for JDBC sources                                                                                           |
| 0.4.26  | 2022-12-12 | [18959](https://github.com/airbytehq/airbyte/pull/18959)                                                          | CDC : Don't timeout if snapshot is not complete.                                                                                                |
| 0.4.25  | 2022-11-04 | [18732](https://github.com/airbytehq/airbyte/pull/18732)                                                          | Upgrade debezium version to 1.9.6                                                                                                               |
| 0.4.24  | 2022-10-25 | [18383](https://github.com/airbytehq/airbyte/pull/18383)                                                          | Better SSH error handling + messages                                                                                                            |
| 0.4.23  | 2022-10-21 | [18263](https://github.com/airbytehq/airbyte/pull/18263)                                                          | Fixes bug introduced in [15833](https://github.com/airbytehq/airbyte/pull/15833) and adds better error messaging for SSH tunnel in Destinations |
| 0.4.22  | 2022-10-19 | [18087](https://github.com/airbytehq/airbyte/pull/18087)                                                          | Better error messaging for configuration errors (SSH configs, choosing an invalid cursor)                                                       |
| 0.4.21  | 2022-10-17 | [18041](https://github.com/airbytehq/airbyte/pull/18041)                                                          | Fixes bug introduced 2022-09-12 with SshTunnel, handles iterator exception properly                                                             |
|         | 2022-10-13 | [15535](https://github.com/airbytehq/airbyte/pull/16238)                                                          | Update incremental query to avoid data missing when new data is inserted at the same time as a sync starts under non-CDC incremental mode       |
| 0.4.20  | 2022-09-14 | [15668](https://github.com/airbytehq/airbyte/pull/15668)                                                          | Wrap logs in AirbyteLogMessage                                                                                                                  |
| 0.4.19  | 2022-09-05 | [16002](https://github.com/airbytehq/airbyte/pull/16002)                                                          | Added ability to specify schemas for discovery during setting connector up                                                                      |
| 0.4.18  | 2022-09-03 | [14910](https://github.com/airbytehq/airbyte/pull/14910)                                                          | Standardize spec for CDC replication. Replace the `replication_method` enum with a config object with a `method` enum field.                    |
| 0.4.17  | 2022-09-01 | [16261](https://github.com/airbytehq/airbyte/pull/16261)                                                          | Emit state messages more frequently                                                                                                             |
| 0.4.16  | 2022-08-18 | [14356](https://github.com/airbytehq/airbyte/pull/14356)                                                          | DB Sources: only show a table can sync incrementally if at least one column can be used as a cursor field                                       |
| 0.4.15  | 2022-08-11 | [15538](https://github.com/airbytehq/airbyte/pull/15538)                                                          | Allow additional properties in db stream state                                                                                                  |
| 0.4.14  | 2022-08-10 | [15430](https://github.com/airbytehq/airbyte/pull/15430)                                                          | fixed a bug on handling special character on database name                                                                                      |
| 0.4.13  | 2022-08-04 | [15268](https://github.com/airbytehq/airbyte/pull/15268)                                                          | Added [] enclosing to escape special character in the database name                                                                             |
| 0.4.12  | 2022-08-02 | [14801](https://github.com/airbytehq/airbyte/pull/14801)                                                          | Fix multiple log bindings                                                                                                                       |
| 0.4.11  | 2022-07-22 | [14714](https://github.com/airbytehq/airbyte/pull/14714)                                                          | Clarified error message when invalid cursor column selected                                                                                     |
| 0.4.10  | 2022-07-14 | [14574](https://github.com/airbytehq/airbyte/pull/14574)                                                          | Removed additionalProperties:false from JDBC source connectors                                                                                  |
| 0.4.9   | 2022-07-05 | [14379](https://github.com/airbytehq/airbyte/pull/14379)                                                          | Aligned Normal and CDC migration + added some fixes for datatypes processing                                                                    |
| 0.4.8   | 2022-06-24 | [14121](https://github.com/airbytehq/airbyte/pull/14121)                                                          | Omit using 'USE' keyword on Azure SQL with CDC                                                                                                  |
| 0.4.5   | 2022-06-23 | [14077](https://github.com/airbytehq/airbyte/pull/14077)                                                          | Use the new state management                                                                                                                    |
| 0.4.3   | 2022-06-17 | [13887](https://github.com/airbytehq/airbyte/pull/13887)                                                          | Increase version to include changes from [13854](https://github.com/airbytehq/airbyte/pull/13854)                                               |
| 0.4.2   | 2022-06-06 | [13435](https://github.com/airbytehq/airbyte/pull/13435)                                                          | Adjust JDBC fetch size based on max memory and max row size                                                                                     |
| 0.4.1   | 2022-05-25 | [13419](https://github.com/airbytehq/airbyte/pull/13419)                                                          | Correct enum for Standard method.                                                                                                               |
| 0.4.0   | 2022-05-25 | [12759](https://github.com/airbytehq/airbyte/pull/12759) [13168](https://github.com/airbytehq/airbyte/pull/13168) | For CDC, Add option to ignore existing data and only sync new changes from the database.                                                        |
| 0.3.22  | 2022-04-29 | [12480](https://github.com/airbytehq/airbyte/pull/12480)                                                          | Query tables with adaptive fetch size to optimize JDBC memory consumption                                                                       |
| 0.3.21  | 2022-04-11 | [11729](https://github.com/airbytehq/airbyte/pull/11729)                                                          | Bump mina-sshd from 2.7.0 to 2.8.0                                                                                                              |
| 0.3.19  | 2022-03-31 | [11495](https://github.com/airbytehq/airbyte/pull/11495)                                                          | Adds Support to Chinese MSSQL Server Agent                                                                                                      |
| 0.3.18  | 2022-03-29 | [11010](https://github.com/airbytehq/airbyte/pull/11010)                                                          | Adds JDBC Params                                                                                                                                |
| 0.3.17  | 2022-02-21 | [10242](https://github.com/airbytehq/airbyte/pull/10242)                                                          | Fixed cursor for old connectors that use non-microsecond format. Now connectors work with both formats                                          |
| 0.3.16  | 2022-02-18 | [10242](https://github.com/airbytehq/airbyte/pull/10242)                                                          | Updated timestamp transformation with microseconds                                                                                              |
| 0.3.15  | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256)                                                          | Add `-XX:+ExitOnOutOfMemoryError` JVM option                                                                                                    |
| 0.3.14  | 2022-01-24 | [9554](https://github.com/airbytehq/airbyte/pull/9554)                                                            | Allow handling of java sql date in CDC                                                                                                          |
| 0.3.13  | 2022-01-07 | [9094](https://github.com/airbytehq/airbyte/pull/9094)                                                            | Added support for missed data types                                                                                                             |
| 0.3.12  | 2021-12-30 | [9206](https://github.com/airbytehq/airbyte/pull/9206)                                                            | Update connector fields title/description                                                                                                       |
| 0.3.11  | 2021-12-24 | [8958](https://github.com/airbytehq/airbyte/pull/8958)                                                            | Add support for JdbcType.ARRAY                                                                                                                  |
| 0.3.10  | 2021-12-01 | [8371](https://github.com/airbytehq/airbyte/pull/8371)                                                            | Fixed incorrect handling "\n" in ssh key                                                                                                        |
| 0.3.9   | 2021-11-09 | [7748](https://github.com/airbytehq/airbyte/pull/7748)                                                            | Improve support for binary and varbinary data types                                                                                             |
| 0.3.8   | 2021-10-26 | [7386](https://github.com/airbytehq/airbyte/pull/7386)                                                            | Fixed data type (smalldatetime, smallmoney) conversion from mssql source                                                                        |
| 0.3.7   | 2021-09-30 | [6585](https://github.com/airbytehq/airbyte/pull/6585)                                                            | Improved SSH Tunnel key generation steps                                                                                                        |
| 0.3.6   | 2021-09-17 | [6318](https://github.com/airbytehq/airbyte/pull/6318)                                                            | Added option to connect to DB via SSH                                                                                                           |
| 0.3.4   | 2021-08-13 | [4699](https://github.com/airbytehq/airbyte/pull/4699)                                                            | Added json config validator                                                                                                                     |
| 0.3.3   | 2021-07-05 | [4689](https://github.com/airbytehq/airbyte/pull/4689)                                                            | Add CDC support                                                                                                                                 |
| 0.3.2   | 2021-06-09 | [3179](https://github.com/airbytehq/airbyte/pull/3973)                                                            | Add AIRBYTE_ENTRYPOINT for Kubernetes support                                                                                                   |
| 0.3.1   | 2021-06-08 | [3893](https://github.com/airbytehq/airbyte/pull/3893)                                                            | Enable SSL connection                                                                                                                           |
| 0.3.0   | 2021-04-21 | [2990](https://github.com/airbytehq/airbyte/pull/2990)                                                            | Support namespaces                                                                                                                              |
| 0.2.3   | 2021-03-28 | [2600](https://github.com/airbytehq/airbyte/pull/2600)                                                            | Add NCHAR and NVCHAR support to DB and cursor type casting                                                                                      |
| 0.2.2   | 2021-03-26 | [2460](https://github.com/airbytehq/airbyte/pull/2460)                                                            | Destination supports destination sync mode                                                                                                      |
| 0.2.1   | 2021-03-18 | [2488](https://github.com/airbytehq/airbyte/pull/2488)                                                            | Sources support primary keys                                                                                                                    |
| 0.2.0   | 2021-03-09 | [2238](https://github.com/airbytehq/airbyte/pull/2238)                                                            | Protocol allows future/unknown properties                                                                                                       |
| 0.1.11  | 2021-02-02 | [1887](https://github.com/airbytehq/airbyte/pull/1887)                                                            | Migrate AbstractJdbcSource to use iterators                                                                                                     |
| 0.1.10  | 2021-01-25 | [1746](https://github.com/airbytehq/airbyte/pull/1746)                                                            | Fix NPE in State Decorator                                                                                                                      |
| 0.1.9   | 2021-01-19 | [1724](https://github.com/airbytehq/airbyte/pull/1724)                                                            | Fix JdbcSource handling of tables with same names in different schemas                                                                          |
| 0.1.9   | 2021-01-14 | [1655](https://github.com/airbytehq/airbyte/pull/1655)                                                            | Fix JdbcSource OOM                                                                                                                              |
| 0.1.8   | 2021-01-13 | [1588](https://github.com/airbytehq/airbyte/pull/1588)                                                            | Handle invalid numeric values in JDBC source                                                                                                    |
| 0.1.6   | 2020-12-09 | [1172](https://github.com/airbytehq/airbyte/pull/1172)                                                            | Support incremental sync                                                                                                                        |
| 0.1.5   | 2020-11-30 | [1038](https://github.com/airbytehq/airbyte/pull/1038)                                                            | Change JDBC sources to discover more than standard schemas                                                                                      |
| 0.1.4   | 2020-11-30 | [1046](https://github.com/airbytehq/airbyte/pull/1046)                                                            | Add connectors using an index YAML file                                                                                                         |

</details>
