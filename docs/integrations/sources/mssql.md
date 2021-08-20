# Microsoft SQL Server \(MSSQL\)

## Overview

The MSSQL source supports Full Refresh and Incremental syncs, including Change Data Capture. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Resulting schema

The MSSQL source does not alter the schema present in your database. Depending on the destination connected to this source, however, the schema may be altered. See the destination's documentation for more details.

### Data type mapping

MSSQL data types are mapped to the following data types when synchronizing data.
You can check the test values examples [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-mssql/src/test-integration/java/io/airbyte/integrations/source/mssql/MssqlSourceComprehensiveTest.java).
If you can't find the data type you are looking for or have any problems feel free to add a new test!

| MSSQL Type | Resulting Type | Notes |
| :--- | :--- | :--- |
| `bigint` | number |  |
| `binary` | string |  |
| `bit` | boolean |  |
| `char` | string |  |
| `date` | number |  |
| `datetime` | string |  |
| `datetime2` | string |  |
| `datetimeoffset` | string |  |
| `decimal` | number |  |
| `int` | number |  |
| `float` | number |  |
| `geography` | string |  |
| `geometry` | string |  |
| `money` | number |  |
| `numeric` | number |  |
| `ntext` | string |  |
| `nvarchar` | string |  |
| `nvarchar(max)` | string |  |
| `real` | number |  |
| `smalldatetime` | string |  |
| `smallint` | number |  |
| `smallmoney` | number |  |
| `sql_variant` | string |  |
| `uniqueidentifier` | string |  |
| `text` | string |  |
| `time` | string |  |
| `tinyint` | number |  |
| `varbinary` | string |  |
| `varchar` | string |  |
| `varchar(max) COLLATE Latin1_General_100_CI_AI_SC_UTF8` | string |  |
| `xml` | string |  |

If you do not see a type in this list, assume that it is coerced into a string. We are happy to take feedback on preferred mappings.

