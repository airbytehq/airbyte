# CockroachDB

## Overview

The CockroachDB source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Resulting schema

The CockroachDb source does not alter the schema present in your database. Depending on the destination connected to this source, however, the schema may be altered. See the destination's documentation for more details.

### Data type mapping

CockroachDb data types are mapped to the following data types when synchronizing data:

| CockroachDb Type             | Resulting Type | Notes                                                             |
| :--------------------------- | :------------- | :---------------------------------------------------------------- |
| `bigint`                     | integer        |                                                                   |
| `bit`                        | boolean        |                                                                   |
| `boolean`                    | boolean        |                                                                   |
| `character`                  | string         |                                                                   |
| `character varying`          | string         |                                                                   |
| `date`                       | string         |                                                                   |
| `double precision`           | string         |                                                                   |
| `enum`                       | number         |                                                                   |
| `inet`                       | string         |                                                                   |
| `int`                        | integer        |                                                                   |
| `json`                       | string         |                                                                   |
| `jsonb`                      | string         |                                                                   |
| `numeric`                    | number         |                                                                   |
| `smallint`                   | integer        |                                                                   |
| `text`                       | string         |                                                                   |
| `time with timezone`         | string         | may be written as a native date type depending on the destination |
| `time without timezone`      | string         | may be written as a native date type depending on the destination |
| `timestamp with timezone`    | string         | may be written as a native date type depending on the destination |
| `timestamp without timezone` | string         | may be written as a native date type depending on the destination |
| `uuid`                       | string         |                                                                   |

**Note:** arrays for all the above types as well as custom types are supported, although they may be de-nested depending on the destination.

### Features

| Feature             | Supported | Notes |
| :------------------ | :-------- | :---- |
| Full Refresh Sync   | Yes       |       |
| Incremental Sync    | Yes       |       |
| Change Data Capture | No        |       |
| SSL Support         | Yes       |       |

## Getting started

### Requirements

1. CockroachDb `v1.15.x` or above
2. Allow connections from Airbyte to your CockroachDb database \(if they exist in separate VPCs\)
3. Create a dedicated read-only Airbyte user with access to all tables needed for replication

### Setup guide

#### 1. Make sure your database is accessible from the machine running Airbyte

This is dependent on your networking setup. The easiest way to verify if Airbyte is able to connect to your CockroachDb instance is via the check connection tool in the UI.

#### 2. Create a dedicated read-only user with access to the relevant tables \(Recommended but optional\)

This step is optional but highly recommended to allow for better permission control and auditing. Alternatively, you can use Airbyte with an existing user in your database.

To create a dedicated database user, run the following commands against your database:

```sql
CREATE USER airbyte PASSWORD 'your_password_here';
```

Then give it access to the relevant schema:

```sql
GRANT USAGE ON SCHEMA <schema_name> TO airbyte
```

Note that to replicate data from multiple CockroachDb schemas, you can re-run the command above to grant access to all the relevant schemas, but you'll need to set up multiple sources connecting to the same db on multiple schemas.

Next, grant the user read-only access to the relevant tables. The simplest way is to grant read access to all tables in the schema as follows:

```sql
GRANT SELECT ON ALL TABLES IN SCHEMA <schema_name> TO airbyte;

# Allow airbyte user to see tables created in the future
ALTER DEFAULT PRIVILEGES IN SCHEMA <schema_name> GRANT SELECT ON TABLES TO airbyte;
```

#### 3. That's it!

