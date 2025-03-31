# Oracle DB

## Features

| Feature                        | Supported?\(Yes/No\) | Notes                                                                 |
| :----------------------------- | :------------------- | :-------------------------------------------------------------------- |
| Full Refresh Sync              | Yes                  |                                                                       |
| Incremental - Append Sync      | Yes                  |                                                                       |
| Incremental - Append + Deduped | Yes                  |                                                                       |
| Namespaces                     | Yes                  |                                                                       |
| Basic Normalization            | Yes                  | Doesn't support for nested json yet                                   |
| SSH Tunnel Connection          | Yes                  |                                                                       |
| Encryption                     | Yes                  | Support Native Network Encryption (NNE) as well as TLS using SSL cert |

## Output Schema

By default, each stream will be output into its own table in Oracle. Each table will contain 3 columns:

- `_AIRBYTE_AB_ID`: a uuid assigned by Airbyte to each event that is processed. The column type in Oracle is `VARCHAR(64)`.
- `_AIRBYTE_EMITTED_AT`: a timestamp representing when the event was pulled from the data source. The column type in Oracle is `TIMESTAMP WITH TIME ZONE`.
- `_AIRBYTE_DATA`: a json blob representing with the event data. The column type in Oracles is `NCLOB`.

Enabling normalization will also create normalized, strongly typed tables.

## Getting Started \(Airbyte Cloud\)

The Oracle connector is currently in Alpha on Airbyte Cloud. Only TLS encrypted connections to your DB can be made from Airbyte Cloud. Other than that, follow the open-source instructions below.

## Getting Started \(Airbyte Open Source\)

#### Requirements

To use the Oracle destination, you'll need:

- An Oracle server version 21 or above

#### Network Access

Make sure your Oracle database can be accessed by Airbyte. If your database is within a VPC, you may need to allow access from the IP you're using to expose Airbyte.

#### **Permissions**

As Airbyte namespaces allows us to store data into different schemas, we have different scenarios and list of required permissions:

| Login user   | Destination user   | Required permissions                                          | Comment                                                                    |
| :----------- | :----------------- | :------------------------------------------------------------ | :------------------------------------------------------------------------- |
| DBA User     | Any user           | -                                                             |                                                                            |
| Regular user | Same user as login | Create, drop and write table, create session                  |                                                                            |
| Regular user | Any existing user  | Create, drop and write ANY table, create session              | Grants can be provided on a system level by DBA or by target user directly |
| Regular user | Not existing user  | Create, drop and write ANY table, create user, create session | Grants should be provided on a system level by DBA                         |

We highly recommend creating an Airbyte-specific user for this purpose.

### Setup the Oracle destination in Airbyte

You should now have all the requirements needed to configure Oracle as a destination in the UI. You'll need the following information to configure the Oracle destination:

- **Host**
- **Port**
- **Username**
- **Password**
- **Database**
- **Connection via SSH Tunnel**

Airbyte has the ability to connect to a Oracle instance via an SSH Tunnel. The reason you might want to do this because it is not possible \(or against security policy\) to connect to the database directly \(e.g. it does not have a public IP address\).

When using an SSH tunnel, you are configuring Airbyte to connect to an intermediate server \(a.k.a. a bastion sever\) that _does_ have direct access to the database. Airbyte connects to the bastion and then asks the bastion to connect directly to the server.

Using this feature requires additional configuration, when creating the source. We will talk through what each piece of configuration means.

1. Configure all fields for the source as you normally would, except `SSH Tunnel Method`.
2. `SSH Tunnel Method` defaults to `No Tunnel` \(meaning a direct connection\). If you want to use an SSH Tunnel choose `SSH Key Authentication` or `Password Authentication`.
   1. Choose `Key Authentication` if you will be using an RSA private key as your secret for establishing the SSH Tunnel \(see below for more information on generating this key\).
   2. Choose `Password Authentication` if you will be using a password as your secret for establishing the SSH Tunnel.
3. `SSH Tunnel Jump Server Host` refers to the intermediate \(bastion\) server that Airbyte will connect to. This should be a hostname or an IP Address.
4. `SSH Connection Port` is the port on the bastion server with which to make the SSH connection. The default port for SSH connections is `22`, so unless you have explicitly changed something, go with the default.
5. `SSH Login Username` is the username that Airbyte should use when connection to the bastion server. This is NOT the Oracle username.
6. If you are using `Password Authentication`, then `SSH Login Username` should be set to the password of the User from the previous step. If you are using `SSH Key Authentication` leave this blank. Again, this is not the Oracle password, but the password for the OS-user that Airbyte is using to perform commands on the bastion.
7. If you are using `SSH Key Authentication`, then `SSH Private Key` should be set to the RSA Private Key that you are using to create the SSH connection. This should be the full contents of the key file starting with `-----BEGIN RSA PRIVATE KEY-----` and ending with `-----END RSA PRIVATE KEY-----`.

