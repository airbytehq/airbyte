import KeypairExample from '@site/static/_snowflake_keypair_generation.md';

# Snowflake

## Overview

The Snowflake source allows you to sync data from Snowflake. It supports both Full Refresh and Incremental syncs. You can choose whether this connector will copy only new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

The connector queries Snowflake with the [Snowflake JDBC driver](https://github.com/snowflakedb/snowflake-jdbc), version 4.0.2. See Snowflake's [JDBC driver documentation](https://docs.snowflake.com/en/developer-guide/jdbc/jdbc) for background on the driver and its connection parameters.

#### Resulting schema

The Snowflake source does not alter the schema present in your warehouse. Depending on the destination connected to this source, however, the result schema may be altered. See the destination's documentation for more details.

The connector discovers tables and views in the database you configure. It always skips the `INFORMATION_SCHEMA`, `SNOWFLAKE_SAMPLE_DATA`, and `UTIL_DB` schemas. If you leave **Schema** empty, the connector lists objects from every schema your role can read.

The connector maps Snowflake types to Airbyte types as follows.

| Snowflake type | Airbyte type |
| --- | --- |
| `VARCHAR`, `CHAR`, `CHARACTER`, `STRING`, `TEXT` | String |
| `BOOLEAN` | Boolean |
| `NUMBER`, `DECIMAL`, `NUMERIC` | Number |
| `INT`, `INTEGER`, `BIGINT`, `SMALLINT`, `TINYINT`, `BYTEINT` | Integer |
| `FLOAT`, `FLOAT4`, `FLOAT8`, `DOUBLE`, `DOUBLE PRECISION`, `REAL` | Number |
| `DATE` | Date |
| `TIME` | Time without time zone |
| `TIMESTAMP`, `TIMESTAMP_NTZ`, `DATETIME` | Timestamp without time zone |
| `TIMESTAMP_LTZ`, `TIMESTAMP_TZ` | Timestamp with time zone |
| `BINARY`, `VARBINARY` | Binary |
| `VARIANT`, `OBJECT`, `ARRAY`, `GEOGRAPHY`, `GEOMETRY`, `VECTOR`, `FILE` | String |

Three of these mappings lose information:

- Semi-structured and geospatial columns are replicated as strings holding Snowflake's text representation of the value, not as nested objects or arrays.
- `TIMESTAMP_TZ` and `TIMESTAMP_LTZ` values are converted to UTC, so the original offset isn't preserved.
- Timestamp values are rounded up to microsecond precision, because Snowflake stores 9 fractional digits and the Airbyte protocol carries 6.

#### Features

| Feature                   | Supported?\(Yes/No\) | Notes |
| :------------------------ | :------------------- | :---- |
| Full Refresh Sync         | Yes                  |       |
| Incremental - Append Sync | Yes                  |       |
| Namespaces                | Yes                  |       |

## Incremental syncs

The connector has no source-defined cursors, so you choose a cursor field for each stream you want to sync incrementally.

### How incremental syncs work

The first sync of a stream reads the whole table and records the highest cursor value it saw. At the start of each later sync, the connector queries the current maximum cursor value and reads the rows between the stored value and that maximum, with the lower bound included and the upper bound included.

Two consequences are worth planning for:

- Because the lower bound is inclusive, rows that share a cursor value with the previous sync's last row are read again. Delivery is at least once, so use a primary key and a deduplicating sync mode in your destination if you need one copy of each row.
- Rows written after the connector reads the maximum cursor value are left for the next sync.

### Choosing a cursor field

A cursor field should only ever gain higher values, and every write that you want to replicate should update it. Creation and modification timestamps and sequence-backed numeric columns work well. Columns that are updated in place without changing the cursor, or that get backdated values, cause the connector to skip rows silently.

Other things to know:

- `BOOLEAN` columns can't be used as cursors.
- Semi-structured and geospatial columns are replicated as strings, so they're compared as strings rather than by their underlying values. Avoid them as cursors.
- Rows with a `NULL` cursor value are replicated during the first sync of the stream, then never again. Prefer a `NOT NULL` cursor column.

### Timestamp cursors

Snowflake stores timestamps with up to nanosecond precision, and the connector rounds them up to the microsecond precision the Airbyte protocol supports. Rounding up means the stored cursor value is never lower than the value that was actually replicated, which is what keeps rows at the boundary from being skipped. The trade-off is that a handful of rows near the boundary can be replicated twice.

`TIMESTAMP_TZ` and `TIMESTAMP_LTZ` cursors are converted to UTC, so cursor comparisons are always in UTC regardless of the session time zone.

### Troubleshooting incremental syncs

**Rows are missing.** Check that every write to the row updates the cursor column, and that no process writes cursor values lower than the values already replicated.

**Rows are duplicated.** This is expected at cursor boundaries. Enable deduplication in the destination, or use a cursor with unique values.

**Start over.** Clearing a connection's state in the Airbyte UI makes the next sync read the full table again.

## Getting started

### Requirements

You'll need the following information to configure the Snowflake source:

1. **Host**
2. **Role**
3. **Warehouse**
4. **Database**
5. **Username**, unless you authenticate with a programmatic access token
6. **Password, private key, or programmatic access token**
7. **Schema** (optional). Leave it empty to replicate from every schema the role can read.
8. **JDBC URL Params** (optional)

Additionally, create a dedicated read-only Airbyte user and role with access to all schemas needed for replication.

### Advanced settings

These settings have working defaults. Change them only if you need to.

| Setting | Default | Description |
| ------- | ------- | ----------- |
| Checkpoint Target Time Interval | 300 | How often, in seconds, a stream checkpoints its progress when possible. |
| Concurrency | 1 | Maximum number of concurrent queries the connector runs against Snowflake. Higher values put more load on the warehouse. |
| Check Table and Column Access Privileges | Enabled | The connector queries each table and view during discovery to confirm the role can read it, and silently drops tables, views, and individual columns it can't read. In large schemas this can make discovery slow, so disable it if discovery times out. |

### Setup guide

#### Connection parameters

Additional information about Snowflake connection parameters can be found in the [Snowflake documentation](https://docs.snowflake.com/en/user-guide/jdbc-configure.html#connection-parameters).

#### Create a dedicated read-only user (Recommended but optional)

This step is optional but highly recommended for better permission control and auditing. Alternatively, you can use Airbyte with an existing user in your database.

Replace the object names with your own, then run the following commands with a role that can create users and roles, such as `USERADMIN`, and grant privileges, such as `SECURITYADMIN`:

```sql
-- create the Airbyte role and user
CREATE ROLE IF NOT EXISTS AIRBYTE_ROLE;

CREATE USER IF NOT EXISTS AIRBYTE_USER
  PASSWORD = '-password-'
  DEFAULT_ROLE = AIRBYTE_ROLE
  DEFAULT_WAREHOUSE = AIRBYTE_WAREHOUSE;

GRANT ROLE AIRBYTE_ROLE TO USER AIRBYTE_USER;

-- let the role run queries
GRANT USAGE ON WAREHOUSE AIRBYTE_WAREHOUSE TO ROLE AIRBYTE_ROLE;

-- let the role read the data you want to replicate
GRANT USAGE ON DATABASE AIRBYTE_DATABASE TO ROLE AIRBYTE_ROLE;
GRANT USAGE ON SCHEMA AIRBYTE_DATABASE.AIRBYTE_SCHEMA TO ROLE AIRBYTE_ROLE;
GRANT SELECT ON ALL TABLES IN SCHEMA AIRBYTE_DATABASE.AIRBYTE_SCHEMA TO ROLE AIRBYTE_ROLE;
GRANT SELECT ON FUTURE TABLES IN SCHEMA AIRBYTE_DATABASE.AIRBYTE_SCHEMA TO ROLE AIRBYTE_ROLE;
GRANT SELECT ON ALL VIEWS IN SCHEMA AIRBYTE_DATABASE.AIRBYTE_SCHEMA TO ROLE AIRBYTE_ROLE;
GRANT SELECT ON FUTURE VIEWS IN SCHEMA AIRBYTE_DATABASE.AIRBYTE_SCHEMA TO ROLE AIRBYTE_ROLE;
```

These grants are everything the connector needs: it reads tables and views and never writes to your warehouse. The `FUTURE` grants keep new tables and views readable, so you don't have to re-grant after schema changes. Repeat the schema-level grants for every schema you want to replicate. To replicate from more than one database, create a separate source for each one.

For more about this pattern, see Snowflake's guide to [creating custom read-only roles](https://docs.snowflake.com/en/user-guide/security-access-control-configure#creating-custom-read-only-roles).

Your database user should now be ready for use with Airbyte.

### Authentication

Source Snowflake supports the following authentication methods:

- Username and password
- Key pair authentication
- Programmatic access token

#### Username and password

| Field                                                                                                 | Description                                                                                                                                                                                       |
| ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Host](https://docs.snowflake.com/en/user-guide/admin-account-identifier.html)                        | The host domain of the snowflake instance (must include the account, region, cloud environment, and end with snowflakecomputing.com). Example: `accountname.us-east-2.aws.snowflakecomputing.com` |
| [Role](https://docs.snowflake.com/en/user-guide/security-access-control-overview.html#roles)          | The role you created for Airbyte to access Snowflake. Example: `AIRBYTE_ROLE`                                                                                                           |
| [Warehouse](https://docs.snowflake.com/en/user-guide/warehouses-overview.html#overview-of-warehouses) | The warehouse Airbyte runs its queries in. Example: `AIRBYTE_WAREHOUSE`                                                                                                   |
| [Database](https://docs.snowflake.com/en/sql-reference/ddl-database.html#database-schema-share-ddl)   | The database Airbyte reads data from. Example: `AIRBYTE_DATABASE`                                                                                                     |
| [Schema](https://docs.snowflake.com/en/sql-reference/ddl-database.html#database-schema-share-ddl) (Optional) | The schema whose tables this replication is targeting. If no schema is specified, all tables with permission will be presented regardless of their schema.                                        |
| Username                                                                                              | The username you created to allow Airbyte to access the database. Example: `AIRBYTE_USER`                                                                                               |
| Password                                                                                              | The password associated with the username.                                                                                                                                                        |
| [JDBC URL Params](https://docs.snowflake.com/en/user-guide/jdbc-parameters.html) (Optional)           | Additional properties to pass to the JDBC URL string when connecting to the database formatted as `key=value` pairs separated by the symbol `&`. Example: `key1=value1&key2=value2&key3=value3`   |

#### Key pair authentication

 <KeypairExample/>

#### Programmatic access token authentication

To authenticate with a Snowflake [programmatic access token](https://docs.snowflake.com/en/user-guide/programmatic-access-tokens), select **Programmatic Access Token** as the authorization method and provide the token. A username is not required; the token identifies the Snowflake user it was created for.

Create a programmatic access token in Snowflake with:

```sql
ALTER USER <user_name> ADD PROGRAMMATIC ACCESS TOKEN <token_name>
  ROLE_RESTRICTION = '<airbyte_role>'
  DAYS_TO_EXPIRY = <days>;
```

The token secret is only shown when the token is created. Store it securely before closing the result.

For service users, Snowflake requires `ROLE_RESTRICTION` by default. Snowflake also requires a network policy for service users to generate or use programmatic access tokens unless your authentication policy changes this behavior. If an authentication policy restricts allowed methods, include `PROGRAMMATIC_ACCESS_TOKEN` in `AUTHENTICATION_METHODS`.

:::note Network policy required for Programmatic Access Token authentication
When using Programmatic Access Token authentication, the Snowflake user's network policy must allow connections from Airbyte's IP addresses. Add the [Airbyte Cloud IP addresses](/platform/operating-airbyte/ip-allowlist) to the network policy attached to the PAT user, or to the account-level network policy.
:::

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

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                                   |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------|
| 1.1.2   | 2026-08-21 | [84927](https://github.com/airbytehq/airbyte/pull/84927) | Bump Bulk CDK extract version from 1.0.1 to 1.1.10                                                                                        |
| 1.1.1   | 2026-08-12 | [82705](https://github.com/airbytehq/airbyte/pull/82705) | Fix incremental sync silently dropping rows at the cursor's upper bound by rounding timestamp precision up instead of down                |
| 1.1.0   | 2026-05-28 | [78481](https://github.com/airbytehq/airbyte/pull/78481) | Support Snowflake Programmatic Access Token authentication.                                                                               |
| 1.0.11  | 2026-05-06 | [77787](https://github.com/airbytehq/airbyte/pull/77787) | Make the hidden additional properties fields in spec optional. No functional change.                                                      |
| 1.0.10  | 2026-03-18 | [74834](https://github.com/airbytehq/airbyte/pull/74834) | Truncate timestamp precision to 6 digits (microseconds) to prevent precision errors in destinations                                       |
| 1.0.9   | 2026-03-02 | [74081](https://github.com/airbytehq/airbyte/pull/74081) | Security update                                                                                                                           |
| 1.0.8   | 2025-09-16 | [66311](https://github.com/airbytehq/airbyte/pull/66311) | Change CDK version to 0.1.31                                                                                                              |
| 1.0.7   | 2025-09-15 | [66200](https://github.com/airbytehq/airbyte/pull/66200) | Fix sampling bug for DefaultJdbcCursorIncrementalPartition                                                                                |
| 1.0.6   | 2025-09-12 | [66226](https://github.com/airbytehq/airbyte/pull/66226) | Fix schema filtering functionality in versions 1.0.0+ - resolves "discovered zero tables" error and enables proper schema-level filtering |
| 1.0.5   | 2025-07-28 | [63780](https://github.com/airbytehq/airbyte/pull/63780) | Fix ts data type for snowflake                                                                                                            |
| 1.0.3   | 2025-07-22 | [63713](https://github.com/airbytehq/airbyte/pull/63713) | Revert base image from 2.0.3 to 2.0.2 to fix SSL certificate errors                                                                       |
| 1.0.2   | 2025-07-15 | [62939](https://github.com/airbytehq/airbyte/pull/62939) | Update base image to 2.0.3                                                                                                                |
| 1.0.1   | 2025-07-11 | [62929](https://github.com/airbytehq/airbyte/pull/62929) | Update test dependencies                                                                                                                  |
| 1.0.0   | 2025-07-09 | [61535](https://github.com/airbytehq/airbyte/pull/61535) | Replace community support connector with Airbyte certified connector                                                                      |
| 0.3.6   | 2025-01-13 | [51504](https://github.com/airbytehq/airbyte/pull/51504) | Use a non root base image                                                                                                                 |
| 0.3.5   | 2025-01-06 | [49911](https://github.com/airbytehq/airbyte/pull/49911) | Use a base image: airbyte/java-connector-base:1.0.0                                                                                       |
| 0.3.4   | 2024-10-31 | [48073](https://github.com/airbytehq/airbyte/pull/48073) | Upgrade jdbc driver                                                                                                                       |
| 0.3.3   | 2024-07-09 | [40424](https://github.com/airbytehq/airbyte/pull/40424) | Support Snowflake key pair authentication                                                                                                 |
| 0.3.2   | 2024-05-17 | [38317](https://github.com/airbytehq/airbyte/pull/38317) | Hide oAuth option from connector                                                                                                          |
| 0.3.1   | 2024-02-14 | [35220](https://github.com/airbytehq/airbyte/pull/35220) | Adopt CDK 0.20.4                                                                                                                          |
| 0.3.1   | 2024-02-01 | [34453](https://github.com/airbytehq/airbyte/pull/34453) | bump CDK version                                                                                                                          |
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