Your database user should now be ready for use with Airbyte.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                                   |
| :------ | :--------- | :------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------- |
| 0.2.4 | 2025-01-10 | [*PR_NUMBER_PLACEHOLDER*](https://github.com/airbytehq/airbyte/pull/*PR_NUMBER_PLACEHOLDER*) | Use a non root base image |
| 0.2.3 | 2024-12-18 | [49915](https://github.com/airbytehq/airbyte/pull/49915) | Use a base image: airbyte/java-connector-base:1.0.0 |
| 0.2.2 | 2024-02-13 | [35234](https://github.com/airbytehq/airbyte/pull/35234) | Adopt CDK 0.20.4 |
| 0.2.1 | 2024-01-24 | [34453](https://github.com/airbytehq/airbyte/pull/34453) | bump CDK version |
| 0.2.0 | 2023-12-18 | [33485](https://github.com/airbytehq/airbyte/pull/33485) | Removed LEGACY state |
| 0.1.22 | 2023-03-22 | [20760](https://github.com/airbytehq/airbyte/pull/20760) | Removed redundant date-time datatypes formatting |
| 0.1.21 | 2023-03-14 | [24000](https://github.com/airbytehq/airbyte/pull/24000) | Removed check method call on read. |
| 0.1.20 | 2023-03-06 | [23455](https://github.com/airbytehq/airbyte/pull/23455) | For network isolation, source connector accepts a list of hosts it is allowed to connect |
| 0.1.19  | 2022-12-14 | [20436](https://github.com/airbytehq/airbyte/pull/20346) | Consolidate date/time values mapping for JDBC sources                                                                                     |
|         | 2022-10-13 | [15535](https://github.com/airbytehq/airbyte/pull/16238) | Update incremental query to avoid data missing when new data is inserted at the same time as a sync starts under non-CDC incremental mode |
| 0.1.18  | 2022-09-01 | [16394](https://github.com/airbytehq/airbyte/pull/16394) | Added custom jdbc properties field                                                                                                        |
| 0.1.17  | 2022-09-01 | [16238](https://github.com/airbytehq/airbyte/pull/16238) | Emit state messages more frequently                                                                                                       |
| 0.1.16  | 2022-08-18 | [14356](https://github.com/airbytehq/airbyte/pull/14356) | DB Sources: only show a table can sync incrementally if at least one column can be used as a cursor field                                 |
| 0.1.13  | 2022-07-14 | [14574](https://github.com/airbytehq/airbyte/pull/14574) | Removed additionalProperties:false from JDBC source connectors                                                                            |
| 0.1.12  | 2022-04-29 | [12480](https://github.com/airbytehq/airbyte/pull/12480) | Query tables with adaptive fetch size to optimize JDBC memory consumption                                                                 |
| 0.1.11  | 2022-04-06 | [11729](https://github.com/airbytehq/airbyte/pull/11729) | Bump mina-sshd from 2.7.0 to 2.8.0                                                                                                        |
| 0.1.10  | 2022-02-24 | [10235](https://github.com/airbytehq/airbyte/pull/10235) | Fix Replication Failure due Multiple portal opens                                                                                         |
| 0.1.9   | 2022-02-21 | [10242](https://github.com/airbytehq/airbyte/pull/10242) | Fixed cursor for old connectors that use non-microsecond format. Now connectors work with both formats                                    |
| 0.1.8   | 2022-02-18 | [10242](https://github.com/airbytehq/airbyte/pull/10242) | Updated timestamp transformation with microseconds                                                                                        |
| 0.1.7   | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256) | Add `-XX:+ExitOnOutOfMemoryError` JVM option                                                                                              |
| 0.1.6   | 2022-02-08 | [10173](https://github.com/airbytehq/airbyte/pull/10173) | Improved discovering tables in case if user does not have permissions to any table                                                        |
| 0.1.5   | 2021-12-24 | [9004](https://github.com/airbytehq/airbyte/pull/9004)   | User can see only permmited tables during discovery                                                                                       |
| 0.1.4   | 2021-12-24 | [8958](https://github.com/airbytehq/airbyte/pull/8958)   | Add support for JdbcType.ARRAY                                                                                                            |
| 0.1.3   | 2021-10-10 | [7819](https://github.com/airbytehq/airbyte/pull/7819)   | Fixed Datatype errors during Cockroach DB parsing                                                                                         |
| 0.1.2   | 2021-08-13 | [4699](https://github.com/airbytehq/airbyte/pull/4699)   | Added json config validator                                                                                                               |

</details>