## Encryption Options

Airbyte has the ability to connect to the Oracle source with 3 network connectivity options:

1. `Unencrypted` the connection will be made using the TCP protocol. In this case, all data over the network will be transmitted in unencrypted form.
2. `Native network encryption` gives you the ability to encrypt database connections, without the configuration overhead of TCP / IP and SSL / TLS and without the need to open and listen on different ports. In this case, the _SQLNET.ENCRYPTION_CLIENT_
   option will always be set as _REQUIRED_ by default: The client or server will only accept encrypted traffic, but the user has the opportunity to choose an `Encryption algorithm` according to the security policies he needs.
3. `TLS Encrypted` (verify certificate) - if this option is selected, data transfer will be transferred using the TLS protocol, taking into account the handshake procedure and certificate verification. To use this option, insert the content of the certificate issued by the server into the `SSL PEM file` field

## Changelog

<details>
  <summary>Expand to review</summary>

| Version     | Date       | Pull Request                                               | Subject                                                                                             |
| :---------- | :--------- | :--------------------------------------------------------- | :-------------------------------------------------------------------------------------------------- |
| 1.0.0       | 2024-04-11 | [\#36048](https://github.com/airbytehq/airbyte/pull/36048) | Removes Normalization, updates to V2 Raw Table Format                                               |
| 0.2.0       | 2023-06-27 | [\#27781](https://github.com/airbytehq/airbyte/pull/27781) | License Update: Elv2                                                                                |
| 0.1.19      | 2022-07-26 | [\#10719](https://github.com/airbytehq/airbyte/pull/)      | Destination Oracle: added custom JDBC parameters support.                                           |
| 0.1.18      | 2022-07-14 | [\#14618](https://github.com/airbytehq/airbyte/pull/14618) | Removed additionalProperties: false from JDBC destination connectors                                |
| unpublished | 2022-05-17 | [12820](https://github.com/airbytehq/airbyte/pull/12820)   | Improved 'check' operation performance                                                              |
| 0.1.16      | 2022-04-06 | [11514](https://github.com/airbytehq/airbyte/pull/11514)   | Bump mina-sshd from 2.7.0 to 2.8.0                                                                  |
| 0.1.15      | 2022-02-25 | [10421](https://github.com/airbytehq/airbyte/pull/10421)   | Refactor JDBC parameters handling and remove DBT support                                            |
| 0.1.14      | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256)   | (unpublished) Add `-XX:+ExitOnOutOfMemoryError` JVM option                                          |
| 0.1.13      | 2021-12-29 | [\#9177](https://github.com/airbytehq/airbyte/pull/9177)   | Update connector fields title/description                                                           |
| 0.1.12      | 2021-11-08 | [\#7719](https://github.com/airbytehq/airbyte/pull/7719)   | Improve handling of wide rows by buffering records based on their byte size rather than their count |
| 0.1.10      | 2021-10-08 | [\#6893](https://github.com/airbytehq/airbyte/pull/6893)   | 🎉 Destination Oracle: implemented connection encryption                                            |
| 0.1.9       | 2021-10-06 | [\#6611](https://github.com/airbytehq/airbyte/pull/6611)   | 🐛 Destination Oracle: maxStringLength should be 128                                                |
| 0.1.8       | 2021-09-28 | [\#6370](https://github.com/airbytehq/airbyte/pull/6370)   | Add SSH Support for Oracle Destination                                                              |
| 0.1.7       | 2021-08-30 | [\#5746](https://github.com/airbytehq/airbyte/pull/5746)   | Use default column name for raw tables                                                              |
| 0.1.6       | 2021-08-23 | [\#5542](https://github.com/airbytehq/airbyte/pull/5542)   | Remove support for Oracle 11g to allow normalization                                                |
| 0.1.5       | 2021-08-10 | [\#5307](https://github.com/airbytehq/airbyte/pull/5307)   | 🐛 Destination Oracle: Fix destination check for users without dba role                             |
| 0.1.4       | 2021-07-30 | [\#5125](https://github.com/airbytehq/airbyte/pull/5125)   | Enable `additionalPropertities` in spec.json                                                        |
| 0.1.3       | 2021-07-21 | [\#3555](https://github.com/airbytehq/airbyte/pull/3555)   | Partial Success in BufferedStreamConsumer                                                           |
| 0.1.2       | 2021-07-20 | [\#4874](https://github.com/airbytehq/airbyte/pull/4874)   | Require `sid` instead of `database` in connector specification                                      |

</details>