Please see [this issue](https://github.com/airbytehq/airbyte/issues/4270) for description of unexpected behaviour for certain datatypes.

### Features

| Feature | Supported | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync - Append | Yes |  |
| Replicate Incremental Deletes | Yes |  |
| CDC (Change Data Capture) | Yes |  |
| SSL Support | Yes |  |
| SSH Tunnel Connection | Coming soon |  |
| Namespaces | Yes | Enabled by default |

## Getting started

### Requirements

1. MSSQL Server `Azure SQL Database`, `Azure Synapse Analytics`, `Azure SQL Managed Instance`, `SQL Server 2019`, `SQL Server 2017`, `SQL Server 2016`, `SQL Server 2014`, `SQL Server 2012`, `PDW 2008R2 AU34`.
2. Create a dedicated read-only Airbyte user with access to all tables needed for replication
3. If you want to use CDC, please see [the relevant section below](mssql.md#change-data-capture-cdc) for further setup requirements

### Setup guide

#### 1. Make sure your database is accessible from the machine running Airbyte

This is dependent on your networking setup. The easiest way to verify if Airbyte is able to connect to your MSSQL instance is via the check connection tool in the UI.

#### 2. Create a dedicated read-only user with access to the relevant tables \(Recommended but optional\)

This step is optional but highly recommended to allow for better permission control and auditing. Alternatively, you can use Airbyte with an existing user in your database.

_Coming soon: suggestions on how to create this user._

Your database user should now be ready for use with Airbyte.

## Change Data Capture : CDC

We use [SQL Server's change data capture feature](https://docs.microsoft.com/en-us/sql/relational-databases/track-changes/about-change-data-capture-sql-server?view=sql-server-2017)
to capture row-level `INSERT`, `UPDATE` and `DELETE` operations that occur on cdc-enabled tables.

Some extra setup requiring at least *db_owner* permissions on the database(s) you intend to sync from will be required (detailed [below](mssql.md#setting-up-cdc-for-mssql)).

Please read the [CDC docs](../../understanding-airbyte/cdc.md) for an overview of how Airbyte approaches CDC.

### Should I use CDC for MSSQL?

* If you need a record of deletions and can accept the limitations posted below, CDC is the way to go!
* If your data set is small and/or you just want a snapshot of your table in the destination, consider using Full Refresh replication for your table instead of CDC.
* If the limitations below prevent you from using CDC and your goal is to maintain a snapshot of your table in the destination, consider using non-CDC incremental and occasionally reset the data and re-sync.
* If your table has a primary key but doesn't have a reasonable cursor field for incremental syncing \(i.e. `updated_at`\), CDC allows you to sync your table incrementally.

### CDC Limitations

* Make sure to read our [CDC docs](../../understanding-airbyte/cdc.md) to see limitations that impact all databases using CDC replication.
* There are some critical issues regarding certain datatypes. Please find detailed info in [this Github issue](https://github.com/airbytehq/airbyte/issues/4542).
* CDC is only available for SQL Server 2016 Service Pack 1 (SP1) and later.
* *db_owner* (or higher) permissions are required to perform the [neccessary setup](mssql.md#setting-up-cdc-for-mssql) for CDC.
* You must enable [snapshot isolation mode](https://docs.microsoft.com/en-us/dotnet/framework/data/adonet/sql/snapshot-isolation-in-sql-server) on the database(s) you want to sync. This is used for retrieving an initial snapshot without locking tables.
* On Linux, CDC is not supported on versions earlier than SQL Server 2017 CU18 (SQL Server 2019 is supported).
* Change data capture cannot be enabled on tables with a clustered columnstore index. (It can be enabled on tables with a *non-clustered* columnstore index).
* The SQL Server CDC feature processes changes that occur in user-created tables only. You cannot enable CDC on the SQL Server master database.
* Using variables with partition switching on databases or tables with change data capture (CDC) is not supported for the `ALTER TABLE` ... `SWITCH TO` ... `PARTITION` ... statement
* Our implementation has not been tested with managed instances, such as Azure SQL Database (we welcome any feedback from users who try this!)
  * If you do want to try this, CDC can only be enabled on Azure SQL databases tiers above Standard 3 (S3+). Basic, S0, S1 and S2 tiers are not supported for CDC.
* Our CDC implementation uses at least once delivery for all change records.
* Read more on CDC limitations in the [Microsoft docs](https://docs.microsoft.com/en-us/sql/relational-databases/track-changes/about-change-data-capture-sql-server?view=sql-server-2017#limitations).

### Setting up CDC for MSSQL

#### Enable CDC on database and tables

MS SQL Server provides some built-in stored procedures to enable CDC.

- To enable CDC, a SQL Server administrator with the necessary privileges (*db_owner* or *sysadmin*) must first run a query to enable CDC at the database level.
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
  @filegroup_name = N'{fiilegroup name}', [2]
  @supports_net_changes = 0 [3]
  GO
```
  - [1] Specifies a role which will gain `SELECT` permission on the captured columns of the source table. We suggest putting a value here so you can use this role in the next step but you can also set the value of @role_name to `NULL` to allow only *sysadmin* and *db_owner* to have access. Be sure that the credentials used to connect to the source in Airbyte align with this role so that Airbyte can access the cdc tables.
  - [2] Specifies the filegroup where SQL Server places the change table. We recommend creating a separate filegroup for CDC but you can leave this parameter out to use the default filegroup.
  - [3] If 0, only the support functions to query for all changes are generated. If 1, the functions that are needed to query for net changes are also generated. If supports_net_changes is set to 1, index_name must be specified, or the source table must have a defined primary key.

- (For more details on parameters, see the [Microsoft doc page](https://docs.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sys-sp-cdc-enable-table-transact-sql?view=sql-server-ver15) for this stored procedure).


- If you have many tables to enable CDC on and would like to avoid having to run this query one-by-one for every table, [this script](http://www.techbrothersit.com/2013/06/change-data-capture-cdc-sql-server_69.html) might help!

For further detail, see the [Microsoft docs on enabling and disabling CDC](https://docs.microsoft.com/en-us/sql/relational-databases/track-changes/enable-and-disable-change-data-capture-sql-server?view=sql-server-ver15).

#### Enabling snapshot isolation

- When a sync runs for the first time using CDC, Airbyte performs an initial consistent snapshot of your database. To avoid acquiring table locks, Airbyte uses *snapshot isolation*, allowing simultaneous writes by other database clients. This must be enabled on the database like so:
```text
  ALTER DATABASE {database name}
    SET ALLOW_SNAPSHOT_ISOLATION ON;
```

#### Create a user and grant appropriate permissions
- Rather than use *sysadmin* or *db_owner* credentials, we recommend creating a new user with the relevant CDC access for use with Airbyte. First let's create the login and user and add to the [db_datareader](https://docs.microsoft.com/en-us/sql/relational-databases/security/authentication-access/database-level-roles?view=sql-server-ver15) role:
```text
  USE {database name};
  CREATE LOGIN {user name}   
    WITH PASSWORD = '{password}';
  CREATE USER {user name} FOR LOGIN {user name};
  EXEC sp_addrolemember 'db_datareader', '{user name}';
```
  - Add the user to the role specified earlier when enabling cdc on the table(s):
```text
  EXEC sp_addrolemember '{role name}', '{user name}';
```
  - This should be enough access, but if you run into problems, try also directly granting the user `SELECT` access on the cdc schema:
```text
  USE {database name};
  GRANT SELECT ON SCHEMA :: [cdc] TO {user name};
```
  - If feasible, granting this user 'VIEW SERVER STATE' permissions will allow Airbyte to check whether or not the [SQL Server Agent](https://docs.microsoft.com/en-us/sql/relational-databases/track-changes/about-change-data-capture-sql-server?view=sql-server-ver15#relationship-with-log-reader-agent) is running. This is preferred as it ensures syncs will fail if the CDC tables are not being updated by the Agent in the source database.
```text
  USE master;
  GRANT VIEW SERVER STATE TO {user name};
```

#### Extending the retention period of CDC data

- In SQL Server, by default, only three days of data are retained in the change tables. Unless you are running very frequent syncs, we suggest increasing this retention so that in case of a failure in sync or if the sync is paused, there is still some bandwidth to start from the last point in incremental sync.
- These settings can be changed using the stored procedure [sys.sp_cdc_change_job](https://docs.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sys-sp-cdc-change-job-transact-sql?view=sql-server-ver15) as below:
```text
  -- we recommend 14400 minutes (10 days) as retention period
  EXEC sp_cdc_change_job @job_type='cleanup', @retention = {minutes}
```
- After making this change, a restart of the cleanup job is required:
```text
  EXEC sys.sp_cdc_stop_job @job_type = 'cleanup';
  
  EXEC sys.sp_cdc_start_job @job_type = 'cleanup';
```

#### Ensuring the SQL Server Agent is running

- MSSQL uses the SQL Server Agent to [run the jobs necessary](https://docs.microsoft.com/en-us/sql/relational-databases/track-changes/about-change-data-capture-sql-server?view=sql-server-ver15#agent-jobs) for CDC. It is therefore vital that the Agent is operational in order for to CDC to work effectively. You can check the status of the SQL Server Agent as follows:
```text
  EXEC xp_servicecontrol 'QueryState', N'SQLServerAGENT';
```
- If you see something other than 'Running.' please follow the [Microsoft docs](https://docs.microsoft.com/en-us/sql/ssms/agent/start-stop-or-pause-the-sql-server-agent-service?view=sql-server-ver15) to start the service.

#### Setting up CDC on managed versions of SQL Server

We readily welcome [contributions to our docs](https://github.com/airbytehq/airbyte/tree/master/docs) providing setup instructions. Please consider contributing to expand our docs!


## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.3.4   | 2021-08-13 | [4699](https://github.com/airbytehq/airbyte/pull/4699) | Added json config validator | 
| 0.3.3   | 2021-07-05 | [4689](https://github.com/airbytehq/airbyte/pull/4689) | Add CDC support |
| 0.3.2   | 2021-06-09 | [3179](https://github.com/airbytehq/airbyte/pull/3973) | Add AIRBYTE_ENTRYPOINT for Kubernetes support |
| 0.3.1   | 2021-06-08 | [3893](https://github.com/airbytehq/airbyte/pull/3893) | Enable SSL connection |
| 0.3.0   | 2021-04-21 | [2990](https://github.com/airbytehq/airbyte/pull/2990) | Support namespaces |
| 0.2.3   | 2021-03-28 | [2600](https://github.com/airbytehq/airbyte/pull/2600) | Add NCHAR and NVCHAR support to DB and cursor type casting |
| 0.2.2   | 2021-03-26 | [2460](https://github.com/airbytehq/airbyte/pull/2460) | Destination supports destination sync mode |
| 0.2.1   | 2021-03-18 | [2488](https://github.com/airbytehq/airbyte/pull/2488) | Sources support primary keys |
| 0.2.0   | 2021-03-09 | [2238](https://github.com/airbytehq/airbyte/pull/2238) | Protocol allows future/unknown properties |
| 0.1.11  | 2021-02-02 | [1887](https://github.com/airbytehq/airbyte/pull/1887) | Migrate AbstractJdbcSource to use iterators |]
| 0.1.10  | 2021-01-25 | [1746](https://github.com/airbytehq/airbyte/pull/1746) | Fix NPE in State Decorator |
| 0.1.9   | 2021-01-19 | [1724](https://github.com/airbytehq/airbyte/pull/1724) | Fix JdbcSource handling of tables with same names in different schemas |
| 0.1.9   | 2021-01-14 | [1655](https://github.com/airbytehq/airbyte/pull/1655) | Fix JdbcSource OOM |
| 0.1.8   | 2021-01-13 | [1588](https://github.com/airbytehq/airbyte/pull/1588) | Handle invalid numeric values in JDBC source |
| 0.1.6   | 2020-12-09 | [1172](https://github.com/airbytehq/airbyte/pull/1172) | Support incremental sync |
| 0.1.5   | 2020-11-30 | [1038](https://github.com/airbytehq/airbyte/pull/1038) | Change JDBC sources to discover more than standard schemas |
| 0.1.4   | 2020-11-30 | [1046](https://github.com/airbytehq/airbyte/pull/1046) | Add connectors using an index YAML file |
