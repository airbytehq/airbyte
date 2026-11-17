# MySQL

This page guides you through setting up the MySQL destination connector. You can also use this connector with MariaDB.

There are two variants of this connector:

- `destination-mysql` supports both encrypted and unencrypted connections, and has an **SSL Connection** option. Airbyte Open Source uses this variant.
- `destination-mysql-strict-encrypt` only supports encrypted connections, and has no **SSL Connection** option. Airbyte Cloud uses this variant.

Apart from SSL, both variants behave the same way.

## Supported sync modes

| Sync mode | Supported? |
| :--- | :--- |
| [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite) | Yes |
| [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append) | Yes |
| [Full Refresh - Overwrite + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite-deduped) | Yes |
| [Incremental Sync - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append) | Yes |
| [Incremental Sync - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped) | Yes |

## Prerequisites

- A supported MySQL server version:
  - MySQL 8.0 or later to write final tables with [typing and deduping](https://docs.airbyte.com/platform/using-airbyte/core-concepts/typing-deduping). Typing and deduping uses SQL features, such as `JSON_VALUE`, that MySQL 5.7 doesn't support.
  - MySQL 5.7 or later if you turn on **Disable Final Tables** and only write raw tables. The connection check fails on versions earlier than 5.7. The bundled MySQL Connector/J 9.x driver officially supports MySQL 8.0 and later. MySQL 5.7 is no longer supported upstream, but still works with this connector.
- If SSL is enabled (the default, and the only option on Airbyte Cloud), the server must accept TLS 1.2 or TLS 1.3. The driver no longer negotiates TLS 1.0 or TLS 1.1.
- The `local_infile` system variable turned on. See [Enable local_infile](#enable-local_infile).
- A database user with the privileges listed in [Create a database user](#create-a-database-user).
- Network access from Airbyte to your MySQL server. If you use Airbyte Cloud, allow inbound connections from [Airbyte's IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist). If the server is in a private network, you can [connect through an SSH tunnel](#connect-through-an-ssh-tunnel).

### Enable local_infile

The connector loads data with `LOAD DATA LOCAL INFILE`, which requires the server's [`local_infile`](https://dev.mysql.com/doc/refman/8.0/en/server-system-variables.html#sysvar_local_infile) system variable to be `ON`.

When the connector checks the connection, and before it loads data, it reads this variable. If `local_infile` is off, the connector tries to turn it on by running `SET GLOBAL local_infile = true`. This only succeeds if the connector's user has the [`SYSTEM_VARIABLES_ADMIN`](https://dev.mysql.com/doc/refman/8.0/en/privileges-provided.html#priv_system-variables-admin) or `SUPER` privilege. Otherwise, the connection check fails.

If you don't want to give the connector's user that privilege, have an administrator turn the variable on before you set up the destination:

```sql
SET GLOBAL local_infile = true;
```

`SET GLOBAL` doesn't survive a server restart. To keep the setting, also set `local_infile=1` in the server's option file, or use `SET PERSIST` on MySQL 8.0.

### Create a database user

Create a dedicated user for Airbyte. The connector needs these privileges:

- `CREATE` to create databases and tables. The connector runs `CREATE DATABASE IF NOT EXISTS` for the target database, the raw table database, and any namespace a source sends.
- `INSERT` and `SELECT` to load and read data.
- `UPDATE` to mark raw records as loaded after typing and deduping.
- `DELETE` to remove older versions of records in deduplicated streams.
- `INDEX` to create indexes on raw and final tables.
- `ALTER` and `DROP` to swap and drop tables during overwrite syncs and table rebuilds.

The connector writes raw tables to a separate database, `airbyte_internal` by default. Grant the privileges on that database as well as on your target database:

```sql
CREATE USER 'airbyte'@'%' IDENTIFIED BY '<password>';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, INDEX ON <database>.* TO 'airbyte'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, INDEX ON airbyte_internal.* TO 'airbyte'@'%';
```

Replace `<database>` with your target database. If you set **Raw table database** to a different name, grant the privileges on that database instead of `airbyte_internal`. If your sources write to other namespaces, grant the same privileges on those databases, or grant them on `*.*`.

### Choose a target database

MySQL doesn't differentiate between a database and a schema. Choose an existing database or create a new one. The connector writes final tables to this database when the source doesn't provide a namespace. See [Namespace support](#namespace-support).

## Set up the MySQL destination

Provide the following information:

- **Host**: The hostname or IP address of your MySQL server.
- **Port**: The port of your MySQL server. The default is `3306`.
- **DB Name**: The target database.
- **User** and **Password**: The credentials of the user you created.
- **SSL Connection** (`destination-mysql` only): Encrypts the connection with TLS. On by default. When on, the connector requires TLS but doesn't verify the server certificate (`verifyServerCertificate=false`). The strict-encrypt variant always behaves as if this option is on.
- **JDBC URL Params** (optional): Extra JDBC URL parameters, formatted as `key=value` pairs separated by `&`. For example, `key1=value1&key2=value2`.
- **SSH Tunnel Method** (optional): See [Connect through an SSH tunnel](#connect-through-an-ssh-tunnel).
- **Raw table database** (optional): The database for raw tables. Defaults to `airbyte_internal`.
- **Disable Final Tables** (optional): Writes only raw tables and skips typing and deduping. The connector doesn't guarantee that raw table columns stay the same between versions.

### Default JDBC URL parameters

The connector sets the following JDBC URL parameters. You can't override them with **JDBC URL Params**:

- `useSSL=true` (unless SSL is turned off)
- `requireSSL=true` (unless SSL is turned off)
- `verifyServerCertificate=false` (unless SSL is turned off)
- `zeroDateTimeBehavior=convertToNull`
- `allowLoadLocalInfile=true`
- `connectionTimeZone=LOCAL`. The connector writes and reads `_airbyte_extracted_at` in the connector's own time zone. Don't set `connectionTimeZone` or its alias `serverTimezone` in **JDBC URL Params**.

## Connect through an SSH tunnel

If you can't connect to the database directly, for example because it has no public IP address, the connector can connect through an SSH tunnel. Airbyte connects to an intermediate (bastion) server that has direct access to the database, and the bastion server forwards the connection to MySQL.

1. Configure all other fields as you normally would.
2. Set **SSH Tunnel Method**. The default is **No Tunnel**, which connects directly. To use a tunnel, choose one of these:
   - **SSH Key Authentication** to authenticate to the bastion server with an RSA private key.
   - **Password Authentication** to authenticate to the bastion server with a password.
3. **SSH Tunnel Jump Server Host**: The hostname or IP address of the bastion server.
4. **SSH Connection Port**: The SSH port on the bastion server. The default is `22`.
5. **SSH Login Username**: The operating system user on the bastion server. This isn't the MySQL user.
6. If you chose **Password Authentication**, set **Password** to that operating system user's password. This isn't the MySQL password.
7. If you chose **SSH Key Authentication**, set **SSH Private Key** to the full contents of the RSA private key file, starting with `-----BEGIN RSA PRIVATE KEY-----` and ending with `-----END RSA PRIVATE KEY-----`.

## Namespace support

This destination supports [namespaces](https://docs.airbyte.com/platform/using-airbyte/core-concepts/namespaces). Because MySQL doesn't differentiate between a database and a schema, each namespace maps to a MySQL database. The configured database acts as the default namespace.

## Limitations

- The connector converts all identifiers (database, table, and column names) to lowercase. The MySQL documentation recommends [using lowercase names](https://dev.mysql.com/doc/refman/8.0/en/identifier-case-sensitivity.html) for portability, because case sensitivity depends on the `lower_case_table_names` system variable and the operating system.
- The connector shortens database and table names longer than 44 characters. It keeps the beginning and end of the name and joins them with `__`.

## Troubleshooting

- **`Cannot create a PoolableConnectionFactory` or an SSL handshake error**: Check that the server, for example an older Amazon RDS MySQL instance, offers TLS 1.2 or later. Turn on a supported TLS version on the server. You can't configure the driver to fall back to TLS 1.0 or 1.1.
- **`The DB user provided to airbyte was unable to switch on the local_infile attribute`**: `local_infile` is off and the connector's user can't turn it on. See [Enable local_infile](#enable-local_infile).
- **`Your MySQL version ... is not compatible with Airbyte`**: The server runs a version earlier than MySQL 5.7. Upgrade the server.
- **`Access denied. Please check your configuration`**: The user is missing a privilege, or can't access the target or raw table database. See [Create a database user](#create-a-database-user).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| :------ | :--------- | :------------------------------------------------------- | :-------------------------------------------------------------------------------------------------- |
| 1.1.2 | 2026-10-27 | [89768](https://github.com/airbytehq/airbyte/pull/89768) | Upgrade MySQL Connector/J 8.0.22 to 9.6.0 and pin `connectionTimeZone=LOCAL` so typing no longer skips records on servers west of UTC (MySQL and MySQL Strict Encrypt destinations). |
| 1.1.1 | 2025-08-04 | [63736](https://github.com/airbytehq/airbyte/pull/63736) | Use MySQL/MariaDB compatible timestamp format |
| 1.1.0 | 2025-03-25 | [50861](https://github.com/airbytehq/airbyte/pull/50861) | add support for mariadb |
| 1.0.4 | 2025-03-24 | [56355](https://github.com/airbytehq/airbyte/pull/56355) | Upgrade to airbyte/java-connector-base:2.0.1 to be M4 compatible. |
| 1.0.3 | 2024-12-18 | [49865](https://github.com/airbytehq/airbyte/pull/49865) | Use a base image: airbyte/java-connector-base:1.0.0 |
| 1.0.3 | 2024-06-26 | [40566](https://github.com/airbytehq/airbyte/pull/40566) | Remove strict-encrypt variant |
| 1.0.2 | 2024-06-26 | [40553](https://github.com/airbytehq/airbyte/pull/40553) | Convert prod code to kotlin |
| 1.0.1 | 2024-06-25 | [40513](https://github.com/airbytehq/airbyte/pull/40513) | Improve error reporting for "access denied" error |
| 1.0.0 | 2024-04-26 | [37322](https://github.com/airbytehq/airbyte/pull/37322) | Remove normalization and upgrade to DV2 output format |
| 0.3.1 | 2024-04-12 | [36926](https://github.com/airbytehq/airbyte/pull/36926) | Upgrade to Kotlin CDK |
| 0.3.0 | 2023-12-18 | [33468](https://github.com/airbytehq/airbyte/pull/33468) | Upgrade to latest Java CDK |
| 0.2.0 | 2023-06-27 | [27781](https://github.com/airbytehq/airbyte/pull/27781) | License Update: Elv2 |
| 0.1.21 | 2022-09-14 | [15668](https://github.com/airbytehq/airbyte/pull/15668) | Wrap logs in AirbyteLogMessage |
| 0.1.20 | 2022-06-17 | [13864](https://github.com/airbytehq/airbyte/pull/13864) | Updated stacktrace format for any trace message errors |
| 0.1.19 | 2022-05-17 | [12820](https://github.com/airbytehq/airbyte/pull/12820) | Improved 'check' operation performance |
| 0.1.18 | 2022-02-25 | [10421](https://github.com/airbytehq/airbyte/pull/10421) | Refactor JDBC parameters handling |
| 0.1.17 | 2022-02-16 | [10362](https://github.com/airbytehq/airbyte/pull/10362) | Add jdbc_url_params support for optional JDBC parameters |
| 0.1.16 | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256) | Add `-XX:+ExitOnOutOfMemoryError` JVM option |
| 0.1.15 | 2021-12-01 | [8371](https://github.com/airbytehq/airbyte/pull/8371) | Fixed incorrect handling "\n" in ssh key |
| 0.1.14  | 2021-11-08 | [#7719](https://github.com/airbytehq/airbyte/pull/7719)  | Improve handling of wide rows by buffering records based on their byte size rather than their count |
| 0.1.13  | 2021-09-28 | [\#6506](https://github.com/airbytehq/airbyte/pull/6506) | Added support for MySQL destination via TLS/SSL                                                     |
| 0.1.12  | 2021-09-24 | [\#6317](https://github.com/airbytehq/airbyte/pull/6317) | Added option to connect to DB via SSH                                                               |
| 0.1.11  | 2021-07-30 | [\#5125](https://github.com/airbytehq/airbyte/pull/5125) | Enable `additionalPropertities` in spec.json                                                        |
| 0.1.10  | 2021-07-28 | [\#5026](https://github.com/airbytehq/airbyte/pull/5026) | Add sanitized json fields in raw tables to handle quotes in column names                            |
| 0.1.7   | 2021-07-09 | [\#4651](https://github.com/airbytehq/airbyte/pull/4651) | Switch normalization flag on so users can use normalization.                                        |
| 0.1.6   | 2021-07-03 | [\#4531](https://github.com/airbytehq/airbyte/pull/4531) | Added normalization for MySQL.                                                                      |
| 0.1.5   | 2021-07-03 | [\#3973](https://github.com/airbytehq/airbyte/pull/3973) | Added `AIRBYTE_ENTRYPOINT` for kubernetes support.                                                  |
| 0.1.4   | 2021-07-03 | [\#3290](https://github.com/airbytehq/airbyte/pull/3290) | Switched to get states from destination instead of source.                                          |
| 0.1.3   | 2021-07-03 | [\#3387](https://github.com/airbytehq/airbyte/pull/3387) | Fixed a bug for message length checking.                                                            |
| 0.1.2   | 2021-07-03 | [\#3327](https://github.com/airbytehq/airbyte/pull/3327) | Fixed LSEP unicode characters.                                                                      |
| 0.1.1   | 2021-07-03 | [\#3289](https://github.com/airbytehq/airbyte/pull/3289) | Added support for outputting messages.                                                              |
| 0.1.0   | 2021-05-06 | [\#3242](https://github.com/airbytehq/airbyte/pull/3242) | Added MySQL destination.                                                                            |

</details>
