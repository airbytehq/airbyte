import KeypairExample from '@site/static/_snowflake_keypair_generation.md';

# Snowflake

:::danger Username and Password Authentication Deprecated
Starting with version **2.0.0**, username and password authentication is **deprecated** and will be removed in a future release. **Key pair authentication** or a **programmatic access token** is now the recommended method for connecting to Snowflake.

This change aligns with [Snowflake's deprecation of single-factor password sign-ins](https://docs.snowflake.com/en/user-guide/security-mfa-rollout). Snowflake is enforcing strong authentication for all users on a rolling per-account basis between **August and October 2026**; once enforced on your account, password-only logins from Airbyte will fail.

If you are currently using username and password authentication, see the [Snowflake Migration Guide](./snowflake-migrations.md) for instructions on migrating to key pair authentication or a programmatic access token.
:::

## Overview

The Snowflake source allows you to sync data from Snowflake. It supports both Full Refresh and Incremental syncs. You can choose whether this connector will copy only new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This connector connects to Snowflake with the [Snowflake JDBC driver](https://github.com/snowflakedb/snowflake-jdbc) (version 4.0.2), as described in the Snowflake [JDBC documentation](https://docs.snowflake.com/en/user-guide/jdbc.html). It discovers both tables and views in the configured database, skipping the `INFORMATION_SCHEMA`, `SNOWFLAKE_SAMPLE_DATA`, and `UTIL_DB` schemas.

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

At the start of each sync, the connector queries the current maximum value of the cursor column (`SELECT MAX(cursor_field)`) and uses it as the upper bound for that sync. It then reads rows where the cursor value is greater than or equal to the last checkpointed value and less than or equal to that upper bound, ordered by the cursor column. When the sync finishes, the upper bound becomes the starting point for the next sync. Because the lower bound is inclusive, rows whose cursor value equals the previous sync's upper bound are read again on the next sync; this makes sure that rows added with that same cursor value after the previous sync aren't missed.

The first sync of a stream reads the whole table. If the table has a primary key, the connector checkpoints its progress by primary key during this initial read so that an interrupted sync can resume where it left off.

### Supported Cursor Field Data Types

You can use a column of any of the following Snowflake data types as a cursor field:

**Date and Time Types:**

- `DATE`
- `TIME`
- `TIMESTAMP_NTZ` (also `TIMESTAMP` and `DATETIME`)
- `TIMESTAMP_LTZ`
- `TIMESTAMP_TZ`

**Numeric Types:**

- `NUMBER` (also `DECIMAL` and `NUMERIC`)
- `INT`, `INTEGER`, `BIGINT`, `SMALLINT`, `TINYINT`, `BYTEINT`
- `FLOAT`, `FLOAT4`, `FLOAT8`, `DOUBLE`, `DOUBLE PRECISION`, `REAL`

**String Types:**

- `VARCHAR` (also `CHAR`, `CHARACTER`, `STRING`, and `TEXT`)

`BOOLEAN` columns can't be used as a cursor.

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

**Timezone Handling**: The connector reads `TIMESTAMP_LTZ` and `TIMESTAMP_TZ` columns as timestamps with time zone, expressed in UTC. `TIMESTAMP_NTZ` columns are read as timestamps without time zone.

**Timestamp Precision**: Snowflake timestamps can have up to 9 fractional digits (nanoseconds), but Airbyte supports 6 (microseconds). The connector rounds timestamps up to the nearest microsecond. Rounding up rather than down means that a row whose timestamp falls between the truncated cursor value and the true value is not skipped by the next sync.

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

**Duplicate cursor values**: When multiple records have the same cursor value, the connector processes all records with that value. Records whose cursor value equals the last checkpointed value are re-synced on the next run, so expect some duplicate records in an Incremental | Append destination.

**NULL cursor values**: Records with NULL cursor field values are excluded from incremental sync. Ensure your cursor field has a NOT NULL constraint or default value.

**State reset**: If you need to re-sync all data, you can reset the connection's state in the Airbyte UI, which will cause the next sync to behave like a full refresh.

## Data type mapping

| Snowflake type                                                             | Airbyte type                  | Notes                                                                  |
| :------------------------------------------------------------------------- | :---------------------------- | :--------------------------------------------------------------------- |
| `VARCHAR`, `CHAR`, `CHARACTER`, `STRING`, `TEXT`                           | string                        |                                                                        |
| `BOOLEAN`                                                                  | boolean                       |                                                                        |
| `NUMBER`, `DECIMAL`, `NUMERIC`                                             | number                        | Precision is preserved.                                                |
| `INT`, `INTEGER`, `BIGINT`, `SMALLINT`, `TINYINT`, `BYTEINT`               | integer                       |                                                                        |
| `FLOAT`, `FLOAT4`, `FLOAT8`, `DOUBLE`, `DOUBLE PRECISION`, `REAL`          | number                        |                                                                        |
| `DATE`                                                                     | date                          |                                                                        |
| `TIME`                                                                     | time without time zone        |                                                                        |
| `TIMESTAMP_NTZ`, `TIMESTAMP`, `DATETIME`                                   | timestamp without time zone   | Rounded up to microsecond precision.                                   |
| `TIMESTAMP_LTZ`, `TIMESTAMP_TZ`                                            | timestamp with time zone      | Expressed in UTC. Rounded up to microsecond precision.                 |
| `BINARY`, `VARBINARY`                                                      | binary                        | Emitted as a Base64-encoded string.                                    |
| `VARIANT`, `OBJECT`, `ARRAY`, `GEOGRAPHY`, `GEOMETRY`, `VECTOR`, `FILE`    | string                        | Semi-structured and geospatial values are emitted as strings.          |

## Getting started

### Requirements

You'll need the following information to configure the Snowflake source:

1. **Host**
2. **Role**
3. **Warehouse**
4. **Database**
5. **Schema** (Optional)
6. **Username** (not required for programmatic access token authentication)
7. **Private key or programmatic access token** (password authentication is deprecated but still supported)
8. **JDBC URL Params** (Optional)

Additionally, create a dedicated read-only Airbyte service user and role with access to all schemas needed for replication.

### Setup guide

#### Connection parameters

Additional information about Snowflake connection parameters can be found in the [Snowflake documentation](https://docs.snowflake.com/en/user-guide/jdbc-configure.html#connection-parameters).

#### Create a dedicated read-only user (Recommended but optional)

This step is optional but highly recommended for better permission control and auditing. Alternatively, you can use Airbyte with an existing user in your database.

To create a dedicated database user, first generate a key pair as described in [Key pair authentication](#key-pair-authentication), then run the following commands in Snowflake using a role that can create users and roles and grant privileges on the source objects (for example, `ACCOUNTADMIN`, or `SECURITYADMIN` combined with the owner of the source database). Replace the variable values with your own names, and replace `<public_key_value>` with the contents of your `rsa_key.pub` file, excluding the `-----BEGIN PUBLIC KEY-----` and `-----END PUBLIC KEY-----` header/footer lines.

```sql
-- set variables (these need to be uppercase)
SET AIRBYTE_ROLE = 'AIRBYTE_ROLE';
SET AIRBYTE_USERNAME = 'AIRBYTE_USER';
SET AIRBYTE_WAREHOUSE = 'AIRBYTE_WAREHOUSE';
SET AIRBYTE_DATABASE = 'AIRBYTE_DATABASE';
SET AIRBYTE_SCHEMA = 'AIRBYTE_DATABASE.AIRBYTE_SCHEMA';

BEGIN;

-- create Airbyte role
CREATE ROLE IF NOT EXISTS IDENTIFIER($AIRBYTE_ROLE);

-- create Airbyte service user with key pair authentication
CREATE USER IF NOT EXISTS IDENTIFIER($AIRBYTE_USERNAME)
TYPE = SERVICE
DEFAULT_ROLE = $AIRBYTE_ROLE
DEFAULT_WAREHOUSE = $AIRBYTE_WAREHOUSE;

-- assign the RSA public key to the service user
ALTER USER IDENTIFIER($AIRBYTE_USERNAME) SET RSA_PUBLIC_KEY='<public_key_value>';

-- grant the role to the user
GRANT ROLE IDENTIFIER($AIRBYTE_ROLE) TO USER IDENTIFIER($AIRBYTE_USERNAME);

-- allow the role to run queries on the warehouse
GRANT USAGE ON WAREHOUSE IDENTIFIER($AIRBYTE_WAREHOUSE) TO ROLE IDENTIFIER($AIRBYTE_ROLE);

-- grant read-only access to the source database and schema
GRANT USAGE ON DATABASE IDENTIFIER($AIRBYTE_DATABASE) TO ROLE IDENTIFIER($AIRBYTE_ROLE);
GRANT USAGE ON SCHEMA IDENTIFIER($AIRBYTE_SCHEMA) TO ROLE IDENTIFIER($AIRBYTE_ROLE);
GRANT SELECT ON ALL TABLES IN SCHEMA IDENTIFIER($AIRBYTE_SCHEMA) TO ROLE IDENTIFIER($AIRBYTE_ROLE);
GRANT SELECT ON ALL VIEWS IN SCHEMA IDENTIFIER($AIRBYTE_SCHEMA) TO ROLE IDENTIFIER($AIRBYTE_ROLE);

-- also cover tables and views created later
GRANT SELECT ON FUTURE TABLES IN SCHEMA IDENTIFIER($AIRBYTE_SCHEMA) TO ROLE IDENTIFIER($AIRBYTE_ROLE);
GRANT SELECT ON FUTURE VIEWS IN SCHEMA IDENTIFIER($AIRBYTE_SCHEMA) TO ROLE IDENTIFIER($AIRBYTE_ROLE);

COMMIT;
```

Repeat the schema grants for every schema you want to replicate. A single source connects to one database; to replicate data from multiple Snowflake databases, set up one source per database. If you leave the **Schema** field empty when configuring the source, the connector discovers tables from every schema in the database that the role can access.

Your database user should now be ready for use with Airbyte.

### Authentication

Source Snowflake supports the following authentication methods:

- Key pair authentication (recommended)
- Programmatic access token
- Username and password (deprecated, see the [migration guide](./snowflake-migrations.md))

#### Connection fields

The following fields are common to all authentication methods:

| Field                                                                                                 | Description                                                                                                                                                                                       |
| ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Host](https://docs.snowflake.com/en/user-guide/admin-account-identifier.html)                        | The host domain of the snowflake instance (must include the account, region, cloud environment, and end with snowflakecomputing.com). Example: `accountname.us-east-2.aws.snowflakecomputing.com` |
| [Role](https://docs.snowflake.com/en/user-guide/security-access-control-overview.html#roles)          | The role you created for Airbyte to access Snowflake. Example: `AIRBYTE_ROLE`                                                                                                                     |
| [Warehouse](https://docs.snowflake.com/en/user-guide/warehouses-overview.html#overview-of-warehouses) | The warehouse Airbyte uses to run its queries. Example: `AIRBYTE_WAREHOUSE`                                                                                                                       |
| [Database](https://docs.snowflake.com/en/sql-reference/ddl-database.html#database-schema-share-ddl)   | The database that contains the tables you want to replicate. Example: `AIRBYTE_DATABASE`                                                                                                          |
| [Schema](https://docs.snowflake.com/en/sql-reference/ddl-database.html#database-schema-share-ddl)     | The schema whose tables this replication is targeting. If no schema is specified, all tables with permission will be presented regardless of their schema.                                        |
| Username                                                                                              | The username you created to allow Airbyte to access the database. Example: `AIRBYTE_USER`. Not required for programmatic access token authentication.                                             |
| [JDBC URL Params](https://docs.snowflake.com/en/user-guide/jdbc-parameters.html) (Optional)           | Additional properties to pass to the JDBC URL string when connecting to the database formatted as `key=value` pairs separated by the symbol `&`. Example: `key1=value1&key2=value2&key3=value3`   |

The following optional fields control how the connector reads data:

| Field                                    | Description                                                                                                                                                                                                                                                             |
| ---------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Update Method                            | How incremental syncs detect changes. The only option is **Scan Changes with User Defined Cursor**, which uses the cursor column you choose when configuring the connection. See [Incremental Sync](#incremental-sync).                                                 |
| Checkpoint Target Time Interval          | How often, in seconds, the connector tries to checkpoint its progress during a sync. Default: `300`.                                                                                                                                                                    |
| Concurrency                              | The maximum number of queries the connector runs against Snowflake at the same time. Default: `1`.                                                                                                                                                                      |
| Check Table and Column Access Privileges | When enabled (the default), the connector queries each table and view individually during schema discovery and drops any tables, views, or columns the role can't read. In databases with many tables, this can make discovery slow. Disable it if discovery times out. |

#### Key pair authentication

 <KeypairExample/>

In the Airbyte UI, select **Key Pair Authentication** as the authorization method, enter the username, paste the full contents of your `rsa_key.p8` private key file (including the `-----BEGIN ... PRIVATE KEY-----` header and footer), and, if the key is encrypted, enter the passphrase.

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

#### Username and password (deprecated)

Username and password authentication is deprecated as of version 2.0.0 and will be removed in a future release. Existing sources that use it continue to work until Snowflake enforces strong authentication on your account. Follow the [migration guide](./snowflake-migrations.md) to switch to key pair authentication or a programmatic access token.

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
| 2.0.0   | 2026-09-03 | [85331](https://github.com/airbytehq/airbyte/pull/85331) | Deprecate username/password authentication; key pair authentication or a programmatic access token is now recommended. Username/password will be removed in a future release. |
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
