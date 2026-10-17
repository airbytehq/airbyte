# Redshift

<HideInUI>

This connector replicates data from Amazon Redshift to your destination using JDBC. It supports both full refresh and cursor-based incremental syncs.

</HideInUI>

## Features

| Feature                       | Supported | Notes                                                                                  |
| :---------------------------- | :-------- | :------------------------------------------------------------------------------------- |
| Full Refresh Sync             | Yes       |                                                                                        |
| Incremental Sync              | Yes       | Cursor-based, using `ORDER BY` on a user-defined cursor column                         |
| Replicate Incremental Deletes | No        |                                                                                        |
| Logical Replication (WAL)     | No        |                                                                                        |
| SSL Support                   | Yes       | Enabled by default on all connections                                                  |
| SSH Tunnel Connection         | No        |                                                                                        |
| Namespaces                    | Yes       | Enabled by default                                                                     |
| Schema Selection              | Yes       | Multiple schemas may be used at one time; leave empty to replicate all schemas          |

The Redshift source does not alter the schema present in your warehouse. Depending on the destination connected to this source, however, the schema may be altered. See the destination's documentation for more details.

### Incremental sync

The Redshift source connector supports incremental syncs using a [user-defined cursor field](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append/#user-defined-cursor) such as an `updated_at` column. The connector uses this column to track which rows have changed since the previous sync.

To run [incremental + dedupe](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped) syncs, you also need to configure a primary key for the stream.

## Prerequisites

1. An active Amazon Redshift cluster.
2. A database user with `SELECT` permission on the tables you want to replicate. Creating a dedicated read-only user is recommended.
3. Network access from Airbyte to your Redshift cluster (if they are in separate VPCs). See [Authorizing access to your cluster](https://docs.aws.amazon.com/redshift/latest/gsg/rs-gsg-authorize-cluster-access.html) in the AWS docs.

## Setup guide

### 1. Verify cluster accessibility

The easiest way to confirm that Airbyte can reach your Redshift cluster is to use the **Test Connection** button in the Airbyte UI. If the connection fails, review your VPC security groups and subnet routing.

### 2. Configure the source

Provide the following connection details in the Airbyte UI:

| Field              | Description                                                                                                                                                                                                                                                   |
| :----------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Host**           | The endpoint of your Redshift cluster, without the port or database name. This typically includes the cluster ID, region, and ends with `.redshift.amazonaws.com`. Find it on the cluster details page under [Connection string](https://docs.aws.amazon.com/redshift/latest/gsg/rs-gsg-connect-to-cluster.html#rs-gsg-how-to-get-connection-string). |
| **Port**           | The port your cluster listens on. The default is `5439`.                                                                                                                                                                                                      |
| **Database**       | The name of the database to connect to.                                                                                                                                                                                                                       |
| **Username**       | The database user to authenticate as.                                                                                                                                                                                                                         |
| **Password**       | The password for the database user.                                                                                                                                                                                                                           |
| **Schemas**        | (Optional) A list of schemas to replicate. Schema names are case-sensitive. Leave empty to replicate all schemas the user has access to.                                                                                                                      |
| **JDBC URL Params** | (Optional) Additional JDBC connection properties, formatted as `key=value` pairs separated by `&` (for example, `loginTimeout=30&tcpKeepAlive=true`).                                                                                                        |

### Encryption

All connections use SSL by default. No additional configuration is required.

## Data type handling

The connector maps Redshift data types to Airbyte types automatically. A few behaviors to be aware of:

- **`timestamp`** and **`timestamptz`** columns are read as raw server-rendered strings and parsed by the connector, bypassing the JDBC driver's timezone conversion. This avoids a known JDBC driver behavior where timestamps can shift by an hour during daylight saving time transitions.
- **`timestamptz`** values are stored in Redshift as UTC. The connector preserves the UTC instant when serializing these values.
- If you use a `timestamptz` column as a cursor for incremental syncs, the connector handles both timezone-aware and timezone-naive cursor formats.

## Limitations

- Change Data Capture (CDC) is not supported. Only cursor-based incremental replication is available.
- SSH tunnel connections are not supported.
- IAM-based authentication is not supported; you must authenticate with a database username and password.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                                   |
| :------ | :--------- | :------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------- |
| 0.5.5 | 2026-06-04 | [74769](https://github.com/airbytehq/airbyte/pull/74769) | Handle timezone-aware timestamps in cursor parsing and fix DST offset in `timestamptz` reads |
| 0.5.4 | 2025-07-16 | [62922](https://github.com/airbytehq/airbyte/pull/62922) | Convert to new gradle build flow |
| 0.5.3 | 2024-12-18 | [49893](https://github.com/airbytehq/airbyte/pull/49893) | Use a base image: airbyte/java-connector-base:1.0.0 |
| 0.5.2 | 2024-02-13 | [35223](https://github.com/airbytehq/airbyte/pull/35223) | Adopt CDK 0.20.4 |
| 0.5.1 | 2024-01-24 | [34453](https://github.com/airbytehq/airbyte/pull/34453) | bump CDK version |
| 0.5.0 | 2023-12-18 | [33484](https://github.com/airbytehq/airbyte/pull/33484) | Remove LEGACY state |
| (none)  | 2023-11-17 | [32616](https://github.com/airbytehq/airbyte/pull/32616) | Improve timestamptz handling                                                                                                              |
| 0.4.0   | 2023-06-26 | [27737](https://github.com/airbytehq/airbyte/pull/27737) | License Update: Elv2                                                                                                                      |
| 0.3.17  | 2023-06-20 | [27212](https://github.com/airbytehq/airbyte/pull/27212) | Fix silent exception swallowing in StreamingJdbcDatabase                                                                                  |
| 0.3.16  | 2022-12-14 | [20346](https://github.com/airbytehq/airbyte/pull/20346) | Consolidate date/time values mapping for JDBC sources                                                                                     |
| 0.3.15  | 2022-10-13 | [16238](https://github.com/airbytehq/airbyte/pull/16238) | Update incremental query to avoid data missing when new data is inserted at the same time as a sync starts under non-CDC incremental mode |
| 0.3.14  | 2022-09-01 | [16258](https://github.com/airbytehq/airbyte/pull/16258) | Emit state messages more frequently                                                                                                       |
| 0.3.13  | 2022-05-25 |                                                          | Added JDBC URL params                                                                                                                     |
| 0.3.12  | 2022-08-18 | [14356](https://github.com/airbytehq/airbyte/pull/14356) | DB Sources: only show a table can sync incrementally if at least one column can be used as a cursor field                                 |
| 0.3.11  | 2022-07-14 | [14574](https://github.com/airbytehq/airbyte/pull/14574) | Removed additionalProperties:false from JDBC source connectors                                                                            |
| 0.3.10  | 2022-04-29 | [12480](https://github.com/airbytehq/airbyte/pull/12480) | Query tables with adaptive fetch size to optimize JDBC memory consumption                                                                 |
| 0.3.9   | 2022-02-21 | [9744](https://github.com/airbytehq/airbyte/pull/9744)   | List only the tables on which the user has SELECT permissions.                                                                            |
| 0.3.8   | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256) | Add `-XX:+ExitOnOutOfMemoryError` JVM option                                                                                              |
| 0.3.7   | 2022-01-26 | [9721](https://github.com/airbytehq/airbyte/pull/9721)   | Added schema selection                                                                                                                    |
| 0.3.6   | 2022-01-20 | [8617](https://github.com/airbytehq/airbyte/pull/8617)   | Update connector fields title/description                                                                                                 |
| 0.3.5   | 2021-12-24 | [8958](https://github.com/airbytehq/airbyte/pull/8958)   | Add support for JdbcType.ARRAY                                                                                                            |
| 0.3.4   | 2021-10-21 | [7234](https://github.com/airbytehq/airbyte/pull/7234)   | Allow SSL traffic only                                                                                                                    |
| 0.3.3   | 2021-10-12 | [6965](https://github.com/airbytehq/airbyte/pull/6965)   | Added SSL Support                                                                                                                         |
| 0.3.2   | 2021-08-13 | [4699](https://github.com/airbytehq/airbyte/pull/4699)   | Added json config validator                                                                                                               |

</details>
