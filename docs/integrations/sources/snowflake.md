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

###Authentication
#### There are 2 way ways of oauth supported: login\pass and oauth2.

### Login and Password
| Field | Description                                                                                                                                                                                       |
|---|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [Host](https://docs.snowflake.com/en/user-guide/admin-account-identifier.html) | The host domain of the snowflake instance (must include the account, region, cloud environment, and end with snowflakecomputing.com). Example: `accountname.us-east-2.aws.snowflakecomputing.com` |
| [Role](https://docs.snowflake.com/en/user-guide/security-access-control-overview.html#roles) | The role you created in Step 1 for Airbyte to access Snowflake. Example: `AIRBYTE_ROLE`                                                                                                           |
| [Warehouse](https://docs.snowflake.com/en/user-guide/warehouses-overview.html#overview-of-warehouses) | The warehouse you created in Step 1 for Airbyte to sync data into. Example: `AIRBYTE_WAREHOUSE`                                                                                                   |
| [Database](https://docs.snowflake.com/en/sql-reference/ddl-database.html#database-schema-share-ddl) | The database you created in Step 1 for Airbyte to sync data into. Example: `AIRBYTE_DATABASE`                                                                                                     |
| [Schema](https://docs.snowflake.com/en/sql-reference/ddl-database.html#database-schema-share-ddl) | The default schema used as the target schema for all statements issued from the connection that do not explicitly specify a schema name.                                                          |
| Username | The username you created in Step 2 to allow Airbyte to access the database. Example: `AIRBYTE_USER`                                                                                               |
| Password | The password associated with the username.                                                                                                                                                        |
| [JDBC URL Params](https://docs.snowflake.com/en/user-guide/jdbc-parameters.html) (Optional) | Additional properties to pass to the JDBC URL string when connecting to the database formatted as `key=value` pairs separated by the symbol `&`. Example: `key1=value1&key2=value2&key3=value3`   |


### OAuth 2.0
Field | Description |
|---|---|
| [Host](https://docs.snowflake.com/en/user-guide/admin-account-identifier.html) | The host domain of the snowflake instance (must include the account, region, cloud environment, and end with snowflakecomputing.com). Example: `accountname.us-east-2.aws.snowflakecomputing.com` |
| [Role](https://docs.snowflake.com/en/user-guide/security-access-control-overview.html#roles) | The role you created in Step 1 for Airbyte to access Snowflake. Example: `AIRBYTE_ROLE` |
| [Warehouse](https://docs.snowflake.com/en/user-guide/warehouses-overview.html#overview-of-warehouses) | The warehouse you created in Step 1 for Airbyte to sync data into. Example: `AIRBYTE_WAREHOUSE` |
| [Database](https://docs.snowflake.com/en/sql-reference/ddl-database.html#database-schema-share-ddl) | The database you created in Step 1 for Airbyte to sync data into. Example: `AIRBYTE_DATABASE` |
| [Schema](https://docs.snowflake.com/en/sql-reference/ddl-database.html#database-schema-share-ddl) | The default schema used as the target schema for all statements issued from the connection that do not explicitly specify a schema name.  |
| OAuth2 | The Login name and password to obtain auth token. |
| [JDBC URL Params](https://docs.snowflake.com/en/user-guide/jdbc-parameters.html) (Optional) | Additional properties to pass to the JDBC URL string when connecting to the database formatted as `key=value` pairs separated by the symbol `&`. Example: `key1=value1&key2=value2&key3=value3` |

### Network policies

By default, Snowflake allows users to connect to the service from any computer or device IP address. A security administrator (i.e. users with the SECURITYADMIN role) or higher can create a network policy to allow or deny access to a single IP address or a list of addresses.

If you have any issues connecting with Airbyte Cloud please make sure that the list of IP addresses is on the allowed list

To determine whether a network policy is set on your account or for a specific user, execute the _SHOW PARAMETERS_ command.

**Account**

        SHOW PARAMETERS LIKE 'network_policy' IN ACCOUNT;

**User**

        SHOW PARAMETERS LIKE 'network_policy' IN USER <username>;

To read more please check official [Snowflake documentation](https://docs.snowflake.com/en/user-guide/network-policies.html#)


## Changelog

| Version   | Date | Pull Request | Subject |
|:----------| :--- | :--- | :--- |
| 0.1.16    | 2022-08-09 | [15314](https://github.com/airbytehq/airbyte/pull/15314) | Discover integer columns as integers rather than floats |
| 0.1.16    | 2022-08-04 | [15314](https://github.com/airbytehq/airbyte/pull/15314) | (broken, do not use) Discover integer columns as integers rather than floats |
| 0.1.15    | 2022-07-22 | [14828](https://github.com/airbytehq/airbyte/pull/14828) | Source Snowflake: Source/Destination doesn't respect DATE data type                                   |
| 0.1.14    | 2022-07-22 | [14714](https://github.com/airbytehq/airbyte/pull/14714) | Clarified error message when invalid cursor column selected |
| 0.1.13    | 2022-07-14 | [14574](https://github.com/airbytehq/airbyte/pull/14574) | Removed additionalProperties:false from JDBC source connectors |
| 0.1.12    | 2022-04-29 | [12480](https://github.com/airbytehq/airbyte/pull/12480) | Query tables with adaptive fetch size to optimize JDBC memory consumption |
| 0.1.11    | 2022-04-27 | [10953](https://github.com/airbytehq/airbyte/pull/10953) | Implement OAuth flow |
| 0.1.9     | 2022-02-21 | [10242](https://github.com/airbytehq/airbyte/pull/10242) | Fixed cursor for old connectors that use non-microsecond format. Now connectors work with both formats |
| 0.1.8     | 2022-02-18 | [10242](https://github.com/airbytehq/airbyte/pull/10242) | Updated timestamp transformation with microseconds |
| 0.1.7     | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256) | Add `-XX:+ExitOnOutOfMemoryError` JVM option |
| 0.1.6     | 2022-01-25 | [9623](https://github.com/airbytehq/airbyte/pull/9623) | Add jdbc_url_params support for optional JDBC parameters |
| 0.1.5     | 2022-01-19 | [9567](https://github.com/airbytehq/airbyte/pull/9567) | Added parameter for keeping JDBC session alive |
| 0.1.4     | 2021-12-30 | [9203](https://github.com/airbytehq/airbyte/pull/9203) | Update connector fields title/description |
| 0.1.3     | 2021-01-11 | [9304](https://github.com/airbytehq/airbyte/pull/9304) | Upgrade version of JDBC driver |
| 0.1.2     | 2021-10-21 | [7257](https://github.com/airbytehq/airbyte/pull/7257) | Fixed parsing of extreme values for FLOAT and NUMBER data types |
| 0.1.1     | 2021-08-13 | [4699](https://github.com/airbytehq/airbyte/pull/4699) | Added json config validator |
