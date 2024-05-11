# Db2

## Overview

The IBM Db2 source allows you to sync data from Db2. It supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This IBM Db2 source connector is built on top of the [IBM Data Server Driver](https://mvnrepository.com/artifact/com.ibm.db2/jcc/11.5.5.0) for JDBC and SQLJ. It is a pure-Java driver \(Type 4\) that supports the JDBC 4 specification as described in IBM Db2 [documentation](https://www.ibm.com/docs/en/db2/11.5?topic=apis-supported-drivers-jdbc-sqlj).

#### Resulting schema

The IBM Db2 source does not alter the schema present in your warehouse. Depending on the destination connected to this source, however, the result schema may be altered. See the destination's documentation for more details.

#### Features

| Feature                   | Supported?\(Yes/No\) | Notes |
| :------------------------ | :------------------- | :---- |
| Full Refresh Sync         | Yes                  |       |
| Incremental - Append Sync | Yes                  |       |
| Namespaces                | Yes                  |       |

## Getting started

### Requirements

1. You'll need the following information to configure the IBM Db2 source:
2. **Host**
3. **Port**
4. **Database**
5. **Username**
6. **Password**
7. Create a dedicated read-only Airbyte user and role with access to all schemas needed for replication.

### Setup guide

#### 1. Specify port, host and name of the database.

#### 2. Create a dedicated read-only user with access to the relevant schemas \(Recommended but optional\)

This step is optional but highly recommended allowing for better permission control and auditing. Alternatively, you can use Airbyte with an existing user in your database.

Please create a dedicated database user and run the following commands against your database:

```sql
-- create Airbyte role
CREATE ROLE 'AIRBYTE_ROLE';

-- grant Airbyte database access
GRANT CONNECT ON 'DATABASE' TO ROLE 'AIRBYTE_ROLE'
GRANT ROLE 'AIRBYTE_ROLE' TO USER 'AIRBYTE_USER'
```

Your database user should now be ready for use with Airbyte.

#### 3. Create SSL connection.

To set up an SSL connection, you need to use a client certificate. Add it to the "SSL PEM file" field and the connector will automatically add it to the secret keystore.
You can also enter your own password for the keystore, but if you don't, the password will be generated automatically.

## Changelog

| Version | Date       | Pull Request                                                                                                  | Subject                                                                                                                                   |
| :------ | :--------- | :------------------------------------------------------------------------------------------------------------ | :---------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| 0.2.2   | 2024-02-13 | [35233](https://github.com/airbytehq/airbyte/pull/35233)                                                      | Adopt CDK 0.20.4                                                                                                                          |
| 0.2.1   | 2024-01-24 | [34453](https://github.com/airbytehq/airbyte/pull/34453)                                                      | bump CDK version                                                                                                                          |
| 0.2.0   | 2023-12-18 | [33485](https://github.com/airbytehq/airbyte/pull/33485)                                                      | Remove LEGACY state                                                                                                                       |
| 0.1.20  | 2023-06-20 | [27212](https://github.com/airbytehq/airbyte/pull/27212)                                                      | Fix silent exception swallowing in StreamingJdbcDatabase                                                                                  |
| 0.1.19  | 2023-03-22 | [20760](https://github.com/airbytehq/airbyte/pull/20760)                                                      | Removed redundant date-time datatypes formatting                                                                                          |
| 0.1.18  | 2023-03-06 | [23455](https://github.com/airbytehq/airbyte/pull/23455)                                                      | For network isolation, source connector accepts a list of hosts it is allowed to connect to                                               |
| 0.1.17  | 2022-12-14 | [20436](https://github.com/airbytehq/airbyte/pull/20346)                                                      | Consolidate date/time values mapping for JDBC sources                                                                                     |
|         | 2022-10-13 | [15535](https://github.com/airbytehq/airbyte/pull/16238)                                                      | Update incremental query to avoid data missing when new data is inserted at the same time as a sync starts under non-CDC incremental mode |
| 0.1.16  | 2022-09-06 | [16354](https://github.com/airbytehq/airbyte/pull/16354)                                                      | Add custom JDBC params                                                                                                                    |
| 0.1.15  | 2022-09-01 | [16238](https://github.com/airbytehq/airbyte/pull/16238)                                                      | Emit state messages more frequently                                                                                                       |
| 0.1.14  | 2022-08-18 | [14356](https://github.com/airbytehq/airbyte/pull/14356)                                                      | DB Sources: only show a table can sync incrementally if at least one column can be used as a cursor field                                 |
| 0.1.13  | 2022-07-22 | [14714](https://github.com/airbytehq/airbyte/pull/14714)                                                      | Clarified error message when invalid cursor column selected                                                                               |
| 0.1.12  | 2022-07-14 | [14574](https://github.com/airbytehq/airbyte/pull/14574)                                                      | Removed additionalProperties:false from JDBC source connectors                                                                            |
| 0.1.11  | 2022-06-17 | [13864](https://github.com/airbytehq/airbyte/pull/13864)                                                      | Updated stacktrace format for any trace message errors                                                                                    |
| 0.1.10  | 2022-04-29 | [12480](https://github.com/airbytehq/airbyte/pull/12480)                                                      | Query tables with adaptive fetch size to optimize JDBC memory consumption                                                                 |
| 0.1.9   | 2022-02-21 | [10242](https://github.com/airbytehq/airbyte/pull/10242)                                                      | Fixed cursor for old connectors that use non-microsecond format. Now connectors work with both formats                                    |
| 0.1.8   | 2022-02-18 | [10242](https://github.com/airbytehq/airbyte/pull/10242)                                                      | Updated timestamp transformation with microseconds                                                                                        |
| 0.1.7   | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256)                                                      | Add `-XX:+ExitOnOutOfMemoryError` JVM option                                                                                              | \*\*\*\* |
| 0.1.6   | 2022-02-08 | [10173](https://github.com/airbytehq/airbyte/pull/10173)                                                      | Improved discovering tables in case if user does not have permissions to any table                                                        |
| 0.1.5   | 2022-02-01 | [9875](https://github.com/airbytehq/airbyte/pull/9875)                                                        | Discover only permitted for user tables                                                                                                   |
| 0.1.4   | 2021-12-30 | [9187](https://github.com/airbytehq/airbyte/pull/9187) [8749](https://github.com/airbytehq/airbyte/pull/8749) | Add support of JdbcType.ARRAY to JdbcSourceOperations.                                                                                    |
| 0.1.3   | 2021-11-05 | [7670](https://github.com/airbytehq/airbyte/pull/7670)                                                        | Updated unique DB2 types transformation                                                                                                   |
| 0.1.2   | 2021-10-25 | [7355](https://github.com/airbytehq/airbyte/pull/7355)                                                        | Added ssl support                                                                                                                         |
| 0.1.1   | 2021-08-13 | [4699](https://github.com/airbytehq/airbyte/pull/4699)                                                        | Added json config validator                                                                                                               |
| 0.1.0   | 2021-06-22 | [4197](https://github.com/airbytehq/airbyte/pull/4197)                                                        | New Source: IBM DB2                                                                                                                       |
