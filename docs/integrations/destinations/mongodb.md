# MongoDB

## Features

| Feature                        | Supported?\(Yes/No\) | Notes |
| :----------------------------- | :------------------- | :---- |
| Full Refresh Sync              | Yes                  |       |
| Incremental - Append Sync      | Yes                  |       |
| Incremental - Append + Deduped | No                   |       |
| Namespaces                     | Yes                  |       |

## Prerequisites

- For Airbyte Open Source users using the [Postgres](https://docs.airbyte.com/integrations/sources/postgres) source connector, [upgrade](https://docs.airbyte.com/operator-guides/upgrading-airbyte/) your Airbyte platform to version `v0.40.0-alpha` or newer and upgrade your MongoDB connector to version `0.1.6` or newer

## Output Schema for `destination-mongodb`

Each stream will be output into its own collection in MongoDB. Each collection will contain 3 fields:

- `_id`: an identifier assigned to each document that is processed. The filed type in MongoDB is `String`.
- `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source. The field type in MongoDB is `Timestamp`.
- `_airbyte_data`: a json blob representing with the event data. The field type in MongoDB is `Object`.

## Getting Started \(Airbyte Cloud\)

Airbyte Cloud only supports connecting to your MongoDB instance with TLS encryption. Other than that, you can proceed with the open-source instructions below.

## Getting Started \(Airbyte Open Source\)

#### Requirements

To use the MongoDB destination, you'll need:

- A MongoDB server

#### **Permissions**

You need a MongoDB user that can create collections and write documents. We highly recommend creating an Airbyte-specific user for this purpose.

#### Target Database

You will need to choose an existing database or create a new database that will be used to store synced data from Airbyte.

### Setup the MongoDB destination in Airbyte

You should now have all the requirements needed to configure MongoDB as a destination in the UI. You'll need the following information to configure the MongoDB destination:

- **Standalone MongoDb instance**
  - Host: URL of the database
  - Port: Port to use for connecting to the database
  - TLS: indicates whether to create encrypted connection
- **Replica Set**
  - Server addresses: the members of a replica set
  - Replica Set: A replica set name
- **MongoDb Atlas Cluster**
  - Cluster URL: URL of a cluster to connect to
- **Database**
- **Username**
- **Password**

For more information regarding configuration parameters, please see [MongoDb Documentation](https://docs.mongodb.com/drivers/java/sync/v4.3/fundamentals/connection/).

### Connection via SSH Tunnel

Airbyte has the ability to connect to an MongoDB instance via an SSH Tunnel.
The reason you might want to do this because it is not possible \(or against security policy\) to connect to your MongoDB instance directly \(e.g. it does not have a public IP address\).

When using an SSH tunnel, you are configuring Airbyte to connect to an intermediate server \(a.k.a. a bastion sever\) that _does_ have direct access to the MongoDB instance.
Airbyte connects to the bastion and then asks the bastion to connect directly to the server.

Using this feature requires additional configuration, when creating the source. We will talk through what each piece of configuration means.

1. Configure all fields for the source as you normally would, except `SSH Tunnel Method`.
2. `SSH Tunnel Method` defaults to `No Tunnel` \(meaning a direct connection\). If you want to use an SSH Tunnel choose `SSH Key Authentication` or `Password Authentication`.
   1. Choose `Key Authentication` if you will be using an RSA private key as your secret for establishing the SSH Tunnel \(see below for more information on generating this key\).
   2. Choose `Password Authentication` if you will be using a password as your secret for establishing the SSH Tunnel.
3. `SSH Tunnel Jump Server Host` refers to the intermediate \(bastion\) server that Airbyte will connect to. This should be a hostname or an IP Address.
4. `SSH Connection Port` is the port on the bastion server with which to make the SSH connection. The default port for SSH connections is `22`, so unless you have explicitly changed something, go with the default.
5. `SSH Login Username` is the username that Airbyte should use when connection to the bastion server. This is NOT the TiDB username.
6. If you are using `Password Authentication`, then `SSH Login Username` should be set to the password of the User from the previous step. If you are using `SSH Key Authentication` TiDB password, but the password for the OS-user that Airbyte is using to perform commands on the bastion.
7. If you are using `SSH Key Authentication`, then `SSH Private Key` should be set to the RSA Private Key that you are using to create the SSH connection. This should be the full contents of the key file starting with `-----BEGIN RSA PRIVATE KEY-----` and ending with `-----END RSA PRIVATE KEY-----`.

## Naming Conventions

The following information comes from the [MongoDB Limits and Thresholds](https://docs.mongodb.com/manual/reference/limits/) documentation.

#### Database Name Case Sensitivity

Since database names are case insensitive in MongoDB, database names cannot differ only by the case of the characters.

#### Restrictions on Database Names for Windows

For MongoDB deployments running on Windows, database names cannot contain any of the following characters: /. "$_&lt;&gt;:\|?_

Also database names cannot contain the null character.

#### Restrictions on Database Names for Unix and Linux Systems

For MongoDB deployments running on Unix and Linux systems, database names cannot contain any of the following characters: /. "$

Also database names cannot contain the null character.

#### Length of Database Names

Database names cannot be empty and must have fewer than 64 characters.

#### Restriction on Collection Names

Collection names should begin with an underscore or a letter character, and cannot:

- contain the $.
- be an empty string \(e.g. ""\).
- contain the null character.
- begin with the system. prefix. \(Reserved for internal use.\)

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                    |
| :------ | :--------- | :------------------------------------------------------- | :--------------------------------------------------------- |
| 0.2.0   | 2023-06-27 | [27781](https://github.com/airbytehq/airbyte/pull/27781) | License Update: Elv2                                       |
| 0.1.9   | 2022-11-08 | [18892](https://github.com/airbytehq/airbyte/pull/18892) | Adds check for TLS flag                                    |
| 0.1.8   | 2022-10-26 | [18280](https://github.com/airbytehq/airbyte/pull/18280) | Adds SSH tunneling                                         |
| 0.1.7   | 2022-09-02 | [16025](https://github.com/airbytehq/airbyte/pull/16025) | Remove additionalProperties:false from spec                |
| 0.1.6   | 2022-08-02 | [15211](https://github.com/airbytehq/airbyte/pull/15211) | Fix standard mode                                          |
| 0.1.5   | 2022-07-27 | [14561](https://github.com/airbytehq/airbyte/pull/14561) | Change Airbyte Id from MD5 to SHA256                       |
| 0.1.4   | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256) | (unpublished) Add `-XX:+ExitOnOutOfMemoryError` JVM option |
| 0.1.3   | 2021-12-30 | [8809](https://github.com/airbytehq/airbyte/pull/8809)   | Update connector fields title/description                  |
| 0.1.2   | 2021-10-18 | [6945](https://github.com/airbytehq/airbyte/pull/6945)   | Create a secure-only MongoDb destination                   |
| 0.1.1   | 2021-09-29 | [6536](https://github.com/airbytehq/airbyte/pull/6536)   | Destination MongoDb: added support via TLS/SSL             |

</details>