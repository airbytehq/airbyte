import KeypairExample from '@site/static/_snowflake_keypair_generation.md';

# Snowflake

## Overview

The Snowflake source syncs tables and views from Snowflake. It supports Full Refresh and Incremental syncs, so you can copy all selected rows on every sync or only rows newer than the last cursor value.

This Snowflake source connector is built on top of the source-jdbc code base and is configured to rely on JDBC 3.23.1 [Snowflake driver](https://github.com/snowflakedb/snowflake-jdbc) as described in the Snowflake [documentation](https://docs.snowflake.com/en/user-guide/jdbc.html).

### Resulting schema

The Snowflake source does not alter the schema present in your warehouse. Depending on the destination connected to this source, however, the result schema may be altered. See the destination's documentation for more details.

### Features

| Feature                   | Supported?\(Yes/No\) | Notes |
| :------------------------ | :------------------- | :---- |
| Full Refresh Sync         | Yes                  |       |
| Incremental - Append Sync | Yes                  |       |
| Namespaces                | Yes                  |       |

## Incremental sync

The Snowflake source connector supports incremental sync, which replicates only new or updated data since the last sync. This is accomplished using a cursor field that tracks the state of the sync.

### How incremental sync works

During incremental sync, the connector:

1. Identifies new records using a `WHERE cursor_field > last_cursor_value` clause.
2. Maintains order using `ORDER BY cursor_field ASC`.
3. Tracks state by storing the maximum cursor value from each sync to use as the starting point for the next sync.

### Supported cursor field data types

The connector supports the following JDBC data types as cursor fields:

**Date and time types:**

- `TIMESTAMP_WITH_TIMEZONE`
- `TIMESTAMP`
- `TIME_WITH_TIMEZONE`
- `TIME`
- `DATE`

**Numeric types:**

- `TINYINT`
- `SMALLINT`
- `INTEGER`
- `BIGINT`
- `FLOAT`
- `DOUBLE`
- `REAL`
- `NUMERIC`
- `DECIMAL`

**String types:**

- `NVARCHAR`
- `VARCHAR`
- `LONGVARCHAR`

### Choosing a cursor field

For effective incremental sync, choose cursor fields that:

- Are monotonically increasing, such as auto-incrementing IDs or creation timestamps.
- Are never updated after record creation.
- Have unique values. The connector handles duplicate cursor values, but duplicates can cause records to be skipped or synced again.
- Are indexed for better query performance on large tables.

Good cursor field examples:

- `CREATED_AT` or `UPDATED_AT` timestamp columns
- Auto-incrementing `ID` columns
- Sequence-generated numeric fields

Avoid using:

- Fields that can be updated after creation
- Fields with many duplicate values
- Fields that can contain `NULL` values

### Snowflake-specific considerations

**Timezone handling**: The connector provides special handling for Snowflake's `TIMESTAMPLTZ` (timestamp with local timezone) data type, automatically converting it to `TIMESTAMP_WITH_TIMEZONE` for consistent processing.

**Data type precision**: Snowflake's numeric types maintain their precision during sync. Ensure your destination can handle the precision of your cursor fields.

### Configure incremental sync

To set up incremental sync in Airbyte:

1. Create or edit your connection in the Airbyte UI.
2. Select the source tables to sync incrementally.
3. Choose **Incremental | Append** sync mode for each table.
4. Select a cursor field from the list of available fields.
5. Verify the cursor field meets the criteria listed in [Choosing a cursor field](#choosing-a-cursor-field).

The Airbyte UI will automatically validate that your chosen cursor field is compatible with incremental sync and will show you the supported data types for your specific table schema.

### Troubleshooting Incremental Sync

**Cursor field validation errors**: If you receive an error about an invalid cursor field, ensure the field exists in your table and uses one of the supported data types.

**Duplicate cursor values**: When multiple records have the same cursor value, the connector processes all records with that value. This might result in some records syncing multiple times across different sync runs.

**`NULL` cursor values**: Records with `NULL` cursor field values are excluded from incremental sync. Ensure your cursor field has a `NOT NULL` constraint or default value.

**State reset**: If you need to re-sync all data, you can reset the connection's state in the Airbyte UI, which will cause the next sync to behave like a full refresh.

## Getting started

### Requirements

You'll need the following information to configure the Snowflake source:

1. **Host**
2. **Role**
3. **Warehouse**
4. **Database**
5. **Schema**
6. **Username**, unless you use programmatic access token authentication
7. **Password**, private key, or programmatic access token
8. **JDBC URL Params** (Optional)

Additionally, create a dedicated read-only Airbyte user and role with access to all schemas needed for replication.

### Setup guide

#### Connection parameters

Additional information about Snowflake connection parameters can be found in the [Snowflake documentation](https://docs.snowflake.com/en/user-guide/jdbc-configure.html#connection-parameters).

#### Create a dedicated read-only user (recommended but optional)

This step is optional but highly recommended for better permission control and auditing. Alternatively, you can use Airbyte with an existing user in your database.

To create a dedicated database user with read-only access to a single database and schema, run the following commands against your database:

```sql
-- set variables (these need to be uppercase)
SET AIRBYTE_ROLE = 'AIRBYTE_ROLE';
SET AIRBYTE_USERNAME = 'AIRBYTE_USER';
SET AIRBYTE_WAREHOUSE = 'AIRBYTE_WAREHOUSE';
SET AIRBYTE_DATABASE = 'AIRBYTE_DATABASE';
SET AIRBYTE_SCHEMA = 'AIRBYTE_SCHEMA';

-- set user password
SET AIRBYTE_PASSWORD = '-password-';

BEGIN;

-- create Airbyte role
CREATE ROLE IF NOT EXISTS $AIRBYTE_ROLE;

-- create Airbyte user
CREATE USER IF NOT EXISTS $AIRBYTE_USERNAME
PASSWORD = $AIRBYTE_PASSWORD
DEFAULT_ROLE = $AIRBYTE_ROLE
DEFAULT_WAREHOUSE = $AIRBYTE_WAREHOUSE;

-- grant Airbyte access to the warehouse, database, schema, tables, and views
USE DATABASE $AIRBYTE_DATABASE;
GRANT USAGE ON WAREHOUSE $AIRBYTE_WAREHOUSE TO ROLE $AIRBYTE_ROLE;
GRANT USAGE ON DATABASE $AIRBYTE_DATABASE TO ROLE $AIRBYTE_ROLE;
GRANT USAGE ON SCHEMA $AIRBYTE_SCHEMA TO ROLE $AIRBYTE_ROLE;
GRANT SELECT ON ALL TABLES IN SCHEMA $AIRBYTE_SCHEMA TO ROLE $AIRBYTE_ROLE;
GRANT SELECT ON FUTURE TABLES IN SCHEMA $AIRBYTE_SCHEMA TO ROLE $AIRBYTE_ROLE;
GRANT SELECT ON ALL VIEWS IN SCHEMA $AIRBYTE_SCHEMA TO ROLE $AIRBYTE_ROLE;
GRANT SELECT ON FUTURE VIEWS IN SCHEMA $AIRBYTE_SCHEMA TO ROLE $AIRBYTE_ROLE;

GRANT ROLE $AIRBYTE_ROLE TO USER $AIRBYTE_USERNAME;

COMMIT;
```

To replicate multiple schemas in the same database, repeat the schema, table, and view grants for each schema. To replicate data from multiple Snowflake databases, set up one source for each database.

Your database user should now be ready for use with Airbyte.

### Authentication

The Snowflake source supports the following authentication methods:

- Username and password
- Key pair authentication
- Programmatic access token

The following fields are common to all authentication methods:

| Field | Description |
| :--- | :--- |
| [Host](https://docs.snowflake.com/en/user-guide/admin-account-identifier.html) | The host domain of the Snowflake instance. Include the account, region, cloud environment, and `snowflakecomputing.com`. Example: `accountname.us-east-2.aws.snowflakecomputing.com`. |
| [Role](https://docs.snowflake.com/en/user-guide/security-access-control-overview.html#roles) | The role you created for Airbyte to access Snowflake. Example: `AIRBYTE_ROLE`. |
| [Warehouse](https://docs.snowflake.com/en/user-guide/warehouses-overview.html#overview-of-warehouses) | The warehouse you created for Airbyte to access data. Example: `AIRBYTE_WAREHOUSE`. |
| [Database](https://docs.snowflake.com/en/sql-reference/ddl-database.html#database-schema-share-ddl) | The database to sync. Example: `AIRBYTE_DATABASE`. |
| [Schema](https://docs.snowflake.com/en/sql-reference/ddl-database.html#database-schema-share-ddl) | Optional. The schema to sync. If no schema is specified, the connector discovers all schemas the role can access in the configured database. |
| [JDBC URL Params](https://docs.snowflake.com/en/user-guide/jdbc-parameters.html) | Optional. Additional properties to pass to the JDBC URL string, formatted as `key=value` pairs separated by `&`. Example: `key1=value1&key2=value2&key3=value3`. |

#### Username and password

Use username and password authentication when your Snowflake user authenticates with a password.

| Field | Description |
| :--- | :--- |
| Username | The username you created to allow Airbyte to access the database. Example: `AIRBYTE_USER`. |
| Password | The password associated with the username. |

#### Key pair authentication

 <KeypairExample/>

#### Programmatic access token authentication

To authenticate with a Snowflake [programmatic access token](https://docs.snowflake.com/en/user-guide/programmatic-access-tokens), select **Programmatic Access Token** as the authorization method and provide the token. Don't provide a username for this authentication method. The token identifies the Snowflake user it was created for.

Create a programmatic access token in Snowflake with:

```sql
ALTER USER <user_name> ADD PROGRAMMATIC ACCESS TOKEN <token_name>
  ROLE_RESTRICTION = '<airbyte_role>'
  DAYS_TO_EXPIRY = <days>;
```

The token secret is shown only when the token is created. Store it securely before closing the result.

Snowflake programmatic access tokens have the following requirements:

- The token role must have the same read privileges described in [Create a dedicated read-only user](#create-a-dedicated-read-only-user-recommended-but-optional). If you set `ROLE_RESTRICTION`, set it to the Airbyte role.
- Snowflake requires a network policy for service users to generate or use programmatic access tokens unless your authentication policy changes this behavior.
- For human users, Snowflake can generate a token without a network policy, but the user must be subject to a network policy to authenticate with the token unless your authentication policy changes this behavior.
- If an authentication policy restricts allowed methods, include `PROGRAMMATIC_ACCESS_TOKEN` in `AUTHENTICATION_METHODS`.

:::note Network policy required for Programmatic Access Token authentication
When using Programmatic Access Token authentication, the Snowflake user's network policy must allow connections from Airbyte's IP addresses. Add the [Airbyte Cloud IP addresses](/platform/operating-airbyte/ip-allowlist) to the network policy attached to the PAT user, or to the account-level network policy.
:::

### Network policies

By default, Snowflake allows users to connect to the service from any computer or device IP address. A security administrator (i.e. users with the SECURITYADMIN role) or higher can create a network policy to allow or deny access to a single IP address or a list of addresses.

If you have any issues connecting with Airbyte Cloud, please make sure that the list of IP addresses is on the allowed list.

To determine whether a network policy is set on your account or for a specific user, execute the _SHOW PARAMETERS_ command.

Account:

```sql
SHOW PARAMETERS LIKE 'network_policy' IN ACCOUNT;
```

User:

```sql
SHOW PARAMETERS LIKE 'network_policy' IN USER <username>;
```

To read more, please check the official [Snowflake documentation](https://docs.snowflake.com/en/user-guide/network-policies.html#).

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Reference

This connector uses the [Snowflake JDBC driver](https://docs.snowflake.com/en/developer-guide/jdbc/jdbc-configure). Requests use the Snowflake host you provide in the connector configuration.

For programmatic configuration, use these parameter names:

| Field | Required | Description |
| :--- | :---: | :--- |
| `credentials.auth_type` | Yes | Authentication method. Valid values are `username/password`, `Key Pair Authentication`, and `Programmatic Access Token`. |
| `credentials.username` | Required for username/password and key pair authentication | Snowflake username. |
| `credentials.password` | Required for username/password authentication | Snowflake password. |
| `credentials.private_key` | Required for key pair authentication | RSA private key for the Snowflake user. |
| `credentials.private_key_password` | No | Passphrase for the private key, if the private key is encrypted. |
| `credentials.programmatic_access_token` | Required for programmatic access token authentication | Snowflake programmatic access token. |
| `host` | Yes | Snowflake host domain, including account, region, cloud environment, and `snowflakecomputing.com`. |
| `role` | Yes | Role Airbyte uses to access Snowflake. |
| `warehouse` | Yes | Warehouse Airbyte uses to query Snowflake. |
| `database` | Yes | Database to sync. |
| `schema` | No | Schema to sync. If unset, the connector discovers all schemas the role can access in the configured database. |
| `jdbc_url_params` | No | Additional JDBC URL parameters as `key=value` pairs separated by `&`. |
| `checkpoint_target_interval_seconds` | No | How often, in seconds, a stream should checkpoint when possible. Defaults to `300`. |
| `concurrency` | No | Maximum number of concurrent queries to Snowflake. Defaults to `1`. |
| `check_privileges` | No | Whether discovery checks table and column access privileges and removes inaccessible objects. Defaults to `true`. |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 1.1.0 | 2026-05-28 | [78481](https://github.com/airbytehq/airbyte/pull/78481) | Support Snowflake Programmatic Access Token authentication. |
| 1.0.11 | 2026-05-06 | [77787](https://github.com/airbytehq/airbyte/pull/77787) | Make the hidden additional properties fields in spec optional. No functional change. |
| 1.0.10 | 2026-03-18 | [74834](https://github.com/airbytehq/airbyte/pull/74834) | Truncate timestamp precision to 6 digits (microseconds) to prevent precision errors in destinations |
| 1.0.9 | 2026-03-02 | [74081](https://github.com/airbytehq/airbyte/pull/74081) | Security update |
| 1.0.8 | 2025-09-16 | [66311](https://github.com/airbytehq/airbyte/pull/66311) | Change CDK version to 0.1.31 |
| 1.0.7 | 2025-09-16 | [66200](https://github.com/airbytehq/airbyte/pull/66200) | Fix sampling bug for DefaultJdbcCursorIncrementalPartition |
| 1.0.6 | 2025-09-12 | [66226](https://github.com/airbytehq/airbyte/pull/66226) | Fix schema filtering functionality in versions 1.0.0+ - resolves "discovered zero tables" error and enables proper schema-level filtering |
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
| 0.1.29 | 2022-12-14 | [20346](https://github.com/airbytehq/airbyte/pull/20346) | Consolidate date/time values mapping for JDBC sources. |
| 0.1.28 | 2023-01-06 | [20465](https://github.com/airbytehq/airbyte/pull/20465) | Improve the schema config field to only discover tables from the specified scehma and make the field optional |
| 0.1.27 | 2022-12-14 | [20407](https://github.com/airbytehq/airbyte/pull/20407) | Fix an issue with integer values converted to floats during replication |
| 0.1.26 | 2022-11-10 | [19314](https://github.com/airbytehq/airbyte/pull/19314) | Set application id in JDBC URL params based on OSS/Cloud environment |
| 0.1.25 | 2022-11-10 | [15535](https://github.com/airbytehq/airbyte/pull/15535) | Update incremental query to avoid data missing when new data is inserted at the same time as a sync starts under non-CDC incremental mode |
| 0.1.24 | 2022-09-26 | [17144](https://github.com/airbytehq/airbyte/pull/17144) | Fixed bug with incorrect date-time datatypes handling |
| 0.1.23 | 2022-09-26 | [17116](https://github.com/airbytehq/airbyte/pull/17116) | added connection string identifier |
| 0.1.22 | 2022-09-21 | [16766](https://github.com/airbytehq/airbyte/pull/16766) | Update JDBC Driver version to 3.13.22 |
| 0.1.21 | 2022-09-14 | [15668](https://github.com/airbytehq/airbyte/pull/15668) | Wrap logs in AirbyteLogMessage |
| 0.1.20 | 2022-09-01 | [16258](https://github.com/airbytehq/airbyte/pull/16258) | Emit state messages more frequently |
| 0.1.19 | 2022-08-19 | [15797](https://github.com/airbytehq/airbyte/pull/15797) | Allow using role during oauth |
| 0.1.18 | 2022-08-18 | [14356](https://github.com/airbytehq/airbyte/pull/14356) | DB Sources: only show a table can sync incrementally if at least one column can be used as a cursor field |
| 0.1.17 | 2022-08-09 | [15314](https://github.com/airbytehq/airbyte/pull/15314) | Discover integer columns as integers rather than floats |
| 0.1.16 | 2022-08-04 | [15314](https://github.com/airbytehq/airbyte/pull/15314) | (broken, do not use) Discover integer columns as integers rather than floats |
| 0.1.15 | 2022-07-22 | [14828](https://github.com/airbytehq/airbyte/pull/14828) | Source Snowflake: Source/Destination doesn't respect DATE data type |
| 0.1.14 | 2022-07-22 | [14714](https://github.com/airbytehq/airbyte/pull/14714) | Clarified error message when invalid cursor column selected |
| 0.1.13 | 2022-07-14 | [14574](https://github.com/airbytehq/airbyte/pull/14574) | Removed additionalProperties:false from JDBC source connectors |
| 0.1.12 | 2022-04-29 | [12480](https://github.com/airbytehq/airbyte/pull/12480) | Query tables with adaptive fetch size to optimize JDBC memory consumption |
| 0.1.11 | 2022-04-27 | [10953](https://github.com/airbytehq/airbyte/pull/10953) | Implement OAuth flow |
| 0.1.9 | 2022-02-21 | [10242](https://github.com/airbytehq/airbyte/pull/10242) | Fixed cursor for old connectors that use non-microsecond format. Now connectors work with both formats |
| 0.1.8 | 2022-02-18 | [10242](https://github.com/airbytehq/airbyte/pull/10242) | Updated timestamp transformation with microseconds |
| 0.1.7 | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256) | Add `-XX:+ExitOnOutOfMemoryError` JVM option |
| 0.1.6 | 2022-01-25 | [9623](https://github.com/airbytehq/airbyte/pull/9623) | Add jdbc_url_params support for optional JDBC parameters |
| 0.1.5 | 2022-01-19 | [9567](https://github.com/airbytehq/airbyte/pull/9567) | Added parameter for keeping JDBC session alive |
| 0.1.4 | 2021-12-30 | [9203](https://github.com/airbytehq/airbyte/pull/9203) | Update connector fields title/description |
| 0.1.3 | 2021-01-11 | [9304](https://github.com/airbytehq/airbyte/pull/9304) | Upgrade version of JDBC driver |
| 0.1.2 | 2021-10-21 | [7257](https://github.com/airbytehq/airbyte/pull/7257) | Fixed parsing of extreme values for FLOAT and NUMBER data types |
| 0.1.1 | 2021-08-13 | [4699](https://github.com/airbytehq/airbyte/pull/4699) | Added json config validator |

</details>
