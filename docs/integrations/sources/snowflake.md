# Snowflake

## Overview

The Snowflake source allows you to sync data from Snowflake. It supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This Snowflake source connector is built on top of the source-jdbc code base and is configured to rely on JDBC 3.12.14 [Snowflake driver](https://github.com/snowflakedb/snowflake-jdbc) as described in Snowflake [documentation](https://docs.snowflake.com/en/user-guide/jdbc.html).

#### Resulting schema

The Snowflake source does not alter the schema present in your warehouse. Depending on the destination connected to this source, however, the result schema may be altered. See the destination's documentation for more details.

#### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | Yes |  |
| Namespaces | Yes |  |

## Getting started

### Requirements

1. You'll need the following information to configure the Snowflake source:
2. **Host**
3. **Role**
4. **Warehouse**
5. **Database**
6. **Schema**
7. **Username**
8. **Password**
9. **JDBC URL Params** (Optional)
10. Create a dedicated read-only Airbyte user and role with access to all schemas needed for replication.

### Setup guide

#### 1. Additional information about Snowflake connection parameters could be found [here](https://docs.snowflake.com/en/user-guide/jdbc-configure.html#connection-parameters).

#### 2. Create a dedicated read-only user with access to the relevant schemas \(Recommended but optional\)

This step is optional but highly recommended to allow for better permission control and auditing. Alternatively, you can use Airbyte with an existing user in your database.

To create a dedicated database user, run the following commands against your database:

```sql
-- set variables (these need to be uppercase)
SET AIRBYTE_ROLE = 'AIRBYTE_ROLE';
SET AIRBYTE_USERNAME = 'AIRBYTE_USER';

-- set user password
SET AIRBYTE_PASSWORD = '-password-';

BEGIN;

-- create Airbyte role
CREATE ROLE IF NOT EXISTS $AIRBYTE_ROLE;

-- create Airbyte user
CREATE USER IF NOT EXISTS $AIRBYTE_USERNAME
PASSWORD = $AIRBYTE_PASSWORD
DEFAULT_ROLE = $AIRBYTE_ROLE
DEFAULT_WAREHOUSE= $AIRBYTE_WAREHOUSE;

-- grant Airbyte schema access
GRANT OWNERSHIP ON SCHEMA $AIRBYTE_SCHEMA TO ROLE $AIRBYTE_ROLE;

COMMIT;
```

You can limit this grant down to specific schemas instead of the whole database. Note that to replicate data from multiple Snowflake databases, you can re-run the command above to grant access to all the relevant schemas, but you'll need to set up multiple sources connecting to the same db on multiple schemas.

Your database user should now be ready for use with Airbyte.

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.6 | 2022-01-25 | [9623](https://github.com/airbytehq/airbyte/pull/9623) | Add jdbc_url_params support for optional JDBC parameters |
| 0.1.5 | 2022-01-19 | [9567](https://github.com/airbytehq/airbyte/pull/9567) | Added parameter for keeping JDBC session alive |
| 0.1.4 | 2021-12-30 | [9203](https://github.com/airbytehq/airbyte/pull/9203) | Update connector fields title/description |
| 0.1.3 | 2021-01-11 | [9304](https://github.com/airbytehq/airbyte/pull/9304) | Upgrade version of JDBC driver |
| 0.1.2 | 2021-10-21 | [7257](https://github.com/airbytehq/airbyte/pull/7257) | Fixed parsing of extreme values for FLOAT and NUMBER data types |
| 0.1.1 | 2021-08-13 | [4699](https://github.com/airbytehq/airbyte/pull/4699) | Added json config validator |
