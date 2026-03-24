# ClickHouse

## Overview

The ClickHouse source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This connector is built using the [ClickHouse JDBC driver](https://github.com/ClickHouse/clickhouse-jdbc) (v0.9.8). It connects to ClickHouse over the [HTTP interface](https://clickhouse.com/docs/interfaces/http) — port 8123 by default, or port 8443 when SSL is enabled.

### Output schema

The ClickHouse source does not alter the schema present in your database. Depending on the destination connected to this source, however, the schema may be altered. See the destination's documentation for more details.

### Features

| Feature                       | Supported   | Notes              |
| :---------------------------- | :---------- | :----------------- |
| Full Refresh Sync             | Yes         |                    |
| Incremental Sync              | Yes         |                    |
| Replicate Incremental Deletes | Coming soon |                    |
| Logical Replication (WAL)     | Coming soon |                    |
| SSL Support                   | Yes         | Enabled by default |
| SSH Tunnel Connection         | Yes         |                    |
| Namespaces                    | Yes         | Enabled by default |

## Getting started

### Requirements

1. ClickHouse Server `21.3.10.1` or later.
2. A dedicated read-only Airbyte user with access to all tables needed for replication.

### Setup guide

#### 1. Make sure your database is accessible from the machine running Airbyte

This is dependent on your networking setup. The easiest way to verify if Airbyte is able to connect to your ClickHouse instance is via the check connection tool in the UI.

#### 2. Create a dedicated read-only user with access to the relevant tables (recommended but optional)

This step is optional but highly recommended for better permission control and auditing. Alternatively, you can use Airbyte with an existing user in your database.

To create a dedicated database user, run the following commands against your database:

```sql
CREATE USER airbyte IDENTIFIED BY 'your_password_here';
```

Then give it read access to the relevant database:

```sql
GRANT SELECT ON <database_name>.* TO airbyte;
```

You can limit this grant to specific tables instead of the whole database. To replicate data from multiple ClickHouse databases, re-run the command above for each database, but you'll need to set up a separate source for each one.

Your database user should now be ready for use with Airbyte.

#### 3. Configure the source in Airbyte

Configure the following fields in the Airbyte UI:

| Field | Required | Default | Description |
| :--- | :--- | :--- | :--- |
| **Host** | Yes | | The hostname or IP address of your ClickHouse server. |
| **Port** | Yes | `8123` | The HTTP interface port. Use `8123` for unencrypted connections, or `8443` for SSL. |
| **Database** | Yes | | The name of the database to sync. |
| **Username** | Yes | | The database username. |
| **Password** | No | | The password for the database user. |
| **SSL Connection** | No | `true` | Encrypt data using SSL. When enabled, the connector uses the `https` protocol. |
| **JDBC URL Parameters** | No | | Additional properties to pass to the JDBC URL string, formatted as `key=value` pairs separated by `&` — for example, `socket_timeout=300000&connection_timeout=60000`. |

## Connection via SSH tunnel

Airbyte can connect to a ClickHouse instance via an SSH tunnel. This is useful when you cannot connect to the database directly — for example, if it does not have a public IP address or your security policy prohibits direct connections.

When using an SSH tunnel, Airbyte connects to an intermediate server (a bastion server) that has direct access to the database. Airbyte connects to the bastion and then asks the bastion to connect directly to the database.

To configure an SSH tunnel:

1. Configure all fields for the source as you normally would, except **SSH Tunnel Method**.
2. **SSH Tunnel Method** defaults to **No Tunnel** (meaning a direct connection). To use an SSH tunnel, choose **SSH Key Authentication** or **Password Authentication**.
   1. Choose **Key Authentication** if you will be using an RSA private key as your secret for establishing the SSH tunnel.
   2. Choose **Password Authentication** if you will be using a password as your secret for establishing the SSH tunnel.
3. **SSH Tunnel Jump Server Host** is the hostname or IP address of the bastion server that Airbyte will connect to.
4. **SSH Connection Port** is the port on the bastion server for the SSH connection. The default port for SSH connections is `22`.
5. **SSH Login Username** is the username that Airbyte should use when connecting to the bastion server. This is NOT the ClickHouse username.
6. If you are using **Password Authentication**, then **SSH Login Password** should be set to the password of the user from the previous step. If you are using **SSH Key Authentication**, leave this blank. This is the password for the OS user on the bastion, not the ClickHouse password.
7. If you are using **SSH Key Authentication**, then **SSH Private Key** should be set to the RSA private key that you are using to create the SSH connection. This should be the full contents of the key file starting with `-----BEGIN RSA PRIVATE KEY-----` and ending with `-----END RSA PRIVATE KEY-----`.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                                | Subject                                                                                                   |
|:--------|:-----------|:------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------|
| 0.3.0-rc.3 | 2026-03-24 | [75260](https://github.com/airbytehq/airbyte/pull/75260) | Remove legacy `sslmode=none` JDBC parameter incompatible with 0.9.7+ driver |
| 0.3.0-rc.2 | 2026-03-19 | [75226](https://github.com/airbytehq/airbyte/pull/75226) | Upgrade ClickHouse JDBC driver from 0.9.5 to 0.9.8 |
| 0.3.0-rc.1 | 2026-02-03 | [72395](https://github.com/airbytehq/airbyte/pull/72395) | Upgrade ClickHouse JDBC driver to 0.9.5 with custom type mapping |
| 0.2.6 | 2025-11-03 | [66714](https://github.com/airbytehq/airbyte/pull/66714) | Revert JDBC driver upgrade |
| 0.2.5 | 2025-09-25 | [66482](https://github.com/airbytehq/airbyte/pull/66482) | Upgrade ClickHouse JDBC driver from 0.3.2-patch10 to 0.9.0 |
| 0.2.4 | 2025-07-10 | [62912](https://github.com/airbytehq/airbyte/pull/62912) | Convert to new gradle build flow |
| 0.2.3 | 2024-12-18 | [49901](https://github.com/airbytehq/airbyte/pull/49901) | Use a base image: airbyte/java-connector-base:1.0.0 |
| 0.2.2 | 2024-02-13 | [35235](https://github.com/airbytehq/airbyte/pull/35235) | Adopt CDK 0.20.4 |
| 0.2.1 | 2024-01-24 | [34453](https://github.com/airbytehq/airbyte/pull/34453) | bump CDK version |
| 0.1.17 | 2023-03-22 | [20760](https://github.com/airbytehq/airbyte/pull/20760) | Removed redundant date-time datatypes formatting |
| 0.1.16 | 2023-03-06 | [23455](https://github.com/airbytehq/airbyte/pull/23455) | For network isolation, source connector accepts a list of hosts it is allowed to connect to |
| 0.1.15 | 2022-12-14 | [20346](https://github.com/airbytehq/airbyte/pull/20346) | Consolidate date/time values mapping for JDBC sources |
| 0.1.14 | 2022-09-27 | [17031](https://github.com/airbytehq/airbyte/pull/17031) | Added custom jdbc url parameters field |
| 0.1.13 | 2022-09-01 | [16238](https://github.com/airbytehq/airbyte/pull/16238) | Emit state messages more frequently |
| 0.1.12 | 2022-08-18 | [14356](https://github.com/airbytehq/airbyte/pull/14356) | DB Sources: only show a table can sync incrementally if at least one column can be used as a cursor field |
| 0.1.10 | 2022-04-12 | [11514](https://github.com/airbytehq/airbyte/pull/11514) | Bump mina-sshd from 2.7.0 to 2.8.0 |
| 0.1.9   | 2022-02-09 | [10214](https://github.com/airbytehq/airbyte/pull/10214)  | Fix exception in case `password` field is not provided                                                    |
| 0.1.8   | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256)    | Add `-XX:+ExitOnOutOfMemoryError` JVM option                                                              |
| 0.1.7   | 2021-12-24 | [8958](https://github.com/airbytehq/airbyte/pull/8958)    | Add support for JdbcType.ARRAY                                                                            |
| 0.1.6   | 2021-12-15 | [8429](https://github.com/airbytehq/airbyte/pull/8429)    | Update titles and descriptions                                                                            |
| 0.1.5   | 2021-12-01 | [8371](https://github.com/airbytehq/airbyte/pull/8371)    | Fixed incorrect handling "\n" in ssh key                                                                  |
| 0.1.4   | 2021-10-20 | [7327](https://github.com/airbytehq/airbyte/pull/7327)    | Added support for connection via SSH tunnel                                                               |
| 0.1.3   | 2021-10-20 | [7127](https://github.com/airbytehq/airbyte/pull/7127)    | Added SSL connections support                                                                             |
| 0.1.2   | 2021-08-13 | [4699](https://github.com/airbytehq/airbyte/pull/4699)    | Added json config validator                                                                               |

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
| 0.1.6   | 2022-02-09 | [10214](https://github.com/airbytehq/airbyte/pull/10214)                                                        | Fix exception in case `password` field is not provided                                                                                    |
| 0.1.5   | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256)                                                          | Add `-XX:+ExitOnOutOfMemoryError` JVM option                                                                                              |
| 0.1.3   | 2021-12-29 | [9182](https://github.com/airbytehq/airbyte/pull/9182) [8958](https://github.com/airbytehq/airbyte/pull/8958) | Add support for JdbcType.ARRAY. Fixed tests                                                                                               |
| 0.1.2   | 2021-12-01 | [8371](https://github.com/airbytehq/airbyte/pull/8371)                                                          | Fixed incorrect handling "\n" in ssh key                                                                                                  |
| 0.1.1   | 2021-10-20 | [7327](https://github.com/airbytehq/airbyte/pull/7327)                                                          | Added support for connection via SSH tunnel                                                                                               |
| 0.1.0   | 2021-10-20 | [7127](https://github.com/airbytehq/airbyte/pull/7127)                                                          | Added source-clickhouse-strict-encrypt that supports SSL connections only                                                                 |

</details>
