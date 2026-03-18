import KeypairExample from '@site/static/_snowflake_keypair_generation.md';

# Snowflake

## Overview

The Snowflake source connector syncs data from [Snowflake](https://www.snowflake.com/) to your chosen destination. It supports Full Refresh and Incremental syncs using user-defined cursor fields.

The connector uses the [Snowflake JDBC driver](https://github.com/snowflakedb/snowflake-jdbc) to connect to your Snowflake instance.

### Output schema

The Snowflake source does not alter the schema present in your warehouse. Depending on the destination connected to this source, however, the result schema may be altered. See the destination's documentation for more details.

### Features

| Feature                   | Supported | Notes |
| :------------------------ | :-------- | :---- |
| Full Refresh Sync         | Yes       |       |
| Incremental - Append Sync | Yes       |       |
| Namespaces                | Yes       |       |

## Getting started

### Requirements

To configure the Snowflake source, you need:

1. **Host** - The host domain of your Snowflake instance, including the account, region, and cloud environment. Must end with `snowflakecomputing.com`. Example: `accountname.us-east-2.aws.snowflakecomputing.com`
2. **Role** - A Snowflake role with read access to the schemas you want to replicate.
3. **Warehouse** - The Snowflake warehouse to use for running queries.
4. **Database** - The Snowflake database containing the data to replicate.
5. **Schema** (Optional) - The specific schema to replicate. If left empty, the connector discovers tables from all schemas you have access to.
6. **Authentication** - Either username and password or key pair credentials.
7. **JDBC URL Params** (Optional) - Additional JDBC connection properties, formatted as `key=value` pairs separated by `&`.

### Setup guide

#### Create a dedicated read-only user

This step is optional but highly recommended for better permission control and auditing. Alternatively, you can use an existing Snowflake user.

Run the following SQL commands in Snowflake to create a dedicated user and role:

```sql
-- Set variables (these need to be uppercase)
SET AIRBYTE_ROLE = 'AIRBYTE_ROLE';
SET AIRBYTE_USERNAME = 'AIRBYTE_USER';
SET AIRBYTE_PASSWORD = '-password-';
SET AIRBYTE_WAREHOUSE = 'AIRBYTE_WAREHOUSE';
SET AIRBYTE_DATABASE = 'YOUR_DATABASE';
SET AIRBYTE_SCHEMA = 'YOUR_SCHEMA';

BEGIN;

-- Create Airbyte role
CREATE ROLE IF NOT EXISTS IDENTIFIER($AIRBYTE_ROLE);

-- Create Airbyte user
CREATE USER IF NOT EXISTS IDENTIFIER($AIRBYTE_USERNAME)
PASSWORD = $AIRBYTE_PASSWORD
DEFAULT_ROLE = $AIRBYTE_ROLE
DEFAULT_WAREHOUSE = $AIRBYTE_WAREHOUSE;

-- Grant the role to the user
GRANT ROLE IDENTIFIER($AIRBYTE_ROLE) TO USER IDENTIFIER($AIRBYTE_USERNAME);

-- Grant read access
GRANT USAGE ON WAREHOUSE IDENTIFIER($AIRBYTE_WAREHOUSE) TO ROLE IDENTIFIER($AIRBYTE_ROLE);
GRANT USAGE ON DATABASE IDENTIFIER($AIRBYTE_DATABASE) TO ROLE IDENTIFIER($AIRBYTE_ROLE);
GRANT USAGE ON SCHEMA IDENTIFIER($AIRBYTE_DATABASE || '.' || $AIRBYTE_SCHEMA) TO ROLE IDENTIFIER($AIRBYTE_ROLE);
GRANT SELECT ON ALL TABLES IN SCHEMA IDENTIFIER($AIRBYTE_DATABASE || '.' || $AIRBYTE_SCHEMA) TO ROLE IDENTIFIER($AIRBYTE_ROLE);
GRANT SELECT ON FUTURE TABLES IN SCHEMA IDENTIFIER($AIRBYTE_DATABASE || '.' || $AIRBYTE_SCHEMA) TO ROLE IDENTIFIER($AIRBYTE_ROLE);

COMMIT;
```

To replicate data from multiple schemas, repeat the `GRANT USAGE ON SCHEMA` and `GRANT SELECT` statements for each schema.

#### Connection parameters

For additional JDBC connection parameters, see the [Snowflake JDBC documentation](https://docs.snowflake.com/en/user-guide/jdbc-configure.html#connection-parameters).

### Authentication

The connector supports two authentication methods.

#### Username and password

Provide your Snowflake username and password in the connector configuration.

#### Key pair authentication

<KeypairExample/>

### Network policies

By default, Snowflake allows connections from any IP address. If your Snowflake account uses [network policies](https://docs.snowflake.com/en/user-guide/network-policies.html), you must allow the IP addresses used by Airbyte.

If you use Airbyte Cloud, add the Airbyte Cloud IP addresses to your Snowflake network policy's allowed list.

To check whether a network policy is set on your account or for a specific user:

```sql
-- Check account-level network policy
SHOW PARAMETERS LIKE 'network_policy' IN ACCOUNT;

-- Check user-level network policy
SHOW PARAMETERS LIKE 'network_policy' IN USER <username>;
```

### Advanced configuration

The connector exposes several optional settings for fine-tuning sync behavior:

| Setting | Description | Default |
| :------ | :---------- | :------ |
| **Concurrency** | Maximum number of concurrent queries to Snowflake during a sync. Increasing this value can improve throughput for databases with many tables. | 1 |
| **Checkpoint Target Time Interval** | How often, in seconds, the connector checkpoints sync progress. Lower values produce more frequent state messages, which can improve recovery time if a sync is interrupted. | 300 |
| **Check Table and Column Access Privileges** | When enabled, the connector tests access to each table individually during schema discovery and excludes inaccessible tables. In large schemas, disabling this can speed up discovery. | Enabled |

## Data type mapping

The connector maps Snowflake data types to Airbyte types as follows:

| Snowflake type | Airbyte type | Notes |
| :------------- | :----------- | :---- |
| `VARCHAR`, `CHAR`, `CHARACTER`, `STRING`, `TEXT` | String | |
| `BOOLEAN` | Boolean | |
| `NUMBER`, `DECIMAL`, `NUMERIC` | Number | |
| `INT`, `INTEGER` | Integer | |
| `BIGINT` | Integer | |
| `SMALLINT`, `TINYINT` | Integer | |
| `FLOAT`, `FLOAT4`, `FLOAT8`, `DOUBLE`, `DOUBLE PRECISION`, `REAL` | Number | |
| `DATE` | Date | |
| `TIME` | Time | |
| `TIMESTAMP_NTZ`, `TIMESTAMP`, `DATETIME` | Timestamp without timezone | Truncated to microsecond precision |
| `TIMESTAMP_TZ`, `TIMESTAMP_LTZ` | Timestamp with timezone | Converted to UTC. Truncated to microsecond precision |
| `BINARY`, `VARBINARY` | String (base64) | |
| `VARIANT`, `OBJECT`, `ARRAY` | String (JSON) | |
| `GEOGRAPHY`, `GEOMETRY`, `VECTOR`, `FILE` | String | |

### Timestamp precision

Snowflake supports timestamp precision up to 9 decimal places (nanoseconds). The connector truncates all timestamp values to 6 decimal places (microseconds) to ensure compatibility with destinations that do not support nanosecond precision.

This truncation applies to `TIMESTAMP_NTZ`, `TIMESTAMP`, `DATETIME`, `TIMESTAMP_TZ`, and `TIMESTAMP_LTZ` columns.

### Timezone handling

Snowflake's `TIMESTAMP_TZ` and `TIMESTAMP_LTZ` types are converted to UTC during replication. The original timezone offset is not preserved.

`TIMESTAMP_NTZ` and its synonym `DATETIME` are replicated without any timezone conversion.

## Incremental sync

The connector supports [incremental sync](/understanding-airbyte/connections/incremental-append) using a user-defined cursor field.

During each sync, the connector queries only records where the cursor value is greater than the last-synced value. Choose a cursor field that is monotonically increasing and never updated after creation, such as a `CREATED_AT` timestamp or an auto-incrementing ID.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                                   |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------|
| 1.0.10  | 2026-03-18 | [74834](https://github.com/airbytehq/airbyte/pull/74834) | Truncate timestamp precision to 6 digits (microseconds) to prevent precision errors in destinations                                       |
| 1.0.9   | 2025-09-16 | [74081](https://github.com/airbytehq/airbyte/pull/74081) | Security update                                                                                                                           |
| 1.0.8   | 2025-09-16 | [66311](https://github.com/airbytehq/airbyte/pull/66311) | Change CDK version to 0.1.31                                                                                                              |
| 1.0.7   | 2025-09-16 | [66200](https://github.com/airbytehq/airbyte/pull/66200) | Fix sampling bug for DefaultJdbcCursorIncrementalPartition                                                                                |
| 1.0.6   | 2025-09-12 | [66226](https://github.com/airbytehq/airbyte/pull/66226) | Fix schema filtering functionality in versions 1.0.0+ - resolves "discovered zero tables" error and enables proper schema-level filtering |
| 1.0.5   | 2025-07-28 | [63780](https://github.com/airbytehq/airbyte/pull/63780) | Fix ts data type for snowflake                                                                                                            |
| 1.0.3   | 2025-07-22 | [63713](https://github.com/airbytehq/airbyte/pull/63713) | Revert base image from 2.0.3 to 2.0.2 to fix SSL certificate errors                                                                       |
| 1.0.2   | 2025-07-14 | [62939](https://github.com/airbytehq/airbyte/pull/62939) | Update base image to 2.0.3                                                                                                                |
| 1.0.1   | 2025-07-11 | [62929](https://github.com/airbytehq/airbyte/pull/62929) | Update test dependencies                                                                                                                  |
| 1.0.0   | 2025-06-24 | [61535](https://github.com/airbytehq/airbyte/pull/61535) | Replace community support connector with Airbyte certified connector                                                                      |
| 0.3.6   | 2025-01-10 | [51504](https://github.com/airbytehq/airbyte/pull/51504) | Use a non root base image                                                                                                                 |
| 0.3.5   | 2024-12-18 | [49911](https://github.com/airbytehq/airbyte/pull/49911) | Use a base image: airbyte/java-connector-base:1.0.0                                                                                       |
| 0.3.4   | 2024-10-31 | [48073](https://github.com/airbytehq/airbyte/pull/48073) | Upgrade jdbc driver                                                                                                                       |
| 0.3.3   | 2024-06-28 | [40424](https://github.com/airbytehq/airbyte/pull/40424) | Support Snowflake key pair authentication                                                                                                 |
| 0.3.2   | 2024-02-13 | [38317](https://github.com/airbytehq/airbyte/pull/38317) | Hide oAuth option from connector                                                                                                          |
| 0.3.1   | 2024-02-13 | [35220](https://github.com/airbytehq/airbyte/pull/35220) | Adopt CDK 0.20.4                                                                                                                          |
| 0.3.1   | 2024-01-24 | [34453](https://github.com/airbytehq/airbyte/pull/34453) | bump CDK version                                                                                                                          |
| 0.3.0   | 2023-12-18 | [33484](https://github.com/airbytehq/airbyte/pull/33484) | Remove LEGACY state                                                                                                                       |
| 0.2.2   | 2023-10-20 | [31613](https://github.com/airbytehq/airbyte/pull/31613) | Fixed handling of TIMESTAMP_TZ columns. upgrade                                                                                           |
| 0.2.1   | 2023-10-11 | [31252](https://github.com/airbytehq/airbyte/pull/31252) | Snowflake JDBC version upgrade                                                                                                            |
| 0.2.0   | 2023-06-26 | [27737](https://github.com/airbytehq/airbyte/pull/27737) | License Update: Elv2                                                                                                                      |
| 0.1.36  | 2023-06-20 | [27212](https://github.com/airbytehq/airbyte/pull/27212) | Fix silent exception swallowing in StreamingJdbcDatabase                                                                                  |
| 0.1.35  | 2023-06-14 | [27335](https://github.com/airbytehq/airbyte/pull/27335) | Remove noisy debug logs                                                                                                                   |
| 0.1.34  | 2023-03-30 | [24693](https://github.com/airbytehq/airbyte/pull/24693) | Fix failure with TIMESTAMP_WITH_TIMEZONE column being used as cursor                                                                      |
| 0.1.33  | 2023-03-29 | [24667](https://github.com/airbytehq/airbyte/pull/24667) | Fix bug which wont allow TIMESTAMP_WITH_TIMEZONE column to be used as a cursor                                                            |
| 0.1.32  | 2023-03-22 | [20760](https://github.com/airbytehq/airbyte/pull/20760) | Removed redundant date-time datatypes formatting                                                                                          |
| 0.1.31  | 2023-03-06 | [23455](https://github.com/airbytehq/airbyte/pull/23455) | For network isolation, source connector accepts a list of hosts it is allowed to connect to                                               |
| 0.1.30  | 2023-02-21 | [22358](https://github.com/airbytehq/airbyte/pull/22358) | Improved handling of big integer cursor type values.                                                                                      |
| 0.1.29  | 2022-12-14 | [20346](https://github.com/airbytehq/airbyte/pull/20346) | Consolidate date/time values mapping for JDBC sources.                                                                                    |
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
