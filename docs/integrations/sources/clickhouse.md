# ClickHouse

The ClickHouse source reads tables from a single ClickHouse database over the HTTP interface, using the [ClickHouse JDBC driver](https://github.com/ClickHouse/clickhouse-jdbc). It supports full refresh and incremental syncs.

## Features

| Feature               | Supported | Notes                                                                    |
| :-------------------- | :-------- | :----------------------------------------------------------------------- |
| Full refresh sync     | Yes       |                                                                          |
| Incremental sync      | Yes       | Cursor-based. The connector doesn't read the ClickHouse replication log. |
| Replicate deletes     | No        | Rows deleted in ClickHouse remain in the destination.                    |
| SSL                   | Yes       | Enabled by default. Always enforced in Airbyte Cloud.                    |
| SSH tunnel connection | Yes       |                                                                          |
| Namespaces            | Yes       | Each stream keeps its ClickHouse database name as its namespace.         |

## Prerequisites

- A ClickHouse server that Airbyte can reach on its HTTP or HTTPS port. The connector uses the HTTP interface (ports `8123` and `8443` by default), not the native protocol port (`9000` or `9440`).
- A ClickHouse user with `SELECT` access to the tables you want to replicate. Airbyte tests this connector against ClickHouse Server 22.5.

## Set up the ClickHouse source

### 1. Create a dedicated read-only user

This step is optional but recommended, so you can audit and limit what Airbyte reads. To create a user with read-only access to one database, run these statements as an administrator:

```sql
CREATE USER airbyte IDENTIFIED WITH sha256_password BY 'your_password_here';
GRANT SELECT ON <database name>.* TO airbyte;
```

You can narrow the grant to individual tables, for example `GRANT SELECT ON <database name>.<table name> TO airbyte`.

Each source reads from one database. To replicate tables from several databases on the same server, grant access to each database, and create one source per database.

### 2. Configure the source in Airbyte

| Field                              | Description                                                                                                                                                                                                                             |
| :--------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Host**                           | Hostname of the ClickHouse server or cluster endpoint. Don't include a scheme or port.                                                                                                                                                  |
| **Port**                           | Port of the HTTP interface. Defaults to `8123`, which is the plaintext HTTP port. If you leave **SSL Connection** enabled, use the HTTPS port instead, which is `8443` in ClickHouse Cloud and in a default self-managed configuration. |
| **Database**                       | The database to replicate from, such as `default`.                                                                                                                                                                                      |
| **Username** and **Password**      | The ClickHouse credentials Airbyte authenticates with.                                                                                                                                                                                  |
| **JDBC URL Parameters (Advanced)** | Extra [ClickHouse JDBC driver properties](https://clickhouse.com/docs/integrations/language-clients/java/jdbc) as `key=value` pairs joined by `&`. The connector appends them to the JDBC URL it builds.                                |
| **SSL Connection**                 | Connects over HTTPS. Enabled by default. Airbyte Cloud always connects over HTTPS and doesn't show this option.                                                                                                                         |

When SSL is enabled, the connector connects with the driver's `sslmode=none`, which encrypts the connection but doesn't validate the server certificate. To validate certificates, add the corresponding driver properties, such as `sslmode=strict` and `sslrootcert=<path>`, to **JDBC URL Parameters**.

### 3. Connect through an SSH tunnel (optional)

Use an SSH tunnel when Airbyte can't reach ClickHouse directly, for example when the server has no public address. Airbyte connects to an intermediate bastion host, which forwards the connection to ClickHouse.

1. Configure every other field as you normally would.
2. Set **SSH Tunnel Method** to **SSH Key Authentication** or **Password Authentication**. The default, **No Tunnel**, connects directly.
3. For **SSH Tunnel Jump Server Host**, enter the hostname or IP address of the bastion host.
4. For **SSH Connection Port**, enter the bastion's SSH port. This is `22` unless you changed it.
5. For **SSH Login Username**, enter the operating system user on the bastion. This isn't your ClickHouse username.
6. If you chose **Password Authentication**, enter that operating system user's password in **Password**. This isn't your ClickHouse password.
7. If you chose **SSH Key Authentication**, paste the full private key into **SSH Private Key**, including the `-----BEGIN RSA PRIVATE KEY-----` and `-----END RSA PRIVATE KEY-----` lines.

## Streams and sync modes

The connector discovers the tables in the configured database. It always excludes the `system` and `information_schema` databases. ClickHouse primary keys are reported as each stream's source-defined primary key, so you can select **Incremental | Append + Deduped** for tables that have one.

For incremental syncs, choose a cursor column with a date, time, timestamp, integer, decimal, floating point, or string type. Boolean, array, and binary columns can't be cursors. During long syncs the connector emits sync state about every 10,000 records, so an interrupted sync resumes near where it stopped.

The connector reads whole tables through the HTTP interface without server-side streaming, because the ClickHouse JDBC driver ignores the JDBC fetch size.

## Data types

The connector maps ClickHouse types to Airbyte types as follows. Nullable columns keep their underlying type.

| ClickHouse type                                         | Airbyte type               |
| :------------------------------------------------------ | :------------------------- |
| `Date`, `Date32`                                        | date                       |
| `DateTime`, `DateTime64`                                | timestamp without timezone |
| `Int8` through `Int64`, `UInt8` through `UInt32`        | integer                    |
| `Float32`, `Float64`, `Decimal`                         | number                     |
| `Array`                                                 | array                      |
| Binary types                                            | base64-encoded string      |
| Everything else, including `Map`, `Tuple`, and `Nested` | string                     |

Since version 0.3.1, temporal columns are emitted as Airbyte date and timestamp types instead of unformatted strings. Version 0.4.0 declares this change as breaking. If a sync fails with a schema evolution error between string and timestamp, follow the [migration guide](/integrations/sources/clickhouse-migrations).

The connector emits the wide integer types `UInt64`, `Int128`, `UInt128`, `Int256`, and `UInt256` as numeric values rather than strings, so you can use them as cursor columns.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                               | Subject                                                                                                   |
|:--------|:-----------|:-----------------------------------------------------------|:----------------------------------------------------------------------------------------------------------|
| 0.4.0   | 2026-08-12 | [81633](https://github.com/airbytehq/airbyte/pull/81633)   | **Breaking**: Declare temporal column typing as breaking. Connections with schema evolution errors must follow the [migration guide](/integrations/sources/clickhouse-migrations)    |
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
| 0.1.15  | 2023-01-18 | [20346](https://github.com/airbytehq/airbyte/pull/20346)   | Consolidate date/time values mapping for JDBC sources                                                     |
| 0.1.14  | 2022-09-27 | [17031](https://github.com/airbytehq/airbyte/pull/17031)   | Added custom jdbc url parameters field                                                                    |
| 0.1.13  | 2022-09-01 | [16238](https://github.com/airbytehq/airbyte/pull/16238)   | Emit state messages more frequently                                                                       |
| 0.1.12  | 2022-08-18 | [14356](https://github.com/airbytehq/airbyte/pull/14356)   | DB Sources: only show a table can sync incrementally if at least one column can be used as a cursor field |
| 0.1.10  | 2022-04-12 | [11514](https://github.com/airbytehq/airbyte/pull/11514)   | Bump mina-sshd from 2.7.0 to 2.8.0                                                                        |
| 0.1.9   | 2022-02-16 | [10214](https://github.com/airbytehq/airbyte/pull/10214)   | Fix exception in case `password` field is not provided                                                    |
| 0.1.8   | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256)   | Add `-XX:+ExitOnOutOfMemoryError` JVM option                                                              |
| 0.1.7   | 2021-12-24 | [8958](https://github.com/airbytehq/airbyte/pull/8958)     | Add support for JdbcType.ARRAY                                                                            |
| 0.1.6   | 2021-12-16 | [8429](https://github.com/airbytehq/airbyte/pull/8429)     | Update titles and descriptions                                                                            |
| 0.1.5   | 2021-12-03 | [8371](https://github.com/airbytehq/airbyte/pull/8371)     | Fixed incorrect handling "\n" in ssh key                                                                  |
| 0.1.4   | 2021-10-26 | [7327](https://github.com/airbytehq/airbyte/pull/7327)     | Added support for connection via SSH tunnel (bastion server)                                              |
| 0.1.3   | 2021-10-25 | [7127](https://github.com/airbytehq/airbyte/pull/7127)     | Added SSL connections support                                                                             |
| 0.1.2   | 2021-08-02 | [4699](https://github.com/airbytehq/airbyte/pull/4699)     | Added json config validator                                                                               |

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
| 0.1.6   | 2022-02-09 | [\#10214](https://github.com/airbytehq/airbyte/pull/10214)                                                        | Fix exception in case `password` field is not provided                                                                                    |
| 0.1.5   | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256)                                                          | Add `-XX:+ExitOnOutOfMemoryError` JVM option                                                                                              |
| 0.1.3   | 2021-12-29 | [\#9182](https://github.com/airbytehq/airbyte/pull/9182) [\#8958](https://github.com/airbytehq/airbyte/pull/8958) | Add support for JdbcType.ARRAY. Fixed tests                                                                                               |
| 0.1.2   | 2021-12-01 | [\#8371](https://github.com/airbytehq/airbyte/pull/8371)                                                          | Fixed incorrect handling "\n" in ssh key                                                                                                  |
| 0.1.1   | 20.10.2021 | [\#7327](https://github.com/airbytehq/airbyte/pull/7327)                                                          | Added support for connection via SSH tunnel(aka Bastion server).                                                                          |
| 0.1.0   | 20.10.2021 | [\#7127](https://github.com/airbytehq/airbyte/pull/7127)                                                          | Added source-clickhouse-strict-encrypt that supports SSL connections only.                                                                |

</details>
