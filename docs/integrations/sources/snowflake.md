# Snowflake

## Overview

The Snowflake source allows you to sync data from Snowflake. It supports both Full Refresh and Incremental syncs. You can choose whether this connector will copy only new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This Snowflake source connector is built on top of the source-jdbc code base and is configured to rely on JDBC 3.23.1 [Snowflake driver](https://github.com/snowflakedb/snowflake-jdbc) as described in the Snowflake [documentation](https://docs.snowflake.com/en/user-guide/jdbc.html).

#### Resulting schema

The Snowflake source does not alter the schema present in your warehouse. Depending on the destination connected to this source, however, the result schema may be altered. See the destination's documentation for more details.

#### Features

| Feature                   | Supported?\(Yes/No\) | Notes |
| :------------------------ | :------------------- | :---- |
| Full Refresh Sync         | Yes                  |       |
| Incremental - Append Sync | Yes                  |       |
| Namespaces                | Yes                  |       |

## Incremental Sync

The Snowflake source connector supports incremental sync, which allows you to replicate only new or updated data since the last sync. This is accomplished using a cursor field that tracks the state of the sync.

### How Incremental Sync Works

During incremental sync, the connector:

1. **Identifies new records**: Uses a `WHERE cursor_field > last_cursor_value` clause to fetch only records newer than the last synced value
2. **Maintains order**: Applies `ORDER BY cursor_field ASC` to ensure records are processed in the correct sequence
3. **Tracks state**: Stores the maximum cursor value from each sync to use as the starting point for the next sync

### Supported Cursor Field Data Types

The connector supports the following JDBC data types as cursor fields:

**Date and Time Types:**
- `TIMESTAMP_WITH_TIMEZONE`
- `TIMESTAMP` 
- `TIME_WITH_TIMEZONE`
- `TIME`
- `DATE`

**Numeric Types:**
- `TINYINT`
- `SMALLINT` 
- `INTEGER`
- `BIGINT`
- `FLOAT`
- `DOUBLE`
- `REAL`
- `NUMERIC`
- `DECIMAL`

**String Types:**
- `NVARCHAR`
- `VARCHAR`
- `LONGVARCHAR`

### Choosing a Cursor Field

For effective incremental sync, choose cursor fields that:

- **Are monotonically increasing**: Values should always increase over time (e.g., auto-incrementing IDs, creation timestamps)
- **Are never updated**: Avoid fields that might be modified after record creation
- **Have unique values**: While duplicate values are handled, they can cause records to be skipped or re-synced
- **Are indexed**: For better query performance on large tables

**Good cursor field examples:**
- `CREATED_AT` or `UPDATED_AT` timestamp columns
- Auto-incrementing `ID` columns
- Sequence-generated numeric fields

**Avoid using:**
- Fields that can be updated after creation
- Fields with many duplicate values
- Fields that can contain NULL values

### Snowflake-Specific Considerations

**Timezone Handling**: The connector provides special handling for Snowflake's `TIMESTAMPLTZ` (timestamp with local timezone) data type, automatically converting it to `TIMESTAMP_WITH_TIMEZONE` for consistent processing.

**Data Type Precision**: Snowflake's numeric types maintain their precision during sync. Ensure your destination can handle the precision of your cursor fields.

### Configuring Incremental Sync

To set up incremental sync in Airbyte:

1. **Create or edit your connection** in the Airbyte UI
2. **Select your source tables** that you want to sync incrementally
3. **Choose "Incremental | Append" sync mode** for each table
4. **Select a cursor field** from the dropdown list of available fields
5. **Verify the cursor field** meets the criteria listed above (monotonically increasing, never updated, etc.)

The Airbyte UI will automatically validate that your chosen cursor field is compatible with incremental sync and will show you the supported data types for your specific table schema.

### Troubleshooting Incremental Sync

**Cursor field validation errors**: If you receive an error about an invalid cursor field, ensure the field exists in your table and is one of the supported data types listed above.

**Duplicate cursor values**: When multiple records have the same cursor value, the connector processes all records with that value. This may result in some records being synced multiple times across different sync runs.

**NULL cursor values**: Records with NULL cursor field values are excluded from incremental sync. Ensure your cursor field has a NOT NULL constraint or default value.

**State reset**: If you need to re-sync all data, you can reset the connection's state in the Airbyte UI, which will cause the next sync to behave like a full refresh.

## Getting started

### Requirements

You'll need the following information to configure the Snowflake source:

1. **Host**
2. **Role**
3. **Warehouse**
4. **Database**
5. **Schema**
6. **Username**
7. **Password**
8. **JDBC URL Params** (Optional)

Additionally, create a dedicated read-only Airbyte user and role with access to all schemas needed for replication.

### Setup guide

#### Connection parameters

Additional information about Snowflake connection parameters can be found in the [Snowflake documentation](https://docs.snowflake.com/en/user-guide/jdbc-configure.html#connection-parameters).

#### Create a dedicated read-only user (Recommended but optional)

This step is optional but highly recommended for better permission control and auditing. Alternatively, you can use Airbyte with an existing user in your database.

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

You can limit this grant to specific schemas instead of the whole database. Note that to replicate data from multiple Snowflake databases, you can re-run the command above to grant access to all the relevant schemas, but you'll need to set up multiple sources connecting to the same database on multiple schemas.

Your database user should now be ready for use with Airbyte.

### Authentication

#### Login and Password

| Field                                                                                                 | Description                                                                                                                                                                                       |
| ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Host](https://docs.snowflake.com/en/user-guide/admin-account-identifier.html)                        | The host domain of the snowflake instance (must include the account, region, cloud environment, and end with snowflakecomputing.com). Example: `accountname.us-east-2.aws.snowflakecomputing.com` |
| [Role](https://docs.snowflake.com/en/user-guide/security-access-control-overview.html#roles)          | The role you created for Airbyte to access Snowflake. Example: `AIRBYTE_ROLE`                                                                                                           |
| [Warehouse](https://docs.snowflake.com/en/user-guide/warehouses-overview.html#overview-of-warehouses) | The warehouse you created for Airbyte to sync data into. Example: `AIRBYTE_WAREHOUSE`                                                                                                   |
| [Database](https://docs.snowflake.com/en/sql-reference/ddl-database.html#database-schema-share-ddl)   | The database you created for Airbyte to sync data into. Example: `AIRBYTE_DATABASE`                                                                                                     |
| [Schema](https://docs.snowflake.com/en/sql-reference/ddl-database.html#database-schema-share-ddl)     | The schema whose tables this replication is targeting. If no schema is specified, all tables with permission will be presented regardless of their schema.                                        |
| Username                                                                                              | The username you created to allow Airbyte to access the database. Example: `AIRBYTE_USER`                                                                                               |
| Password                                                                                              | The password associated with the username.                                                                                                                                                        |
| [JDBC URL Params](https://docs.snowflake.com/en/user-guide/jdbc-parameters.html) (Optional)           | Additional properties to pass to the JDBC URL string when connecting to the database formatted as `key=value` pairs separated by the symbol `&`. Example: `key1=value1&key2=value2&key3=value3`   |

### Key pair authentication

To configure key pair authentication, you will need a private/public key pair.
If you do not have the key pair yet, you can generate one using the openssl command line tool.
Use this command to generate an unencrypted private key file:

`openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key.p8 -nocrypt`

Alternatively, use this command to generate an encrypted private key file:

`openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -v1 PBE-SHA1-RC4-128 -out rsa_key.p8`

Once you have your private key, you need to generate a matching public key.
You can do this with the following command:

`openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub`

Finally, you need to add the public key to your Snowflake user account.
You can do this with the following SQL command in Snowflake:

`alter user <user_name> set rsa_public_key=<public_key_value>;`

and replace `<user_name>` with your user name and `<public_key_value>` with your public key.

### Network policies

By default, Snowflake allows users to connect to the service from any computer or device IP address. A security administrator (i.e. users with the SECURITYADMIN role) or higher can create a network policy to allow or deny access to a single IP address or a list of addresses.

If you have any issues connecting with Airbyte Cloud, please make sure that the list of IP addresses is on the allowed list.

To determine whether a network policy is set on your account or for a specific user, execute the _SHOW PARAMETERS_ command.

**Account**

```
SHOW PARAMETERS LIKE 'network_policy' IN ACCOUNT;
```

**User**

```
SHOW PARAMETERS LIKE 'network_policy' IN USER <username>;
```

To read more, please check the official [Snowflake documentation](https://docs.snowflake.com/en/user-guide/network-policies.html#).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                                   |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------|
| 1.0.5 | 2025-07-28 | [63780](https://github.com/airbytehq/airbyte/pull/63780) | Fix ts data type for snowflake |
| 1.0.3 | 2025-07-22 | [63713](https://github.com/airbytehq/airbyte/pull/63713) | Revert base image from 2.0.3 to 2.0.2 to fix SSL certificate errors |
| 1.0.2 | 2025-07-14 | [62939](https://github.com/airbytehq/airbyte/pull/62939) | Update base image to 2.0.3 |
| 1.0.1 | 2025-07-11 | [62929](https://github.com/airbytehq/airbyte/pull/62929) | Update test dependencies |
| 1.0.0 | 2025-06-24 | [61535](https://github.com/airbytehq/airbyte/pull/61535) | Replace community support connector with Airbyte certified connector |
| 0.3.6 | 2025-01-10 | [51504](https://github.com/airbytehq/airbyte/pull/51504) | Use a non root base image |
| 0.3.5 | 2024-12-18 | [49911](https://github.com/airbytehq/airbyte/pull/49911) | Use a base image: airbyte/java-connector-base:1.0.0 |
| 0.3.4 | 2024-10-31 | [48073](https://github.com/airbytehq/airbyte/pull/48073) | Upgrade jdbc driver |
| 0.3.3 | 2024-06-28 | [40424](https://github.com/airbytehq/airbyte/pull/40424) | Support Snowflake key pair authentication |
| 0.3.2 | 2024-02-13 | [38317](https://github.com/airbytehq/airbyte/pull/38317) | Hide oAuth option from connector |
| 0.3.1 | 2024-02-13 | [35220](https://github.com/airbytehq/airbyte/pull/35220) | Adopt CDK 0.20.4 |
| 0.3.1 | 2024-01-24 | [34453](https://github.com/airbytehq/airbyte/pull/34453) | bump CDK version |
| 0.3.0 | 2023-12-18 | [33484](https://github.com/airbytehq/airbyte/pull/33484) | Remove LEGACY state |
| 0.2.2 | 2023-10-20 | [31613](https://github.com/airbytehq/airbyte/pull/31613) | Fixed handling of TIMESTAMP_TZ columns. upgrade |
| 0.2.1 | 2023-10-11 | [31252](https://github.com/airbytehq/airbyte/pull/31252) | Snowflake JDBC version upgrade |
| 0.2.0 | 2023-06-26 | [27737](https://github.com/airbytehq/airbyte/pull/27737) | License Update: Elv2 |
| 0.1.36 | 2023-06-20 | [27212](https://github.com/airbytehq/airbyte/pull/27212) | Fix silent exception swallowing in StreamingJdbcDatabase |
| 0.1.35 | 2023-06-14 | [27335](https://github.com/airbytehq/airbyte/pull/27335) | Remove noisy debug logs |
| 0.1.34 | 2023-03-30 | [24693](https://github.com/airbytehq/airbyte/pull/24693) | Fix failure with TIMESTAMP_WITH_TIMEZONE column being used as cursor |
| 0.1.33 | 2023-03-29 | [24667](https://github.com/airbytehq/airbyte/pull/24667) | Fix bug which wont allow TIMESTAMP_WITH_TIMEZONE column to be used as a cursor |
| 0.1.32 | 2023-03-22 | [20760](https://github.com/airbytehq/airbyte/pull/20760) | Removed redundant date-time datatypes formatting |
| 0.1.31 | 2023-03-06 | [23455](https://github.com/airbytehq/airbyte/pull/23455) | For network isolation, source connector accepts a list of hosts it is allowed to connect to |
| 0.1.30 | 2023-02-21 | [22358](https://github.com/airbytehq/airbyte/pull/22358) | Improved handling of big integer cursor type values. |
| 0.1.29  | 2022-12-14 | [20436](https://github.com/airbytehq/airbyte/pull/20346) | Consolidate date/time values mapping for JDBC sources.                                                                                    |
| 0.1.28  | 2023-01-06 | [20465](https://github.com/airbytehq/airbyte/pull/20465) | Improve the schema config field to only discover tables from the specified scehma and make the field optional                             |
| 0.1.27  | 2022-12-14 | [20407](https://github.com/airbytehq/airbyte/pull/20407) | Fix an issue with integer values converted to floats during replication                                                                   |
| 0.1.26  | 2022-11-10 | [19314](https://github.com/airbytehq/airbyte/pull/19314) | Set application id in JDBC URL params based on OSS/Cloud environment                                                                      |
| 0.1.25  | 2022-11-10 | [15535](https://github.com/airbytehq/airbyte/pull/15535) | Update incremental query to avoid data missing when new data is inserted at the same time as a sync starts under non-CDC incremental mode |
| 0.1.24  | 2022-09-26 | [17144](https://github.com/airbytehq/airbyte/pull/17144) | Fixed bug with incorrect date-time datatypes handling                                                                                     |
| 0.1.23  | 2022-09-26 | [17116](https://github.com/airbytehq/airbyte/pull/17116) | added connection string identifier                                                                                                        |
| 0.1.22  | 2022-09-21 | [16766](https://github.com/airbytehq/airbyte/pull/16766) | Update JDBC Driver version to 3.13.22                                                                                                     |
| 0.1.21  | 2022-09-14 | [15668](https://github.com/airbytehq/airbyte/pull/15668) | Wrap logs in AirbyteLogMessage                                                                                                            |
| 0.1.20  | 2022-09-01 | [16258](https://github.com/airbytehq/airbyte/pull/16258) | Emit state messages more frequently                                                                                                       |
| 0.1.19  | 2022-08-19 | [15797](https://github.com/airbytehq/airbyte/pull/15797) | Allow using role during oauth                                                                                                             |
| 0.1.18  | 2022-08-18 | [14356](https://github.com/airbytehq/airbyte/pull/14356) | DB Sources: only show a table can sync incrementally if at least one column can be used as a cursor field                                 |
| 0.1.17  | 2022-08-09 | [15314](https://github.com/airbytehq/airbyte/pull/15314) | Discover integer columns as integers rather than floats                                                                                   |
| 0.1.16  | 2022-08-04 | [15314](https://github.com/airbytehq/airbyte/pull/15314) | (broken, do not use) Discover integer columns as integers rather than floats                                                              |
| 0.1.15  | 2022-07-22 | [14828](https://github.com/airbytehq/airbyte/pull/14828) | Source Snowflake: Source/Destination doesn't respect DATE data type                                                                       |
| 0.1.14  | 2022-07-22 | [14714](https://github.com/airbytehq/airbyte/pull/14714) | Clarified error message when invalid cursor column selected                                                                               |
| 0.1.13  | 2022-07-14 | [14574](https://github.com/airbytehq/airbyte/pull/14574) | Removed additionalProperties:false from JDBC source connectors                                                                            |
| 0.1.12  | 2022-04-29 | [12480](https://github.com/airbytehq/airbyte/pull/12480) | Query tables with adaptive fetch size to optimize JDBC memory consumption                                                                 |
| 0.1.11  | 2022-04-27 | [10953](https://github.com/airbytehq/airbyte/pull/10953) | Implement OAuth flow                                                                                                                      |
| 0.1.9   | 2022-02-21 | [10242](https://github.com/airbytehq/airbyte/pull/10242) | Fixed cursor for old connectors that use non-microsecond format. Now connectors work with both formats                                    |
| 0.1.8   | 2022-02-18 | [10242](https://github.com/airbytehq/airbyte/pull/10242) | Updated timestamp transformation with microseconds                                                                                        |
| 0.1.7   | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256) | Add `-XX:+ExitOnOutOfMemoryError` JVM option                                                                                              |
| 0.1.6   | 2022-01-25 | [9623](https://github.com/airbytehq/airbyte/pull/9623)   | Add jdbc_url_params support for optional JDBC parameters                                                                                  |
| 0.1.5   | 2022-01-19 | [9567](https://github.com/airbytehq/airbyte/pull/9567)   | Added parameter for keeping JDBC session alive                                                                                            |
| 0.1.4   | 2021-12-30 | [9203](https://github.com/airbytehq/airbyte/pull/9203)   | Update connector fields title/description                                                                                                 |
| 0.1.3   | 2021-01-11 | [9304](https://github.com/airbytehq/airbyte/pull/9304)   | Upgrade version of JDBC driver                                                                                                            |
| 0.1.2   | 2021-10-21 | [7257](https://github.com/airbytehq/airbyte/pull/7257)   | Fixed parsing of extreme values for FLOAT and NUMBER data types                                                                           |
| 0.1.1   | 2021-08-13 | [4699](https://github.com/airbytehq/airbyte/pull/4699)   | Added json config validator                                                                                                               |

</details>
