# TiDB

[TiDB](https://github.com/pingcap/tidb) (/’taɪdiːbi:/, "Ti" stands for Titanium) is an open-source, distributed, NewSQL database that supports Hybrid Transactional and Analytical Processing (HTAP) workloads. It is MySQL compatible and features horizontal scalability, strong consistency, and high availability. Now, everyone can take a free dev trial on [TiDB Cloud](https://en.pingcap.com/tidb-cloud/).

This page guides you through the process of setting up the TiDB destination connector.

## Features

| Feature                       | Supported?\(Yes/No\) | Notes |
| :---------------------------- | :------------------- | :---- |
| Full Refresh Sync             | Yes                  |       |
| Incremental - Append Sync     | Yes                  |       |
| Incremental - Deduped History | Yes                  |       |
| Namespaces                    | Yes                  |       |
| SSH Tunnel Connection         | Yes                  |       |

#### Output Schema

Each stream will be output into its own table in TiDB. Each table will contain 3 columns:

- `_airbyte_ab_id`: a uuid assigned by Airbyte to each event that is processed. The column type in TiDB is `VARCHAR(256)`.
- `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source. The column type in TiDB is `TIMESTAMP(6)`.
- `_airbyte_data`: a json blob representing with the event data. The column type in TiDB is `JSON`.

## Getting Started

### Requirements

To use the TiDB destination, you'll need:

- To sync data to TiDB **with normalization** you should have a TiDB database v5.4.0 or above.

#### Network Access

Make sure your TiDB database can be accessed by Airbyte. If your database is within a VPC, you may need to allow access from the IP you're using to expose Airbyte.

#### **Permissions**

You need a user with `CREATE, INSERT, SELECT, DROP, CREATE VIEW, ALTER` permissions. We highly recommend creating an Airbyte-specific user for this purpose.

To create a dedicated database user, run the following commands against your database:

```sql
CREATE USER 'airbyte'@'%' IDENTIFIED BY 'your_password_here';
```

Then give it access to the relevant database:

```sql
GRANT CREATE, INSERT, SELECT, DROP, CREATE VIEW, ALTER ON <database name>.* TO 'airbyte'@'%';
```

#### Target Database

TiDB doesn't differentiate between a database and schema. A database is essentially a schema where all the tables live in. You will need to choose an existing database or create a new database. This will act as a default database/schema where the tables will be created if the source doesn't provide a namespace.

### Setup the TiDB destination in Airbyte

Config the following information in the TiDB destination:

- **Host**
- **Port**
- **Username**
- **Password**
- **Database**
- **jdbc_url_params** (Optional)

**Note:** When connecting to TiDB Cloud with TLS enabled, you need to specify TLS protocol, such as `enabledTLSProtocols=TLSv1.2` or `enabledTLSProtocols=TLSv1.3` in the JDBC parameters.

### Default JDBC URL Parameters

- `useSSL=false` (unless `ssl` is set to true)
- `requireSSL=false` (unless `ssl` is set to true)
- `verifyServerCertificate=false` (unless `ssl` is set to true)

## Known Limitations

TiDB destination forces all identifier \(table, schema and columns\) names to be lowercase.

## Connection via SSH Tunnel

Airbyte has the ability to connect to a TiDB instance via an SSH Tunnel. The reason you might want to do this because it is not possible \(or against security policy\) to connect to the database directly \(e.g. it does not have a public IP address\).

When using an SSH tunnel, you are configuring Airbyte to connect to an intermediate server \(a.k.a. a bastion sever\) that _does_ have direct access to the database. Airbyte connects to the bastion and then asks the bastion to connect directly to the server.

Using this feature requires additional configuration, when creating the destination. We will talk through what each piece of configuration means.

1. Configure all fields for the destination as you normally would, except `SSH Tunnel Method`.
2. `SSH Tunnel Method` defaults to `No Tunnel` \(meaning a direct connection\). If you want to use an SSH Tunnel choose `SSH Key Authentication` or `Password Authentication`.
   1. Choose `Key Authentication` if you will be using an RSA private key as your secret for establishing the SSH Tunnel \(see below for more information on generating this key\).
   2. Choose `Password Authentication` if you will be using a password as your secret for establishing the SSH Tunnel.
3. `SSH Tunnel Jump Server Host` refers to the intermediate \(bastion\) server that Airbyte will connect to. This should be a hostname or an IP Address.
4. `SSH Connection Port` is the port on the bastion server with which to make the SSH connection. The default port for SSH connections is `22`, so unless you have explicitly changed something, go with the default.
5. `SSH Login Username` is the username that Airbyte should use when connection to the bastion server. This is NOT the TiDB username.
6. If you are using `Password Authentication`, then `SSH Login Username` should be set to the password of the User from the previous step. If you are using `SSH Key Authentication` leave this blank. Again, this is not the TiDB password, but the password for the OS-user that Airbyte is using to perform commands on the bastion.
7. If you are using `SSH Key Authentication`, then `SSH Private Key` should be set to the RSA Private Key that you are using to create the SSH connection. This should be the full contents of the key file starting with `-----BEGIN RSA PRIVATE KEY-----` and ending with `-----END RSA PRIVATE KEY-----`.

## CHANGELOG

| Version | Date       | Pull Request                                               | Subject                                                                                       |
| :------ | :--------- | :--------------------------------------------------------- | :-------------------------------------------------------------------------------------------- |
| 0.1.4   | 2023-06-21 | [\#27555](https://github.com/airbytehq/airbyte/pull/27555) | Reduce image size                                                                             |
| 0.1.3   | 2023-06-05 | [\#27025](https://github.com/airbytehq/airbyte/pull/27025) | Internal code change for future development (install normalization packages inside connector) |
| 0.1.2   | 2023-05-23 | [\#19109](https://github.com/airbytehq/airbyte/pull/19109) | Enabled Append Dedub mode                                                                     |
| 0.1.1   | 2023-04-04 | [\#24604](https://github.com/airbytehq/airbyte/pull/24604) | Support for destination checkpointing                                                         |
| 0.1.0   | 2022-08-12 | [\#15592](https://github.com/airbytehq/airbyte/pull/15592) | Added TiDB destination.                                                                       |
