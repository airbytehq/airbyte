# ClickHouse

The ClickHouse source supports Full Refresh and Incremental syncs. You can choose whether the connector copies only new or updated data, or all rows in the tables and columns you set up for replication, every time a sync runs.

This connector is built on top of the source-jdbc code base and uses the [ClickHouse JDBC driver](https://github.com/ClickHouse/clickhouse-jdbc). For more information, see the [ClickHouse JDBC documentation](https://clickhouse.com/docs/integrations/language-clients/java/jdbc).

## Output schema

The ClickHouse source does not alter the schema present in your database. Depending on the destination connected to this source, however, the schema may be altered. See the destination's documentation for more details.

### Features

| Feature                       | Supported   | Notes              |
| :---------------------------- | :---------- | :----------------- |
| Full Refresh Sync             | Yes         |                    |
| Incremental Sync              | Yes         |                    |
| SSL Support                   | Yes         |                    |
| SSH Tunnel Connection         | Yes         |                    |
| Namespaces                    | Yes         | Enabled by default |

## Prerequisites

1. ClickHouse server version `21.3.10.1` or later.
2. A ClickHouse user with `SELECT` access to the tables you want to replicate.

## Setup guide

### Step 1: Confirm network access

Make sure the machine running Airbyte can reach your ClickHouse instance. The easiest way to verify connectivity is with the **Test Connection** button in the Airbyte UI.

The connector communicates with ClickHouse over the HTTP interface. The default port is `8123` for unencrypted connections and `8443` for SSL-encrypted connections.

### Step 2: Create a read-only user (recommended)

Creating a dedicated user is optional but recommended for better permission control and auditing. You can also use an existing ClickHouse user.

To create a dedicated user, run the following SQL against your ClickHouse server:

```sql
CREATE USER airbyte IDENTIFIED BY 'your_password_here';
```

Grant read access to the relevant database:

```sql
GRANT SELECT ON <database_name>.* TO airbyte;
```

To limit access to specific tables, replace `<database_name>.*` with `<database_name>.<table_name>`.

To replicate data from multiple databases, run the `GRANT` command for each database. You need to set up a separate Airbyte source for each database.

### Step 3: Configure the connector in Airbyte

Provide the following configuration values:

| Field | Description |
| :--- | :--- |
| **Host** | The hostname or IP address of your ClickHouse server. |
| **Port** | The HTTP interface port. Default is `8123`, or `8443` for SSL. |
| **Database** | The name of the database to replicate. |
| **Username** | The ClickHouse user to authenticate as. |
| **Password** | The password for the user. |
| **SSL Connection** | Enable to encrypt the connection using SSL. Enabled by default. On Airbyte Cloud, SSL is always enforced. |
| **JDBC URL Parameters** | Additional parameters appended to the JDBC connection URL, formatted as `key=value` pairs separated by `&`. |

## Connection via SSH tunnel

Airbyte can connect to a ClickHouse instance through an SSH tunnel. This is useful when the database is not publicly accessible or when security policy prohibits direct connections.

When using an SSH tunnel, Airbyte connects to an intermediate server (a bastion host) that has direct access to the database. Airbyte connects to the bastion, and the bastion connects to ClickHouse.

To configure an SSH tunnel:

1. Configure all fields for the source as you normally would, except **SSH Tunnel Method**.
2. Set **SSH Tunnel Method** to **SSH Key Authentication** or **Password Authentication**.
   1. Choose **Key Authentication** to use an RSA private key.
   2. Choose **Password Authentication** to use a password.
3. Set **SSH Tunnel Jump Server Host** to the hostname or IP address of the bastion server.
4. Set **SSH Connection Port** to the SSH port on the bastion server. The default SSH port is `22`.
5. Set **SSH Login Username** to the OS username on the bastion server. This is not the ClickHouse username.
6. If you are using **Password Authentication**, set **SSH Login Password** to the password for the OS user on the bastion server. If you are using **SSH Key Authentication**, leave this blank.
7. If you are using **SSH Key Authentication**, set **SSH Private Key** to the full contents of the RSA private key file, starting with `-----BEGIN RSA PRIVATE KEY-----` and ending with `-----END RSA PRIVATE KEY-----`.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                               | Subject                                                                                                   |
|:--------|:-----------|:-----------------------------------------------------------|:----------------------------------------------------------------------------------------------------------|
| 0.3.0   | 2026-03-24 | [75298](https://github.com/airbytehq/airbyte/pull/75298)   | Fold strict-encrypt variant into main connector; SSL is now enforced automatically in cloud mode          |
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
| 0.1.4   | 2021-10-20 | [7327](https://github.com/airbytehq/airbyte/pull/7327)     | Added support for connection via SSH tunnel                                                               |
| 0.1.3   | 2021-10-20 | [7127](https://github.com/airbytehq/airbyte/pull/7127)     | Added SSL connections support                                                                             |
| 0.1.2   | 2021-08-13 | [4699](https://github.com/airbytehq/airbyte/pull/4699)     | Added json config validator                                                                               |

</details>

## Changelog: source-clickhouse-strict-encrypt

:::note
The `source-clickhouse-strict-encrypt` connector was merged into `source-clickhouse` in version 0.3.0. SSL is now enforced automatically in Airbyte Cloud. This changelog is preserved for historical reference.
:::

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                                                                                  | Subject                                                                                                                                   |
| :------ | :--------- | :------------------------------------------------------------------------------------------------------------ | :---------------------------------------------------------------------------------------------------------------------------------------- |
| 0.2.6   | 2025-11-03 | [66714](https://github.com/airbytehq/airbyte/pull/66714)                                                      | Revert JDBC driver upgrade                                                                                                                |
| 0.2.5   | 2025-09-25 | [66482](https://github.com/airbytehq/airbyte/pull/66482)                                                      | Upgrade ClickHouse JDBC driver from 0.3.2-patch10 to 0.9.0                                                                                |
| 0.2.4   | 2025-07-10 | [62913](https://github.com/airbytehq/airbyte/pull/62913)                                                      | Convert to new gradle build flow                                                                                                          |
| 0.2.0   | 2023-12-18 | [33485](https://github.com/airbytehq/airbyte/pull/33485)                                                      | Remove LEGACY state                                                                                                                       |
| 0.1.17  | 2022-03-22 | [20760](https://github.com/airbytehq/airbyte/pull/20760)                                                      | Removed redundant date-time datatypes formatting                                                                                          |
| 0.1.16  | 2023-03-06 | [23455](https://github.com/airbytehq/airbyte/pull/23455)                                                      | For network isolation, source connector accepts a list of hosts it is allowed to connect to                                               |
| 0.1.15  | 2022-12-14 | [20346](https://github.com/airbytehq/airbyte/pull/20346)                                                      | Consolidate date/time values mapping for JDBC sources                                                                                     |
|         | 2022-10-13 | [15535](https://github.com/airbytehq/airbyte/pull/16238)                                                      | Update incremental query to avoid data missing when new data is inserted at the same time as a sync starts under non-CDC incremental mode |
| 0.1.14  | 2022-09-27 | [17031](https://github.com/airbytehq/airbyte/pull/17031)                                                      | Added custom jdbc url parameters field                                                                                                    |
| 0.1.13  | 2022-09-01 | [16238](https://github.com/airbytehq/airbyte/pull/16238)                                                      | Emit state messages more frequently                                                                                                       |
| 0.1.9   | 2022-08-18 | [14356](https://github.com/airbytehq/airbyte/pull/14356)                                                      | DB Sources: only show a table can sync incrementally if at least one column can be used as a cursor field                                 |
| 0.1.6   | 2022-02-09 | [10214](https://github.com/airbytehq/airbyte/pull/10214)                                                      | Fix exception in case `password` field is not provided                                                                                    |
| 0.1.5   | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256)                                                      | Add `-XX:+ExitOnOutOfMemoryError` JVM option                                                                                              |
| 0.1.3   | 2021-12-29 | [9182](https://github.com/airbytehq/airbyte/pull/9182) [8958](https://github.com/airbytehq/airbyte/pull/8958) | Add support for JdbcType.ARRAY. Fixed tests                                                                                               |
| 0.1.2   | 2021-12-01 | [8371](https://github.com/airbytehq/airbyte/pull/8371)                                                        | Fixed incorrect handling "\n" in ssh key                                                                                                  |
| 0.1.1   | 2021-10-20 | [7327](https://github.com/airbytehq/airbyte/pull/7327)                                                        | Added support for connection via SSH tunnel                                                                                               |
| 0.1.0   | 2021-10-20 | [7127](https://github.com/airbytehq/airbyte/pull/7127)                                                        | Added source-clickhouse-strict-encrypt that supports SSL connections only                                                                 |

</details>
