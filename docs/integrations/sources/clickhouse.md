# ClickHouse

The ClickHouse source supports Full Refresh and Incremental syncs. You can choose whether the connector copies only new or updated data, or all rows in the tables and columns you set up for replication, every time a sync runs.

This connector is built on the source-jdbc framework and uses the [ClickHouse JDBC driver](https://github.com/ClickHouse/clickhouse-jdbc) to connect over the HTTP interface.

## Output schema

The ClickHouse source does not alter the schema present in your database. Depending on the destination connected to this source, however, the schema may be altered. See the destination's documentation for more details.

The connector automatically excludes the `system`, `information_schema`, and `INFORMATION_SCHEMA` databases from discovery.

## Features

| Feature                   | Supported   | Notes              |
| :------------------------ | :---------- | :----------------- |
| Full Refresh Sync         | Yes         |                    |
| Incremental Sync          | Yes         |                    |
| SSL Support               | Yes         |                    |
| SSH Tunnel Connection     | Yes         |                    |
| Namespaces                | Yes         | Enabled by default |

## Data type mapping

The connector maps ClickHouse types to JSON Schema types as follows:

| ClickHouse type                                 | JSON Schema type                        |
| :---------------------------------------------- | :-------------------------------------- |
| Bool, UInt8 (boolean context)                   | boolean                                 |
| Int8, Int16, Int32, Int64, UInt16, UInt32       | integer                                 |
| UInt64, Int128, Int256, UInt128, UInt256        | number (numeric string)                 |
| Float32, Float64, Decimal                       | number                                  |
| Date, Date32                                    | string (date format)                    |
| DateTime, DateTime64                            | string (date-time format)               |
| String, FixedString, Enum, UUID, IPv4, IPv6     | string                                  |
| Array                                           | array                                   |

Large integer types (`UInt64`, `Int128`, `Int256`, `UInt128`, `UInt256`) are supported as cursor columns for incremental sync.

## Getting started

### Requirements

1. ClickHouse Server `21.3.10.1` or later.
2. A ClickHouse user with `SELECT` access to the tables you want to replicate.

### Setup guide

#### 1. Make sure your database is accessible from the machine running Airbyte

This is dependent on your networking setup. The easiest way to verify if Airbyte is able to connect to your ClickHouse instance is with the **Test connection** button in the UI.

#### 2. Create a dedicated read-only user (recommended but optional)

This step is optional but highly recommended for better permission control and auditing. Alternatively, you can use an existing user in your database.

To create a dedicated database user, run the following commands against your ClickHouse instance:

```sql
CREATE USER airbyte IDENTIFIED BY 'your_password_here';
```

Then grant it read access to the relevant database:

```sql
GRANT SELECT ON <database_name>.* TO airbyte;
```

You can limit this grant to specific tables instead of the whole database. To replicate data from multiple ClickHouse databases, run the `GRANT` command for each database.

#### 3. Configure the connector in Airbyte

| Field | Description |
| :---- | :---------- |
| **Host** | The hostname or IP address of your ClickHouse server. |
| **Port** | The HTTP interface port. Default is `8123`. Use `8443` if connecting over HTTPS without a reverse proxy. |
| **Database** | The name of the database to sync from. |
| **Username** | The ClickHouse user to authenticate as. |
| **Password** | The password for the user (optional if the user has no password). |
| **SSL** | Enable to connect over HTTPS. Enabled by default. On Airbyte Cloud, SSL is always enforced and this setting is not shown. |
| **JDBC URL Parameters** | Additional parameters appended to the JDBC connection URL, formatted as `key=value` pairs separated by `&`. See the [ClickHouse JDBC driver documentation](https://clickhouse.com/docs/integrations/language-clients/java/jdbc) for available parameters. |

## Connection via SSH Tunnel

Airbyte can connect to a ClickHouse instance via an SSH tunnel. This is useful when the database is not directly accessible (for example, it does not have a public IP address).

When using an SSH tunnel, Airbyte connects to an intermediate server (a bastion server) that has direct access to the database. Airbyte connects to the bastion and then asks the bastion to connect directly to the server.

Using this feature requires additional configuration when creating the source:

1. Configure all fields for the source as you normally would, except **SSH Tunnel Method**.
2. **SSH Tunnel Method** defaults to **No Tunnel** (meaning a direct connection). If you want to use an SSH tunnel, choose **SSH Key Authentication** or **Password Authentication**.
   1. Choose **Key Authentication** if you will be using an RSA private key as your secret for establishing the SSH tunnel (see below for more information on generating this key).
   2. Choose **Password Authentication** if you will be using a password as your secret for establishing the SSH tunnel.
3. **SSH Tunnel Jump Server Host** refers to the intermediate (bastion) server that Airbyte will connect to. This should be a hostname or an IP address.
4. **SSH Connection Port** is the port on the bastion server with which to make the SSH connection. The default port for SSH connections is `22`, so unless you have explicitly changed something, go with the default.
5. **SSH Login Username** is the username that Airbyte should use when connecting to the bastion server. This is NOT the ClickHouse username.
6. If you are using **Password Authentication**, then **SSH Login Password** should be set to the password of the user from the previous step. If you are using **SSH Key Authentication**, leave this blank. Again, this is not the ClickHouse password, but the password for the OS-user that Airbyte is using to perform commands on the bastion.
7. If you are using **SSH Key Authentication**, then **SSH Private Key** should be set to the RSA private key that you are using to create the SSH connection. This should be the full contents of the key file starting with `-----BEGIN RSA PRIVATE KEY-----` and ending with `-----END RSA PRIVATE KEY-----`.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                               | Subject                                                                                                   |
|:--------|:-----------|:-----------------------------------------------------------|:----------------------------------------------------------------------------------------------------------|
| 0.3.1   | 2026-06-29 | [72484](https://github.com/airbytehq/airbyte/pull/72484)   | Add JSON Schema format hints for temporal types (DateTime, Date) and fix documentation URL                |
| 0.3.0   | 2026-03-24 | [75298](https://github.com/airbytehq/airbyte/pull/75298)   | Fold source-clickhouse-strict-encrypt into source-clickhouse                                              |
| 0.2.6   | 2025-11-03 | [66714](https://github.com/airbytehq/airbyte/pull/66714)   | Revert JDBC driver upgrade                                                                                |
| 0.2.5   | 2025-09-25 | [66482](https://github.com/airbytehq/airbyte/pull/66482)   | Upgrade ClickHouse JDBC driver from 0.3.2-patch10 to 0.9.0                                                |
| 0.2.4   | 2025-07-10 | [62912](https://github.com/airbytehq/airbyte/pull/62912)   | Convert to new gradle build flow                                                                          |
| 0.2.3   | 2024-12-18 | [49901](https://github.com/airbytehq/airbyte/pull/49901)   | Use a base image: airbyte/java-connector-base:1.0.0                                                       |
| 0.2.2   | 2024-02-13 | [35235](https://github.com/airbytehq/airbyte/pull/35235)   | Adopt CDK 0.20.4                                                                                          |
| 0.2.1   | 2024-01-24 | [34453](https://github.com/airbytehq/airbyte/pull/34453)   | bump CDK version                                                                                          |
| 0.1.17  | 2023-03-22 | [20760](https://github.com/airbytehq/airbyte/pull/20760)   | Removed redundant date-time datatypes formatting                                                          |
| 0.1.16  | 2023-03-06 | [23455](https://github.com/airbytehq/airbyte/pull/23455)   | For network isolation, source connector accepts a list of hosts it is allowed to connect to               |
| 0.1.15  | 2022-12-14 | [20346](https://github.com/airbytehq/airbyte/pull/20346)   | Consolidate date/time values mapping for JDBC sources                                                     |
| 0.1.14  | 2022-09-27 | [17031](https://github.com/airbytehq/airbyte/pull/17031)   | Added custom jdbc url parameters field                                                                    |
| 0.1.13  | 2022-09-01 | [16238](https://github.com/airbytehq/airbyte/pull/16238)   | Emit state messages more frequently                                                                       |
| 0.1.12  | 2022-08-18 | [14356](https://github.com/airbytehq/airbyte/pull/14356)   | DB Sources: only show a table can sync incrementally if at least one column can be used as a cursor field |
| 0.1.10  | 2022-04-12 | [11514](https://github.com/airbytehq/airbyte/pull/11514)   | Bump mina-sshd from 2.7.0 to 2.8.0                                                                        |
| 0.1.9   | 2022-02-09 | [10214](https://github.com/airbytehq/airbyte/pull/10214)   | Fix exception in case `password` field is not provided                                                    |
| 0.1.8   | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256)   | Add `-XX:+ExitOnOutOfMemoryError` JVM option                                                              |
| 0.1.7   | 2021-12-24 | [8958](https://github.com/airbytehq/airbyte/pull/8958)     | Add support for JdbcType.ARRAY                                                                            |
| 0.1.6   | 2021-12-15 | [8429](https://github.com/airbytehq/airbyte/pull/8429)     | Update titles and descriptions                                                                            |
| 0.1.5   | 2021-12-01 | [8371](https://github.com/airbytehq/airbyte/pull/8371)     | Fixed incorrect handling "\n" in ssh key                                                                  |
| 0.1.4   | 2021-10-20 | [7327](https://github.com/airbytehq/airbyte/pull/7327)     | Added support for connection via SSH tunnel (bastion server)                                              |
| 0.1.3   | 2021-10-20 | [7127](https://github.com/airbytehq/airbyte/pull/7127)     | Added SSL connections support                                                                             |
| 0.1.2   | 2021-08-13 | [4699](https://github.com/airbytehq/airbyte/pull/4699)     | Added json config validator                                                                               |

</details>

## Changelog: source-clickhouse-strict-encrypt

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                                                                                      | Subject                                                                                                                                   |
| :------ | :--------- | :---------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------- |
| 0.2.6   | 2025-11-03 | [66714](https://github.com/airbytehq/airbyte/pull/66714)    | Revert JDBC driver upgrade                                                                                |
| 0.2.5 | 2025-09-25 | [66482](https://github.com/airbytehq/airbyte/pull/66482) | Upgrade ClickHouse JDBC driver from 0.3.2-patch10 to 0.9.0 |
| 0.2.4 | 2025-07-10 | [62913](https://github.com/airbytehq/airbyte/pull/62913) | Convert to new gradle build flow |
| 0.2.0   | 2023-12-18 | [33485](https://github.com/airbytehq/airbyte/pull/33485)                                                          | Remove LEGACY state                                                                                                                       |
| 0.1.17  | 2022-03-22 | [20760](https://github.com/airbytehq/airbyte/pull/20760)                                                          | Removed redundant date-time datatypes formatting                                                                                          |
| 0.1.16  | 2023-03-06 | [23455](https://github.com/airbytehq/airbyte/pull/23455)                                                          | For network isolation, source connector accepts a list of hosts it is allowed to connect to                                               |
| 0.1.15  | 2022-12-14 | [20346](https://github.com/airbytehq/airbyte/pull/20346)                                                          | Consolidate date/time values mapping for JDBC sources                                                                                     |
|         | 2022-10-13 | [15535](https://github.com/airbytehq/airbyte/pull/16238)                                                          | Update incremental query to avoid data missing when new data is inserted at the same time as a sync starts under non-CDC incremental mode |
| 0.1.14  | 2022-09-27 | [17031](https://github.com/airbytehq/airbyte/pull/17031)                                                          | Added custom jdbc url parameters field                                                                                                    |
| 0.1.13  | 2022-09-01 | [16238](https://github.com/airbytehq/airbyte/pull/16238)                                                          | Emit state messages more frequently                                                                                                       |
| 0.1.9   | 2022-08-18 | [14356](https://github.com/airbytehq/airbyte/pull/14356)                                                          | DB Sources: only show a table can sync incrementally if at least one column can be used as a cursor field                                 |
| 0.1.6   | 2022-02-09 | [10214](https://github.com/airbytehq/airbyte/pull/10214)                                                          | Fix exception in case `password` field is not provided                                                                                    |
| 0.1.5   | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256)                                                          | Add `-XX:+ExitOnOutOfMemoryError` JVM option                                                                                              |
| 0.1.3   | 2021-12-29 | [9182](https://github.com/airbytehq/airbyte/pull/9182) [8958](https://github.com/airbytehq/airbyte/pull/8958)     | Add support for JdbcType.ARRAY. Fixed tests                                                                                               |
| 0.1.2   | 2021-12-01 | [8371](https://github.com/airbytehq/airbyte/pull/8371)                                                            | Fixed incorrect handling "\n" in ssh key                                                                                                  |
| 0.1.1   | 2021-10-20 | [7327](https://github.com/airbytehq/airbyte/pull/7327)                                                            | Added support for connection via SSH tunnel (bastion server)                                                                              |
| 0.1.0   | 2021-10-20 | [7127](https://github.com/airbytehq/airbyte/pull/7127)                                                            | Added source-clickhouse-strict-encrypt that supports SSL connections only                                                                 |

</details>
