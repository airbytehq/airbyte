# Microsoft SQL Server \(MSSQL\)

## Overview

The MSSQL source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Resulting schema

The MSSQL source does not alter the schema present in your database. Depending on the destination connected to this source, however, the schema may be altered. See the destination's documentation for more details.

### Data type mapping

MSSQL data types are mapped to the following data types when synchronizing data:

| MSSQL Type | Resulting Type | Notes |
| :--- | :--- | :--- |
| `bigint` | number |  |
| `numeric` | number |  |
| `bit` | boolean |  |
| `smallint` | number |  |
| `decimal` | number |  |
| `int` | number |  |
| `tinyint` | number |  |
| `float` | number |  |
| everything else | string |  |

If you do not see a type in this list, assume that it is coerced into a string. We are happy to take feedback on preferred mappings.

### Features

| Feature | Supported | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync - Append | Yes |  |
| Replicate Incremental Deletes | Coming soon |  |
| Logical Replication \(WAL\) | Coming soon |  |
| SSL Support | Yes |  |
| SSH Tunnel Connection | Coming soon |  |
| Namespaces | Yes | Enabled by default |

## Getting started

### Requirements

1. MSSQL Server `Azure SQL Database`, `Azure Synapse Analytics`, `Azure SQL Managed Instance`, `SQL Server 2019`, `SQL Server 2017`, `SQL Server 2016`, `SQL Server 2014`, `SQL Server 2012`, `PDW 2008R2 AU34`.
2. Create a dedicated read-only Airbyte user with access to all tables needed for replication

### Setup guide

#### 1. Make sure your database is accessible from the machine running Airbyte

This is dependent on your networking setup. The easiest way to verify if Airbyte is able to connect to your MSSQL instance is via the check connection tool in the UI.

#### 2. Create a dedicated read-only user with access to the relevant tables \(Recommended but optional\)

This step is optional but highly recommended to allow for better permission control and auditing. Alternatively, you can use Airbyte with an existing user in your database.

_Coming soon: suggestions on how to create this user._

Your database user should now be ready for use with Airbyte.

## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
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
