# Snowflake

Setting up the Snowflake destination connector involves setting up Snowflake entities (warehouse,
database, schema, user, and role) in the Snowflake console and configuring the Snowflake destination
connector using the Airbyte UI.

This page describes the step-by-step process of setting up the Snowflake destination connector.

## Prerequisites

- A Snowflake account with the
  [ACCOUNTADMIN](https://docs.snowflake.com/en/user-guide/security-access-control-considerations.html)
  role. If you don’t have an account with the `ACCOUNTADMIN` role, contact your Snowflake
  administrator to set one up for you.

### Network policies

By default, Snowflake allows users to connect to the service from any computer or device IP address.
A security administrator (i.e. users with the SECURITYADMIN role) or higher can create a network
policy to allow or deny access to a single IP address or a list of addresses.

If you have any issues connecting with Airbyte Cloud please make sure that the list of IP addresses
is on the allowed list

To determine whether a network policy is set on your account or for a specific user, execute the
_SHOW PARAMETERS_ command.

**Account**

```
SHOW PARAMETERS LIKE 'network_policy' IN ACCOUNT;
```

**User**

```
SHOW PARAMETERS LIKE 'network_policy' IN USER <username>;
```

To read more please check official
[Snowflake documentation](https://docs.snowflake.com/en/user-guide/network-policies.html#)

## Setup guide

### Step 1: Set up Airbyte-specific entities in Snowflake

To set up the Snowflake destination connector, you first need to create Airbyte-specific Snowflake
entities (a warehouse, database, schema, user, and role) with the `OWNERSHIP` permission to write
data into Snowflake, track costs pertaining to Airbyte, and control permissions at a granular level.

You can use the following script in a new
[Snowflake worksheet](https://docs.snowflake.com/en/user-guide/ui-worksheet.html) to create the
entities:

1.  [Log into your Snowflake account](https://www.snowflake.com/login/).
2.  Edit the following script to change the password to a more secure password and to change the
    names of other resources if you so desire.

    **Note:** Make sure you follow the
    [Snowflake identifier requirements](https://docs.snowflake.com/en/sql-reference/identifiers-syntax.html)
    while renaming the resources.

```sql
-- set variables (these need to be uppercase)
set airbyte_role = 'AIRBYTE_ROLE';
set airbyte_username = 'AIRBYTE_USER';
set airbyte_warehouse = 'AIRBYTE_WAREHOUSE';
set airbyte_database = 'AIRBYTE_DATABASE';
set airbyte_schema = 'AIRBYTE_SCHEMA';

-- set user password
set airbyte_password = 'password';

begin;

-- create Airbyte role
use role securityadmin;
create role if not exists identifier($airbyte_role);
grant role identifier($airbyte_role) to role SYSADMIN;

-- create Airbyte user
create user if not exists identifier($airbyte_username)
password = $airbyte_password
default_role = $airbyte_role
default_warehouse = $airbyte_warehouse;

grant role identifier($airbyte_role) to user identifier($airbyte_username);

-- change role to sysadmin for warehouse / database steps
use role sysadmin;

-- create Airbyte warehouse
create warehouse if not exists identifier($airbyte_warehouse)
warehouse_size = xsmall
warehouse_type = standard
auto_suspend = 60
auto_resume = true
initially_suspended = true;

-- create Airbyte database
create database if not exists identifier($airbyte_database);

-- grant Airbyte warehouse access
grant USAGE
on warehouse identifier($airbyte_warehouse)
to role identifier($airbyte_role);

-- grant Airbyte database access
grant OWNERSHIP
on database identifier($airbyte_database)
to role identifier($airbyte_role);

commit;

begin;

USE DATABASE identifier($airbyte_database);

-- create schema for Airbyte data
CREATE SCHEMA IF NOT EXISTS identifier($airbyte_schema);

commit;

begin;

-- grant Airbyte schema access
grant OWNERSHIP
on schema identifier($airbyte_schema)
to role identifier($airbyte_role);

commit;
```

3.  Run the script using the
    [Worksheet page](https://docs.snowflake.com/en/user-guide/ui-worksheet.html) or
    [Snowsight](https://docs.snowflake.com/en/user-guide/ui-snowsight-gs.html). Make sure to select
    the **All Queries** checkbox.

### Step 2: Set up a data loading method

Airbyte uses Snowflake’s
[Internal Stage](https://docs.snowflake.com/en/user-guide/data-load-local-file-system-create-stage.html)
to load data.

Make sure the database and schema have the `USAGE` privilege.

### Step 3: Set up Snowflake as a destination in Airbyte

Navigate to the Airbyte UI to set up Snowflake as a destination. You can authenticate using
username/password or key pair authentication:

### Login and Password

| Field                                                                                                 | Description                                                                                                                                                                                                                          |
| ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [Host](https://docs.snowflake.com/en/user-guide/admin-account-identifier.html)                        | The host domain of the snowflake instance (must include the account, region, cloud environment, and end with snowflakecomputing.com). Example: `accountname.us-east-2.aws.snowflakecomputing.com`                                    |
| [Role](https://docs.snowflake.com/en/user-guide/security-access-control-overview.html#roles)          | The role you created in Step 1 for Airbyte to access Snowflake. Example: `AIRBYTE_ROLE`                                                                                                                                              |
| [Warehouse](https://docs.snowflake.com/en/user-guide/warehouses-overview.html#overview-of-warehouses) | The warehouse you created in Step 1 for Airbyte to sync data into. Example: `AIRBYTE_WAREHOUSE`                                                                                                                                      |
| [Database](https://docs.snowflake.com/en/sql-reference/ddl-database.html#database-schema-share-ddl)   | The database you created in Step 1 for Airbyte to sync data into. Example: `AIRBYTE_DATABASE`                                                                                                                                        |
| [Schema](https://docs.snowflake.com/en/sql-reference/ddl-database.html#database-schema-share-ddl)     | The default schema used as the target schema for all statements issued from the connection that do not explicitly specify a schema name.                                                                                             |
| Username                                                                                              | The username you created in Step 1 to allow Airbyte to access the database. Example: `AIRBYTE_USER`                                                                                                                                  |
| Password                                                                                              | The password associated with the username.                                                                                                                                                                                           |
| [JDBC URL Params](https://docs.snowflake.com/en/user-guide/jdbc-parameters.html) (Optional)           | Additional properties to pass to the JDBC URL string when connecting to the database formatted as `key=value` pairs separated by the symbol `&`. Example: `key1=value1&key2=value2&key3=value3`                                      |
| Disable Final Tables (Optional)                                                                       | Disables writing final Typed tables See [output schema](#output-schema). WARNING! The data format in \_airbyte_data is likely stable but there are no guarantees that other metadata columns will remain the same in future versions |

### Key pair authentication

    In order to configure key pair authentication you will need a private/public key pair.
    If you do not have the key pair yet, you can generate one using openssl command line tool
    Use this command in order to generate an unencrypted private key file:

       `openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key.p8 -nocrypt`

    Alternatively, use this command to generate an encrypted private key file:

      `openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -v1 PBE-SHA1-RC4-128 -out rsa_key.p8`

    Once you have your private key, you need to generate a matching public key.
    You can do so with the following command:

      `openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub`

    Finally, you need to add the public key to your Snowflake user account.
    You can do so with the following SQL command in Snowflake:

      `alter user <user_name> set rsa_public_key=<public_key_value>;`

    and replace `<user_name>` with your user name and `<public_key_value>` with your public key.

## Output schema

Airbyte outputs each stream into its own raw table in `airbyte_internal` schema by default (can be
overriden by user) and a final table with Typed columns. Contents in raw table are _NOT_
deduplicated.

### Raw Table schema

| Airbyte field          | Description                                                        | Column type              |
| ---------------------- | ------------------------------------------------------------------ | ------------------------ |
| \_airbyte_raw_id       | A UUID assigned to each processed event                            | VARCHAR                  |
| \_airbyte_extracted_at | A timestamp for when the event was pulled from the data source     | TIMESTAMP WITH TIME ZONE |
| \_airbyte_loaded_at    | Timestamp to indicate when the record was loaded into Typed tables | TIMESTAMP WITH TIME ZONE |
| \_airbyte_data         | A JSON blob with the event data.                                   | VARIANT                  |

**Note:** Although the contents of the `_airbyte_data` are fairly stable, schema of the raw table
could be subject to change in future versions.

**Note:** By default, Airbyte creates permanent tables. If you prefer transient tables, create a
dedicated transient database for Airbyte. For more information, refer
to[ Working with Temporary and Transient Tables](https://docs.snowflake.com/en/user-guide/tables-temp-transient.html)

## Data type map

| Airbyte type                        | Snowflake type |
| :---------------------------------- | :------------- |
| STRING                              | TEXT           |
| STRING (BASE64)                     | TEXT           |
| STRING (BIG_NUMBER)                 | TEXT           |
| STRING (BIG_INTEGER)                | TEXT           |
| NUMBER                              | FLOAT          |
| INTEGER                             | NUMBER         |
| BOOLEAN                             | BOOLEAN        |
| STRING (TIMESTAMP_WITH_TIMEZONE)    | TIMESTAMP_TZ   |
| STRING (TIMESTAMP_WITHOUT_TIMEZONE) | TIMESTAMP_NTZ  |
| STRING (TIME_WITH_TIMEZONE)         | TEXT           |
| STRING (TIME_WITHOUT_TIMEZONE)      | TIME           |
| DATE                                | DATE           |
| OBJECT                              | OBJECT         |
| ARRAY                               | ARRAY          |

## Supported sync modes

The Snowflake destination supports the following sync modes:

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental Sync - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental Sync - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Snowflake tutorials

Now that you have set up the Snowflake destination connector, check out the following Snowflake
tutorials:

- [Build a data ingestion pipeline from Mailchimp to Snowflake](https://airbyte.com/tutorials/data-ingestion-pipeline-mailchimp-snowflake)
- [Replicate data from a PostgreSQL database to Snowflake](https://airbyte.com/tutorials/postgresql-database-to-snowflake)
- [Migrate your data from Redshift to Snowflake](https://airbyte.com/tutorials/redshift-to-snowflake)
- [Orchestrate ELT pipelines with Prefect, Airbyte and dbt](https://airbyte.com/tutorials/elt-pipeline-prefect-airbyte-dbt)

## Troubleshooting

### 'Current role does not have permissions on the target schema'

If you receive an error stating `Current role does not have permissions on the target schema` make
sure that the Snowflake destination `SCHEMA` is one that the role you've provided has permissions
on. When creating a connection, it may allow you to select `Mirror source structure` for the
`Destination namespace`, which if you have followed some of our default examples and tutorials may
result in the connection trying to write to a `PUBLIC` schema.

A quick fix could be to edit your connection's 'Replication' settings from `Mirror source structure`
to `Destination Default`. Otherwise, make sure to grant the role the required permissions in the
desired namespace.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version         | Date       | Pull Request                                               | Subject                                                                                                                                                                          |
| :-------------- | :--------- | :--------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 3.11.11         | 2024-08-20 | [44476](https://github.com/airbytehq/airbyte/pull/44476)   | Increase message parsing limit to 100mb                                                                                                                                          |
| 3.11.10         | 2024-08-22 | [\#44526](https://github.com/airbytehq/airbyte/pull/44526) | Revert protocol compliance fix                                                                                                                                                   |
| 3.11.9          | 2024-08-19 | [\#43367](https://github.com/airbytehq/airbyte/pull/43367) | Add opt in using MERGE statement for upserts and deletes                                                                                                                         |
| 3.11.8          | 2024-08-16 | [\#42505](https://github.com/airbytehq/airbyte/pull/42505) | Fix bug in refreshes logic (already mitigated in platform, just fixing protocol compliance)                                                                                      |
| 3.11.7          | 2024-08-09 | [\#43440](https://github.com/airbytehq/airbyte/pull/43440) | remove contention on state table by deleting rows ony once every 100 updates                                                                                                     |
| 3.11.6          | 2024-08-09 | [\#43332](https://github.com/airbytehq/airbyte/pull/43332) | bump Java CDK                                                                                                                                                                    |
| 3.11.5          | 2024-08-07 | [\#43348](https://github.com/airbytehq/airbyte/pull/43348) | SnowflakeSqlGen cleanup to Kotlin string interpolation                                                                                                                           |
| 3.11.4          | 2024-07-18 | [\#41940](https://github.com/airbytehq/airbyte/pull/41940) | Update host regex to allow connecting to LocalStack Snowflake                                                                                                                    |
| 3.11.3          | 2024-07-15 | [\#41968](https://github.com/airbytehq/airbyte/pull/41968) | Don't hang forever on empty stream list; shorten error message on INCOMPLETE stream status                                                                                       |
| 3.11.2          | 2024-07-12 | [\#41674](https://github.com/airbytehq/airbyte/pull/41674) | Upgrade to latest CDK                                                                                                                                                            |
| 3.11.1          | 2024-07-08 | [\#41041](https://github.com/airbytehq/airbyte/pull/41041) | Fix resume logic in truncate refreshes to prevent data loss                                                                                                                      |
| 3.11.0          | 2024-06-25 | [\#39473](https://github.com/airbytehq/airbyte/pull/39473) | Support for [refreshes](../../operator-guides/refreshes.md) and resumable full refresh. WARNING: You must upgrade to platform 0.63.7 before upgrading to this connector version. |
| 3.10.1          | 2024-06-11 | [\#39399](https://github.com/airbytehq/airbyte/pull/39399) | Bug fix for \_airbyte_meta not migrated in OVERWRITE mode                                                                                                                        |
| 3.10.0          | 2024-06-10 | [\#39107](https://github.com/airbytehq/airbyte/pull/39107) | \_airbyte_meta and \_airbyte_generation_id in Raw tables and final tables                                                                                                        |
| 3.9.1           | 2024-06-05 | [\#39135](https://github.com/airbytehq/airbyte/pull/39135) | Improved error handling for Staging files                                                                                                                                        |
| 3.9.0           | 2024-05-23 | [\#38658](https://github.com/airbytehq/airbyte/pull/38658) | Adapting to newer interfaces from #38107                                                                                                                                         |
| 3.8.4           | 2024-05-23 | [\#38632](https://github.com/airbytehq/airbyte/pull/38632) | convert all tests to kotlin                                                                                                                                                      |
| 3.8.3           | 2024-05-23 | [\#38586](https://github.com/airbytehq/airbyte/pull/38586) | Bump CDK version                                                                                                                                                                 |
| 3.8.2           | 2024-05-22 | [\#38553](https://github.com/airbytehq/airbyte/pull/38553) | Remove `SwitchingDestination` and `AbstractJdbcDestination` dependency in destination                                                                                            |
| 3.8.1           | 2024-05-22 | [\#38568](https://github.com/airbytehq/airbyte/pull/38568) | Adopt latest CDK                                                                                                                                                                 |
| 3.8.0           | 2024-05-08 | [\#37715](https://github.com/airbytehq/airbyte/pull/37715) | Remove option for incremental typing and deduping                                                                                                                                |
| 3.7.4           | 2024-05-07 | [\#38052](https://github.com/airbytehq/airbyte/pull/38052) | Revert problematic optimization                                                                                                                                                  |
| 3.7.3           | 2024-05-07 | [\#34612](https://github.com/airbytehq/airbyte/pull/34612) | Adopt CDK 0.33.2                                                                                                                                                                 |
| 3.7.2           | 2024-05-06 | [\#37857](https://github.com/airbytehq/airbyte/pull/37857) | Use safe executeMetadata call                                                                                                                                                    |
| 3.7.1           | 2024-04-30 | [\#36910](https://github.com/airbytehq/airbyte/pull/36910) | Bump CDK version                                                                                                                                                                 |
| 3.7.0           | 2024-04-08 | [\#35754](https://github.com/airbytehq/airbyte/pull/35754) | Allow configuring `data_retention_time_in_days`; apply to both raw and final tables. _Note_: Existing tables will not be affected; you must manually alter them.                 |
| 3.6.6           | 2024-03-26 | [\#36466](https://github.com/airbytehq/airbyte/pull/36466) | Correctly hhandle instances with `QUOTED_IDENTIFIERS_IGNORE_CASE` enabled globally                                                                                               |
| 3.6.5           | 2024-03-25 | [\#36461](https://github.com/airbytehq/airbyte/pull/36461) | Internal code change (use published CDK artifact instead of source dependency)                                                                                                   |
| 3.6.4           | 2024-03-25 | [\#36396](https://github.com/airbytehq/airbyte/pull/36396) | Handle instances with `QUOTED_IDENTIFIERS_IGNORE_CASE` enabled globally                                                                                                          |
| 3.6.3           | 2024-03-25 | [\#36452](https://github.com/airbytehq/airbyte/pull/36452) | Remove Query timeout                                                                                                                                                             |
| 3.6.2           | 2024-03-18 | [\#36240](https://github.com/airbytehq/airbyte/pull/36240) | Hide oAuth config option                                                                                                                                                         |
| 3.6.1           | 2024-03-07 | [\#35899](https://github.com/airbytehq/airbyte/pull/35899) | Adopt CDK 0.23.18; Null safety check in state parsing                                                                                                                            |
| 3.6.0           | 2024-03-06 | [\#35308](https://github.com/airbytehq/airbyte/pull/35308) | Upgrade CDK; use utc tz for extracted_at; Migrate existing extracted_at to utc;                                                                                                  |
| 3.5.14          | 2024-02-22 | [\#35456](https://github.com/airbytehq/airbyte/pull/35456) | Adopt CDK 0.23.0; Gather initial state upfront, reduce information_schema calls                                                                                                  |
| 3.5.13          | 2024-02-22 | [\#35569](https://github.com/airbytehq/airbyte/pull/35569) | Fix logging bug.                                                                                                                                                                 |
| 3.5.12          | 2024-02-15 | [\#35240](https://github.com/airbytehq/airbyte/pull/35240) | Adopt CDK 0.20.9                                                                                                                                                                 |
| 3.5.11          | 2024-02-12 | [\#35194](https://github.com/airbytehq/airbyte/pull/35194) | Reorder auth options                                                                                                                                                             |
| 3.5.10          | 2024-02-12 | [\#35144](https://github.com/airbytehq/airbyte/pull/35144) | Adopt CDK 0.20.2                                                                                                                                                                 |
| 3.5.9           | 2024-02-12 | [\#35111](https://github.com/airbytehq/airbyte/pull/35111) | Adopt CDK 0.20.1                                                                                                                                                                 |
| 3.5.8           | 2024-02-09 | [\#34574](https://github.com/airbytehq/airbyte/pull/34574) | Adopt CDK 0.20.0                                                                                                                                                                 |
| 3.5.7           | 2024-02-08 | [\#34747](https://github.com/airbytehq/airbyte/pull/34747) | Adopt CDK 0.19.0                                                                                                                                                                 |
| 3.5.6           | 2024-02-08 | [\#35027](https://github.com/airbytehq/airbyte/pull/35027) | Upgrade CDK to version 0.17.1                                                                                                                                                    |
| 3.5.5           | 2024-02-08 | [\#34502](https://github.com/airbytehq/airbyte/pull/34502) | Reduce COPY frequency                                                                                                                                                            |
| 3.5.4           | 2024-01-24 | [\#34451](https://github.com/airbytehq/airbyte/pull/34451) | Improve logging for unparseable input                                                                                                                                            |
| 3.5.3           | 2024-01-25 | [\#34528](https://github.com/airbytehq/airbyte/pull/34528) | Fix spurious `check` failure (`UnsupportedOperationException: Snowflake does not use the native JDBC DV2 interface`)                                                             |
| 3.5.2           | 2024-01-24 | [\#34458](https://github.com/airbytehq/airbyte/pull/34458) | Improve error reporting                                                                                                                                                          |
| 3.5.1           | 2024-01-24 | [\#34501](https://github.com/airbytehq/airbyte/pull/34501) | Internal code changes for Destinations V2                                                                                                                                        |
| 3.5.0           | 2024-01-24 | [\#34462](https://github.com/airbytehq/airbyte/pull/34462) | Upgrade CDK to 0.14.0                                                                                                                                                            |
| 3.4.22          | 2024-01-12 | [\#34227](https://github.com/airbytehq/airbyte/pull/34227) | Upgrade CDK to 0.12.0; Cleanup unused dependencies                                                                                                                               |
| 3.4.21          | 2024-01-10 | [\#34083](https://github.com/airbytehq/airbyte/pull/34083) | Emit destination stats as part of the state message                                                                                                                              |
| 3.4.20          | 2024-01-05 | [\#33948](https://github.com/airbytehq/airbyte/pull/33948) | Skip retrieving initial table state when setup fails                                                                                                                             |
| 3.4.19          | 2024-01-04 | [\#33730](https://github.com/airbytehq/airbyte/pull/33730) | Internal code structure changes                                                                                                                                                  |
| 3.4.18          | 2024-01-02 | [\#33728](https://github.com/airbytehq/airbyte/pull/33728) | Add option to only type and dedupe at the end of the sync                                                                                                                        |
| 3.4.17          | 2023-12-20 | [\#33704](https://github.com/airbytehq/airbyte/pull/33704) | Update to java CDK 0.10.0 (no changes)                                                                                                                                           |
| 3.4.16          | 2023-12-18 | [\#33124](https://github.com/airbytehq/airbyte/pull/33124) | Make Schema Creation Seperate from Table Creation                                                                                                                                |
| 3.4.15          | 2023-12-13 | [\#33232](https://github.com/airbytehq/airbyte/pull/33232) | Only run typing+deduping for a stream if the stream had any records                                                                                                              |
| 3.4.14          | 2023-12-08 | [\#33263](https://github.com/airbytehq/airbyte/pull/33263) | Adopt java CDK version 0.7.0                                                                                                                                                     |
| 3.4.13          | 2023-12-05 | [\#32326](https://github.com/airbytehq/airbyte/pull/32326) | Use jdbc metadata for table existence check                                                                                                                                      |
| 3.4.12          | 2023-12-04 | [\#33084](https://github.com/airbytehq/airbyte/pull/33084) | T&D SQL statements moved to debug log level                                                                                                                                      |
| 3.4.11          | 2023-11-14 | [\#32526](https://github.com/airbytehq/airbyte/pull/32526) | Clean up memory manager logs.                                                                                                                                                    |
| 3.4.10          | 2023-11-08 | [\#32125](https://github.com/airbytehq/airbyte/pull/32125) | Fix compilation warnings.                                                                                                                                                        |
| 3.4.9           | 2023-11-06 | [\#32026](https://github.com/airbytehq/airbyte/pull/32026) | Add separate TRY_CAST transaction to reduce compute usage                                                                                                                        |
| 3.4.8           | 2023-11-06 | [\#32190](https://github.com/airbytehq/airbyte/pull/32190) | Further improve error reporting                                                                                                                                                  |
| 3.4.7           | 2023-11-06 | [\#32193](https://github.com/airbytehq/airbyte/pull/32193) | Adopt java CDK version 0.4.1.                                                                                                                                                    |
| 3.4.6           | 2023-11-02 | [\#32124](https://github.com/airbytehq/airbyte/pull/32124) | Revert `merge` statement                                                                                                                                                         |
| 3.4.5           | 2023-11-02 | [\#31983](https://github.com/airbytehq/airbyte/pull/31983) | Improve error reporting                                                                                                                                                          |
| 3.4.4           | 2023-10-30 | [\#31985](https://github.com/airbytehq/airbyte/pull/31985) | Delay upgrade deadline to Nov 7                                                                                                                                                  |
| 3.4.3           | 2023-10-30 | [\#31960](https://github.com/airbytehq/airbyte/pull/31960) | Adopt java CDK version 0.2.0.                                                                                                                                                    |
| 3.4.2           | 2023-10-27 | [\#31897](https://github.com/airbytehq/airbyte/pull/31897) | Further filtering on extracted_at                                                                                                                                                |
| 3.4.1           | 2023-10-27 | [\#31683](https://github.com/airbytehq/airbyte/pull/31683) | Performance enhancement (switch to a `merge` statement for incremental-dedup syncs)                                                                                              |
| 3.4.0           | 2023-10-25 | [\#31686](https://github.com/airbytehq/airbyte/pull/31686) | Opt out flag for typed and deduped tables                                                                                                                                        |
| 3.3.0           | 2023-10-25 | [\#31520](https://github.com/airbytehq/airbyte/pull/31520) | Stop deduping raw table                                                                                                                                                          |
| 3.2.3           | 2023-10-17 | [\#31191](https://github.com/airbytehq/airbyte/pull/31191) | Improve typing+deduping performance by filtering new raw records on extracted_at                                                                                                 |
| 3.2.2           | 2023-10-10 | [\#31194](https://github.com/airbytehq/airbyte/pull/31194) | Deallocate unused per stream buffer memory when empty                                                                                                                            |
| 3.2.1           | 2023-10-10 | [\#31083](https://github.com/airbytehq/airbyte/pull/31083) | Fix precision of numeric values in async destinations                                                                                                                            |
| 3.2.0           | 2023-10-09 | [\#31149](https://github.com/airbytehq/airbyte/pull/31149) | No longer fail syncs when PKs are null - try do dedupe anyway                                                                                                                    |
| 3.1.22          | 2023-10-06 | [\#31153](https://github.com/airbytehq/airbyte/pull/31153) | Increase jvm GC retries                                                                                                                                                          |
| 3.1.21          | 2023-10-06 | [\#31139](https://github.com/airbytehq/airbyte/pull/31139) | Bump CDK version                                                                                                                                                                 |
| 3.1.20          | 2023-10-06 | [\#31129](https://github.com/airbytehq/airbyte/pull/31129) | Reduce async buffer size                                                                                                                                                         |
| 3.1.19          | 2023-10-04 | [\#31082](https://github.com/airbytehq/airbyte/pull/31082) | Revert null PK checks                                                                                                                                                            |
| 3.1.18          | 2023-10-01 | [\#30779](https://github.com/airbytehq/airbyte/pull/30779) | Final table PK columns become non-null and skip check for null PKs in raw records (performance)                                                                                  |
| 3.1.17          | 2023-09-29 | [\#30938](https://github.com/airbytehq/airbyte/pull/30938) | Upgrade snowflake-jdbc driver                                                                                                                                                    |
| 3.1.16          | 2023-09-28 | [\#30835](https://github.com/airbytehq/airbyte/pull/30835) | Fix regression from 3.1.15 in supporting concurrent syncs with identical stream name but different namespace                                                                     |
| 3.1.15          | 2023-09-26 | [\#30775](https://github.com/airbytehq/airbyte/pull/30775) | Increase async block size                                                                                                                                                        |
| 3.1.14          | 2023-09-27 | [\#30739](https://github.com/airbytehq/airbyte/pull/30739) | Fix column name collision detection                                                                                                                                              |
| 3.1.13          | 2023-09-19 | [\#30599](https://github.com/airbytehq/airbyte/pull/30599) | Support concurrent syncs with identical stream name but different namespace                                                                                                      |
| 3.1.12          | 2023-09-21 | [\#30671](https://github.com/airbytehq/airbyte/pull/30671) | Reduce async buffer size                                                                                                                                                         |
| 3.1.11          | 2023-09-19 | [\#30592](https://github.com/airbytehq/airbyte/pull/30592) | Internal code changes                                                                                                                                                            |
| 3.1.10          | 2023-09-18 | [\#30546](https://github.com/airbytehq/airbyte/pull/30546) | Make sure that the async buffer are flush every 5 minutes                                                                                                                        |
| 3.1.9           | 2023-09-19 | [\#30319](https://github.com/airbytehq/airbyte/pull/30319) | Support column names that are reserved                                                                                                                                           |
| 3.1.8           | 2023-09-18 | [\#30479](https://github.com/airbytehq/airbyte/pull/30479) | Fix async memory management                                                                                                                                                      |
| 3.1.7           | 2023-09-15 | [\#30491](https://github.com/airbytehq/airbyte/pull/30491) | Improve error message display                                                                                                                                                    |
| 3.1.6           | 2023-09-14 | [\#30439](https://github.com/airbytehq/airbyte/pull/30439) | Fix a transient error                                                                                                                                                            |
| 3.1.5           | 2023-09-13 | [\#30416](https://github.com/airbytehq/airbyte/pull/30416) | Support `${` in stream name/namespace, and in column names                                                                                                                       |
| 3.1.4           | 2023-09-12 | [\#30364](https://github.com/airbytehq/airbyte/pull/30364) | Add log message                                                                                                                                                                  |
| 3.1.3           | 2023-08-29 | [\#29878](https://github.com/airbytehq/airbyte/pull/29878) | Reenable incremental typing and deduping                                                                                                                                         |
| 3.1.2           | 2023-08-31 | [\#30020](https://github.com/airbytehq/airbyte/pull/30020) | Run typing and deduping tasks in parallel                                                                                                                                        |
| 3.1.1           | 2023-09-05 | [\#30117](https://github.com/airbytehq/airbyte/pull/30117) | Type and Dedupe at sync start and then every 6 hours                                                                                                                             |
| 3.1.0           | 2023-09-01 | [\#30056](https://github.com/airbytehq/airbyte/pull/30056) | Upcase final table names to allow case-insensitive references                                                                                                                    |
| 3.0.2           | 2023-09-01 | [\#30121](https://github.com/airbytehq/airbyte/pull/30121) | Improve performance on very wide streams by skipping TRY_CAST on strings                                                                                                         |
| 3.0.1           | 2023-08-27 | [\#30065](https://github.com/airbytehq/airbyte/pull/30065) | Clearer error thrown when records are missing a primary key                                                                                                                      |
| 3.0.0           | 2023-08-27 | [\#29783](https://github.com/airbytehq/airbyte/pull/29783) | Destinations V2                                                                                                                                                                  |
| 2.1.7           | 2023-08-29 | [\#29949](https://github.com/airbytehq/airbyte/pull/29949) | Destinations V2: Fix checking for empty table by ensuring upper-case DB names                                                                                                    |
| 2.1.6           | 2023-08-28 | [\#29878](https://github.com/airbytehq/airbyte/pull/29878) | Destinations V2: Fix detection of existing table by ensuring upper-case DB names                                                                                                 |
| 2.1.5           | 2023-08-28 | [\#29903](https://github.com/airbytehq/airbyte/pull/29917) | Destinations V2: Performance Improvement, Changing Metadata error array construction from ARRAY_CAT to ARRAY_CONSTRUCT_COMPACT                                                   |
| 2.1.4           | 2023-08-28 | [\#29903](https://github.com/airbytehq/airbyte/pull/29903) | Abort queries on crash                                                                                                                                                           |
| 2.1.3           | 2023-08-25 | [\#29881](https://github.com/airbytehq/airbyte/pull/29881) | Destinations v2: Only run T+D once at end of sync, to prevent data loss under async conditions                                                                                   |
| 2.1.2           | 2023-08-24 | [\#29805](https://github.com/airbytehq/airbyte/pull/29805) | Destinations v2: Don't soft reset in migration                                                                                                                                   |
| 2.1.1           | 2023-08-23 | [\#29774](https://github.com/airbytehq/airbyte/pull/29774) | Destinations v2: Don't soft reset overwrite syncs                                                                                                                                |
| 2.1.0           | 2023-08-21 | [\#29636](https://github.com/airbytehq/airbyte/pull/29636) | Destinations v2: Several Critical Bug Fixes (cursorless dedup, improved floating-point handling, improved special characters handling; improved error handling)                  |
| 2.0.0           | 2023-08-09 | [\#28894](https://github.com/airbytehq/airbyte/pull/29236) | Remove support for Snowflake GCS/S3 loading method in favor of Snowflake Internal staging                                                                                        |
| 1.3.3           | 2023-08-15 | [\#29461](https://github.com/airbytehq/airbyte/pull/29461) | Changing a static constant reference                                                                                                                                             |
| 1.3.2           | 2023-08-11 | [\#29381](https://github.com/airbytehq/airbyte/pull/29381) | Destinations v2: Add support for streams with no columns                                                                                                                         |
| 1.3.1           | 2023-08-04 | [\#28894](https://github.com/airbytehq/airbyte/pull/28894) | Destinations v2: Update SqlGenerator                                                                                                                                             |
| 1.3.0           | 2023-08-07 | [\#29174](https://github.com/airbytehq/airbyte/pull/29174) | Destinations v2: early access release                                                                                                                                            |
| 1.2.10          | 2023-08-07 | [\#29188](https://github.com/airbytehq/airbyte/pull/29188) | Internal code refactoring                                                                                                                                                        |
| 1.2.9           | 2023-08-04 | [\#28677](https://github.com/airbytehq/airbyte/pull/28677) | Destinations v2: internal code changes to prepare for early access release                                                                                                       |
| 1.2.8           | 2023-08-03 | [\#29047](https://github.com/airbytehq/airbyte/pull/29047) | Avoid logging record if the format is invalid                                                                                                                                    |
| 1.2.7           | 2023-08-02 | [\#28976](https://github.com/airbytehq/airbyte/pull/28976) | Fix composite PK handling in v1 mode                                                                                                                                             |
| 1.2.6           | 2023-08-01 | [\#28618](https://github.com/airbytehq/airbyte/pull/28618) | Reduce logging noise                                                                                                                                                             |
| 1.2.5           | 2023-07-24 | [\#28618](https://github.com/airbytehq/airbyte/pull/28618) | Add hooks in preparation for destinations v2 implementation                                                                                                                      |
| 1.2.4           | 2023-07-21 | [\#28584](https://github.com/airbytehq/airbyte/pull/28584) | Install dependencies in preparation for destinations v2 work                                                                                                                     |
| 1.2.3           | 2023-07-21 | [\#28345](https://github.com/airbytehq/airbyte/pull/28345) | Pull in async framework minor bug fix for race condition on state emission                                                                                                       |
| 1.2.2           | 2023-07-14 | [\#28345](https://github.com/airbytehq/airbyte/pull/28345) | Increment patch to trigger a rebuild                                                                                                                                             |
| 1.2.1           | 2023-07-14 | [\#28315](https://github.com/airbytehq/airbyte/pull/28315) | Pull in async framework minor bug fix to avoid Snowflake hanging on close                                                                                                        |
| 1.2.0           | 2023-07-5  | [\#27935](https://github.com/airbytehq/airbyte/pull/27935) | Enable Faster Snowflake Syncs with Asynchronous writes                                                                                                                           |
| 1.1.0           | 2023-06-27 | [\#27781](https://github.com/airbytehq/airbyte/pull/27781) | License Update: Elv2                                                                                                                                                             |
| 1.0.6           | 2023-06-21 | [\#27555](https://github.com/airbytehq/airbyte/pull/27555) | Reduce image size                                                                                                                                                                |
| 1.0.5           | 2023-05-31 | [\#25782](https://github.com/airbytehq/airbyte/pull/25782) | Internal scaffolding for future development                                                                                                                                      |
| 1.0.4           | 2023-05-19 | [\#26323](https://github.com/airbytehq/airbyte/pull/26323) | Prevent infinite retry loop under specific circumstances                                                                                                                         |
| 1.0.3           | 2023-05-15 | [\#26081](https://github.com/airbytehq/airbyte/pull/26081) | Reverts splits bases                                                                                                                                                             |
| 1.0.2           | 2023-05-05 | [\#25649](https://github.com/airbytehq/airbyte/pull/25649) | Splits bases (reverted)                                                                                                                                                          |
| 1.0.1           | 2023-04-29 | [\#25570](https://github.com/airbytehq/airbyte/pull/25570) | Internal library update                                                                                                                                                          |
| 1.0.0           | 2023-05-02 | [\#25739](https://github.com/airbytehq/airbyte/pull/25739) | Removed Azure Blob Storage as a loading method                                                                                                                                   |
| 0.4.63          | 2023-04-27 | [\#25346](https://github.com/airbytehq/airbyte/pull/25346) | Added FlushBufferFunction interface                                                                                                                                              |
| 0.4.61          | 2023-03-30 | [\#24736](https://github.com/airbytehq/airbyte/pull/24736) | Improve behavior when throttled by AWS API                                                                                                                                       |
| 0.4.60          | 2023-03-30 | [\#24698](https://github.com/airbytehq/airbyte/pull/24698) | Add option in spec to allow increasing the stream buffer size to 50                                                                                                              |
| 0.4.59          | 2023-03-23 | [\#23904](https://github.com/airbytehq/airbyte/pull/24405) | Fail faster in certain error cases                                                                                                                                               |
| 0.4.58          | 2023-03-27 | [\#24615](https://github.com/airbytehq/airbyte/pull/24615) | Fixed host validation by pattern on UI                                                                                                                                           |
| 0.4.56 (broken) | 2023-03-22 | [\#23904](https://github.com/airbytehq/airbyte/pull/23904) | Added host validation by pattern on UI                                                                                                                                           |
| 0.4.54          | 2023-03-17 | [\#23788](https://github.com/airbytehq/airbyte/pull/23788) | S3-Parquet: added handler to process null values in arrays                                                                                                                       |
| 0.4.53          | 2023-03-15 | [\#24058](https://github.com/airbytehq/airbyte/pull/24058) | added write attempt to internal staging Check method                                                                                                                             |
| 0.4.52          | 2023-03-10 | [\#23931](https://github.com/airbytehq/airbyte/pull/23931) | Added support for periodic buffer flush                                                                                                                                          |
| 0.4.51          | 2023-03-10 | [\#23466](https://github.com/airbytehq/airbyte/pull/23466) | Changed S3 Avro type from Int to Long                                                                                                                                            |
| 0.4.49          | 2023-02-27 | [\#23360](https://github.com/airbytehq/airbyte/pull/23360) | Added logging for flushing and writing data to destination storage                                                                                                               |
| 0.4.48          | 2023-02-23 | [\#22877](https://github.com/airbytehq/airbyte/pull/22877) | Add handler for IP not in whitelist error and more handlers for insufficient permission error                                                                                    |
| 0.4.47          | 2023-01-30 | [\#21912](https://github.com/airbytehq/airbyte/pull/21912) | Catch "Create" Table and Stage Known Permissions and rethrow as ConfigExceptions                                                                                                 |
| 0.4.46          | 2023-01-26 | [\#20631](https://github.com/airbytehq/airbyte/pull/20631) | Added support for destination checkpointing with staging                                                                                                                         |
| 0.4.45          | 2023-01-25 | [\#21087](https://github.com/airbytehq/airbyte/pull/21764) | Catch Known Permissions and rethrow as ConfigExceptions                                                                                                                          |
| 0.4.44          | 2023-01-20 | [\#21087](https://github.com/airbytehq/airbyte/pull/21087) | Wrap Authentication Errors as Config Exceptions                                                                                                                                  |
| 0.4.43          | 2023-01-20 | [\#21450](https://github.com/airbytehq/airbyte/pull/21450) | Updated Check methods to handle more possible s3 and gcs stagings issues                                                                                                         |
| 0.4.42          | 2023-01-12 | [\#21342](https://github.com/airbytehq/airbyte/pull/21342) | Better handling for conflicting destination streams                                                                                                                              |
| 0.4.41          | 2022-12-16 | [\#20566](https://github.com/airbytehq/airbyte/pull/20566) | Improve spec to adhere to standards                                                                                                                                              |
| 0.4.40          | 2022-11-11 | [\#19302](https://github.com/airbytehq/airbyte/pull/19302) | Set jdbc application env variable depends on env - airbyte_oss or airbyte_cloud                                                                                                  |
| 0.4.39          | 2022-11-09 | [\#18970](https://github.com/airbytehq/airbyte/pull/18970) | Updated "check" connection method to handle more errors                                                                                                                          |
| 0.4.38          | 2022-09-26 | [\#17115](https://github.com/airbytehq/airbyte/pull/17115) | Added connection string identifier                                                                                                                                               |
| 0.4.37          | 2022-09-21 | [\#16839](https://github.com/airbytehq/airbyte/pull/16839) | Update JDBC driver for Snowflake to 3.13.19                                                                                                                                      |
| 0.4.36          | 2022-09-14 | [\#15668](https://github.com/airbytehq/airbyte/pull/15668) | Wrap logs in AirbyteLogMessage                                                                                                                                                   |
| 0.4.35          | 2022-09-01 | [\#16243](https://github.com/airbytehq/airbyte/pull/16243) | Fix Json to Avro conversion when there is field name clash from combined restrictions (`anyOf`, `oneOf`, `allOf` fields).                                                        |
| 0.4.34          | 2022-07-23 | [\#14388](https://github.com/airbytehq/airbyte/pull/14388) | Add support for key pair authentication                                                                                                                                          |
| 0.4.33          | 2022-07-15 | [\#14494](https://github.com/airbytehq/airbyte/pull/14494) | Make S3 output filename configurable.                                                                                                                                            |
| 0.4.32          | 2022-07-14 | [\#14618](https://github.com/airbytehq/airbyte/pull/14618) | Removed additionalProperties: false from JDBC destination connectors                                                                                                             |
| 0.4.31          | 2022-07-07 | [\#13729](https://github.com/airbytehq/airbyte/pull/13729) | Improve configuration field description                                                                                                                                          |
| 0.4.30          | 2022-06-24 | [\#14114](https://github.com/airbytehq/airbyte/pull/14114) | Remove "additionalProperties": false from specs for connectors with staging                                                                                                      |
| 0.4.29          | 2022-06-17 | [\#13753](https://github.com/airbytehq/airbyte/pull/13753) | Deprecate and remove PART_SIZE_MB fields from connectors based on StreamTransferManager                                                                                          |
| 0.4.28          | 2022-05-18 | [\#12952](https://github.com/airbytehq/airbyte/pull/12952) | Apply buffering strategy on GCS staging                                                                                                                                          |
| 0.4.27          | 2022-05-17 | [\#12820](https://github.com/airbytehq/airbyte/pull/12820) | Improved 'check' operation performance                                                                                                                                           |
| 0.4.26          | 2022-05-12 | [\#12805](https://github.com/airbytehq/airbyte/pull/12805) | Updated to latest base-java to emit AirbyteTraceMessages on error.                                                                                                               |
| 0.4.25          | 2022-05-03 | [\#12452](https://github.com/airbytehq/airbyte/pull/12452) | Add support for encrypted staging on S3; fix the purge_staging_files option                                                                                                      |
| 0.4.24          | 2022-03-24 | [\#11093](https://github.com/airbytehq/airbyte/pull/11093) | Added OAuth support (Compatible with Airbyte Version 0.35.60+)                                                                                                                   |
| 0.4.22          | 2022-03-18 | [\#10793](https://github.com/airbytehq/airbyte/pull/10793) | Fix namespace with invalid characters                                                                                                                                            |
| 0.4.21          | 2022-03-18 | [\#11071](https://github.com/airbytehq/airbyte/pull/11071) | Switch to compressed on-disk buffering before staging to s3/internal stage                                                                                                       |
| 0.4.20          | 2022-03-14 | [\#10341](https://github.com/airbytehq/airbyte/pull/10341) | Add Azure blob staging support                                                                                                                                                   |
| 0.4.19          | 2022-03-11 | [\#10699](https://github.com/airbytehq/airbyte/pull/10699) | Added unit tests                                                                                                                                                                 |
| 0.4.17          | 2022-02-25 | [\#10421](https://github.com/airbytehq/airbyte/pull/10421) | Refactor JDBC parameters handling                                                                                                                                                |
| 0.4.16          | 2022-02-25 | [\#10627](https://github.com/airbytehq/airbyte/pull/10627) | Add try catch to make sure all handlers are closed                                                                                                                               |
| 0.4.15          | 2022-02-22 | [\#10459](https://github.com/airbytehq/airbyte/pull/10459) | Add FailureTrackingAirbyteMessageConsumer                                                                                                                                        |
| 0.4.14          | 2022-02-17 | [\#10394](https://github.com/airbytehq/airbyte/pull/10394) | Reduce memory footprint.                                                                                                                                                         |
| 0.4.13          | 2022-02-16 | [\#10212](https://github.com/airbytehq/airbyte/pull/10212) | Execute COPY command in parallel for S3 and GCS staging                                                                                                                          |
| 0.4.12          | 2022-02-15 | [\#10342](https://github.com/airbytehq/airbyte/pull/10342) | Use connection pool, and fix connection leak.                                                                                                                                    |
| 0.4.11          | 2022-02-14 | [\#9920](https://github.com/airbytehq/airbyte/pull/9920)   | Updated the size of staging files for S3 staging. Also, added closure of S3 writers to staging files when data has been written to an staging file.                              |
| 0.4.10          | 2022-02-14 | [\#10297](https://github.com/airbytehq/airbyte/pull/10297) | Halve the record buffer size to reduce memory consumption.                                                                                                                       |
| 0.4.9           | 2022-02-14 | [\#10256](https://github.com/airbytehq/airbyte/pull/10256) | Add `ExitOnOutOfMemoryError` JVM flag.                                                                                                                                           |
| 0.4.8           | 2022-02-01 | [\#9959](https://github.com/airbytehq/airbyte/pull/9959)   | Fix null pointer exception from buffered stream consumer.                                                                                                                        |
| 0.4.7           | 2022-01-29 | [\#9745](https://github.com/airbytehq/airbyte/pull/9745)   | Integrate with Sentry.                                                                                                                                                           |
| 0.4.6           | 2022-01-28 | [\#9623](https://github.com/airbytehq/airbyte/pull/9623)   | Add jdbc_url_params support for optional JDBC parameters                                                                                                                         |
| 0.4.5           | 2021-12-29 | [\#9184](https://github.com/airbytehq/airbyte/pull/9184)   | Update connector fields title/description                                                                                                                                        |
| 0.4.4           | 2022-01-24 | [\#9743](https://github.com/airbytehq/airbyte/pull/9743)   | Fixed bug with dashes in schema name                                                                                                                                             |
| 0.4.3           | 2022-01-20 | [\#9531](https://github.com/airbytehq/airbyte/pull/9531)   | Start using new S3StreamCopier and expose the purgeStagingData option                                                                                                            |
| 0.4.2           | 2022-01-10 | [\#9141](https://github.com/airbytehq/airbyte/pull/9141)   | Fixed duplicate rows on retries                                                                                                                                                  |
| 0.4.1           | 2021-01-06 | [\#9311](https://github.com/airbytehq/airbyte/pull/9311)   | Update сreating schema during check                                                                                                                                              |
| 0.4.0           | 2021-12-27 | [\#9063](https://github.com/airbytehq/airbyte/pull/9063)   | Updated normalization to produce permanent tables                                                                                                                                |
| 0.3.24          | 2021-12-23 | [\#8869](https://github.com/airbytehq/airbyte/pull/8869)   | Changed staging approach to Byte-Buffered                                                                                                                                        |
| 0.3.23          | 2021-12-22 | [\#9039](https://github.com/airbytehq/airbyte/pull/9039)   | Added part_size configuration in UI for S3 loading method                                                                                                                        |
| 0.3.22          | 2021-12-21 | [\#9006](https://github.com/airbytehq/airbyte/pull/9006)   | Updated jdbc schema naming to follow Snowflake Naming Conventions                                                                                                                |
| 0.3.21          | 2021-12-15 | [\#8781](https://github.com/airbytehq/airbyte/pull/8781)   | Updated check method to verify permissions to create/drop stage for internal staging; compatibility fix for Java 17                                                              |
| 0.3.20          | 2021-12-10 | [\#8562](https://github.com/airbytehq/airbyte/pull/8562)   | Moving classes around for better dependency management; compatibility fix for Java 17                                                                                            |
| 0.3.19          | 2021-12-06 | [\#8528](https://github.com/airbytehq/airbyte/pull/8528)   | Set Internal Staging as default choice                                                                                                                                           |
| 0.3.18          | 2021-11-26 | [\#8253](https://github.com/airbytehq/airbyte/pull/8253)   | Snowflake Internal Staging Support                                                                                                                                               |
| 0.3.17          | 2021-11-08 | [\#7719](https://github.com/airbytehq/airbyte/pull/7719)   | Improve handling of wide rows by buffering records based on their byte size rather than their count                                                                              |
| 0.3.15          | 2021-10-11 | [\#6949](https://github.com/airbytehq/airbyte/pull/6949)   | Each stream was split into files of 10,000 records each for copying using S3 or GCS                                                                                              |
| 0.3.14          | 2021-09-08 | [\#5924](https://github.com/airbytehq/airbyte/pull/5924)   | Fixed AWS S3 Staging COPY is writing records from different table in the same raw table                                                                                          |
| 0.3.13          | 2021-09-01 | [\#5784](https://github.com/airbytehq/airbyte/pull/5784)   | Updated query timeout from 30 minutes to 3 hours                                                                                                                                 |
| 0.3.12          | 2021-07-30 | [\#5125](https://github.com/airbytehq/airbyte/pull/5125)   | Enable `additionalPropertities` in spec.json                                                                                                                                     |
| 0.3.11          | 2021-07-21 | [\#3555](https://github.com/airbytehq/airbyte/pull/3555)   | Partial Success in BufferedStreamConsumer                                                                                                                                        |
| 0.3.10          | 2021-07-12 | [\#4713](https://github.com/airbytehq/airbyte/pull/4713)   | Tag traffic with `airbyte` label to enable optimization opportunities from Snowflake                                                                                             |

</details>
