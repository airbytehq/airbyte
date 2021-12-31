# Db2

## Overview

The IBM Db2 source allows you to sync data from Db2. It supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This IBM Db2 source connector is built on top of the [IBM Data Server Driver](https://mvnrepository.com/artifact/com.ibm.db2/jcc/11.5.5.0) for JDBC and SQLJ. It is a pure-Java driver \(Type 4\) that supports the JDBC 4 specification as described in IBM Db2 [documentation](https://www.ibm.com/docs/en/db2/11.5?topic=apis-supported-drivers-jdbc-sqlj).

#### Resulting schema

The IBM Db2 source does not alter the schema present in your warehouse. Depending on the destination connected to this source, however, the result schema may be altered. See the destination's documentation for more details.

#### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | Yes |  |
| Namespaces | Yes |  |

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

**Note.** Unfortunately SSL and SSH are incompatible because SSH changes the visible name of the target.

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.4 | 2021-12-30 | [9187](https://github.com/airbytehq/airbyte/pull/9187) [8749](https://github.com/airbytehq/airbyte/pull/8749) | Add support of JdbcType.ARRAY to JdbcSourceOperations. |
| 0.1.3 | 2021-11-05 | [7670](https://github.com/airbytehq/airbyte/pull/7670) | Updated unique DB2 types transformation |
| 0.1.2 | 2021-10-25 | [7355](https://github.com/airbytehq/airbyte/pull/7355) | Added ssl support |
| 0.1.1 | 2021-08-13 | [4699](https://github.com/airbytehq/airbyte/pull/4699) | Added json config validator |
| 0.1.0 | 2021-06-22 | [4197](https://github.com/airbytehq/airbyte/pull/4197) | New Source: IBM DB2 |

