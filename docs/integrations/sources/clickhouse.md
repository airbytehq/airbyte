# ClickHouse

## Overview

The ClickHouse source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This Clickhouse source connector is built on top of the source-jdbc code base and is configured to rely on JDBC v0.3.1 standard drivers provided by ClickHouse [here](https://github.com/ClickHouse/clickhouse-jdbc) as described in ClickHouse documentation [here](https://clickhouse.tech/docs/en/interfaces/jdbc/).

#### Resulting schema

The ClickHouse source does not alter the schema present in your warehouse. Depending on the destination connected to this source, however, the schema may be altered. See the destination's documentation for more details.

### Features

| Feature                       | Supported   | Notes              |
| :---------------------------- | :---------- | :----------------- |
| Full Refresh Sync             | Yes         |                    |
| Incremental Sync              | Yes         |                    |
| Replicate Incremental Deletes | Coming soon |                    |
| Logical Replication \(WAL\)   | Coming soon |                    |
| SSL Support                   | Yes         |                    |
| SSH Tunnel Connection         | Yes         |                    |
| Namespaces                    | Yes         | Enabled by default |

## Getting started

### Requirements

1. ClickHouse Server `21.3.10.1` or later.
2. Create a dedicated read-only Airbyte user with access to all tables needed for replication

### Setup guide

#### 1. Make sure your database is accessible from the machine running Airbyte

This is dependent on your networking setup. The easiest way to verify if Airbyte is able to connect to your ClickHouse instance is via the check connection tool in the UI.

#### 2. Create a dedicated read-only user with access to the relevant tables \(Recommended but optional\)

This step is optional but highly recommended to allow for better permission control and auditing. Alternatively, you can use Airbyte with an existing user in your database.

To create a dedicated database user, run the following commands against your database:

```sql
CREATE USER 'airbyte'@'%' IDENTIFIED BY 'your_password_here';
```

Then give it access to the relevant schema:

```sql
GRANT SELECT ON <database name>.* TO 'airbyte'@'%';
```

You can limit this grant down to specific tables instead of the whole database. Note that to replicate data from multiple ClickHouse databases, you can re-run the command above to grant access to all the relevant schemas, but you'll need to set up multiple sources connecting to the same db on multiple schemas.

Your database user should now be ready for use with Airbyte.

## Connection via SSH Tunnel

Airbyte has the ability to connect to a Clickhouse instance via an SSH Tunnel. The reason you might want to do this because it is not possible \(or against security policy\) to connect to the database directly \(e.g. it does not have a public IP address\).

When using an SSH tunnel, you are configuring Airbyte to connect to an intermediate server \(a.k.a. a bastion sever\) that _does_ have direct access to the database. Airbyte connects to the bastion and then asks the bastion to connect directly to the server.

Using this feature requires additional configuration, when creating the source. We will talk through what each piece of configuration means.

1. Configure all fields for the source as you normally would, except `SSH Tunnel Method`.
2. `SSH Tunnel Method` defaults to `No Tunnel` \(meaning a direct connection\). If you want to use an SSH Tunnel choose `SSH Key Authentication` or `Password Authentication`.
   1. Choose `Key Authentication` if you will be using an RSA private key as your secret for establishing the SSH Tunnel \(see below for more information on generating this key\).
   2. Choose `Password Authentication` if you will be using a password as your secret for establishing the SSH Tunnel.
3. `SSH Tunnel Jump Server Host` refers to the intermediate \(bastion\) server that Airbyte will connect to. This should be a hostname or an IP Address.
4. `SSH Connection Port` is the port on the bastion server with which to make the SSH connection. The default port for SSH connections is `22`, so unless you have explicitly changed something, go with the default.
5. `SSH Login Username` is the username that Airbyte should use when connection to the bastion server. This is NOT the Clickhouse username.
6. If you are using `Password Authentication`, then `SSH Login Username` should be set to the password of the User from the previous step. If you are using `SSH Key Authentication` leave this blank. Again, this is not the Clickhouse password, but the password for the OS-user that Airbyte is using to perform commands on the bastion.
7. If you are using `SSH Key Authentication`, then `SSH Private Key` should be set to the RSA Private Key that you are using to create the SSH connection. This should be the full contents of the key file starting with `-----BEGIN RSA PRIVATE KEY-----` and ending with `-----END RSA PRIVATE KEY-----`.

## Changelog

| Version | Date       | Pull Request                                               | Subject                                                                                                   |
| :------ | :--------- | :--------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------- |
| 0.2.2   | 2024-02-13 | [35235](https://github.com/airbytehq/airbyte/pull/35235)   | Adopt CDK 0.20.4                                                                                          |
| 0.2.1   | 2024-01-24 | [34453](https://github.com/airbytehq/airbyte/pull/34453)   | bump CDK version                                                                                          |
| 0.1.17  | 2023-03-22 | [20760](https://github.com/airbytehq/airbyte/pull/20760)   | Removed redundant date-time datatypes formatting                                                          |
| 0.1.16  | 2023-03-06 | [23455](https://github.com/airbytehq/airbyte/pull/23455)   | For network isolation, source connector accepts a list of hosts it is allowed to connect to               |
| 0.1.15  | 2022-12-14 | [20436](https://github.com/airbytehq/airbyte/pull/20346)   | Consolidate date/time values mapping for JDBC sources                                                     |
| 0.1.14  | 2022-09-27 | [17031](https://github.com/airbytehq/airbyte/pull/17031)   | Added custom jdbc url parameters field                                                                    |
| 0.1.13  | 2022-09-01 | [16238](https://github.com/airbytehq/airbyte/pull/16238)   | Emit state messages more frequently                                                                       |
| 0.1.12  | 2022-08-18 | [14356](https://github.com/airbytehq/airbyte/pull/14356)   | DB Sources: only show a table can sync incrementally if at least one column can be used as a cursor field |
| 0.1.10  | 2022-04-12 | [11729](https://github.com/airbytehq/airbyte/pull/11514)   | Bump mina-sshd from 2.7.0 to 2.8.0                                                                        |
| 0.1.9   | 2022-02-09 | [\#10214](https://github.com/airbytehq/airbyte/pull/10214) | Fix exception in case `password` field is not provided                                                    |
| 0.1.8   | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256)   | Add `-XX:+ExitOnOutOfMemoryError` JVM option                                                              |
| 0.1.7   | 2021-12-24 | [\#8958](https://github.com/airbytehq/airbyte/pull/8958)   | Add support for JdbcType.ARRAY                                                                            |
| 0.1.6   | 2021-12-15 | [\#8429](https://github.com/airbytehq/airbyte/pull/8429)   | Update titles and descriptions                                                                            |
| 0.1.5   | 2021-12-01 | [\#8371](https://github.com/airbytehq/airbyte/pull/8371)   | Fixed incorrect handling "\n" in ssh key                                                                  |
| 0.1.4   | 20.10.2021 | [\#7327](https://github.com/airbytehq/airbyte/pull/7327)   | Added support for connection via SSH tunnel(aka Bastion server).                                          |
| 0.1.3   | 20.10.2021 | [\#7127](https://github.com/airbytehq/airbyte/pull/7127)   | Added SSL connections support.                                                                            |
| 0.1.2   | 13.08.2021 | [\#4699](https://github.com/airbytehq/airbyte/pull/4699)   | Added json config validator.                                                                              |

## CHANGELOG source-clickhouse-strict-encrypt

| Version | Date       | Pull Request                                                                                                      | Subject                                                                                                                                   |
| :------ | :--------- | :---------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------- |
| 0.2.0   | 2023-12-18 | [33485](https://github.com/airbytehq/airbyte/pull/33485)                                                          | Remove LEGACY state                                                                                                                       |
| 0.1.17  | 2022-03-22 | [20760](https://github.com/airbytehq/airbyte/pull/20760)                                                          | Removed redundant date-time datatypes formatting                                                                                          |
| 0.1.16  | 2023-03-06 | [23455](https://github.com/airbytehq/airbyte/pull/23455)                                                          | For network isolation, source connector accepts a list of hosts it is allowed to connect to                                               |
| 0.1.15  | 2022-12-14 | [20436](https://github.com/airbytehq/airbyte/pull/20346)                                                          | Consolidate date/time values mapping for JDBC sources                                                                                     |
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
