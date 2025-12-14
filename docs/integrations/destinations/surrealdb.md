# SurrealDB

[SurrealDB](https://github.com/surrealdb/surrealdb) is an end-to-end cloud-native database designed for modern applications, including web, mobile, serverless, Jamstack, backend, and traditional applications. With SurrealDB, you can simplify your database and API infrastructure, reduce development time, and build secure, performant apps quickly and cost-effectively.

This page guides you through the process of setting up the SurrealDB destination connector.

## Features

| Feature                        | Supported?\(Yes/No\) | Notes |
| :----------------------------- | :------------------- | :---- |
| Full Refresh Sync              | Yes                  |       |
| Incremental - Append Sync      | No                  |       |
| Incremental - Append + Deduped | No                  |       |
| Namespaces                     | No                  |       |

#### Output Schema

Each stream will be output into its own table in SurrealDB. Each table will contain 3 columns:

- `_airbyte_raw_id`: a uuid assigned by Airbyte to each event that is processed. The column type in SurrealDB is `string`.
The connector use this as the ID of each record in the destination SurrealDB table.
- `_airbyte_extracted_at`: a timestamp representing when the event was pulled from the data source. The column type in SurrealDB is `datetime`.
- `_airbyte_data`: a json blob representing with the event data. The column type in SurrealDB is `object`.

## Getting Started

### Requirements

To use the SurrealDB destination, you'll need SurrealDB v2.2.0 or above.

#### Network Access

Make sure your SurrealDB database can be accessed by Airbyte. If your database is within a VPC, you may need to allow access from the IP you're using to expose Airbyte.

#### **Permissions**

You need a user with `DEFINE TABLE, DEFINE INDEX, UPSERT, SELECT, REMOVE` permissions. We highly recommend creating an Airbyte-specific user for this purpose.

To create a dedicated database user, run the following commands against your database:

```sql
DEFINE USER airbyte ON ROOT PASSWORD "your_password_here" ROLES OWNER;
```

#### Target Database

SurrealDB doesn't differentiate between a database and schema. A database is essentially a schema where all the tables live in. You will need to choose an existing database or create a new database. This will act as a default database/schema where the tables will be created if the source doesn't provide a namespace.

### Setup the SurrealDB destination in Airbyte

Config the following information in the SurrealDB destination:

- **Host**
- **Port**
- **Username** (`Token` or pair of `Username`/`Password` is required)
- **Password** (`Token` or pair of `Username`/`Password` is required)
- **Namespace**
- **Database**
- **Token** (`Token` or pair of `Username`/`Password` is required)

## Known Limitations

SurrealDB destination forces all identifier \(table, schema and columns\) names to be lowercase.

## Connection via SSH Tunnel

Airbyte has the ability to connect to a SurrealDB instance via an SSH Tunnel. The reason you might want to do this because it is not possible \(or against security policy\) to connect to the database directly \(e.g. it does not have a public IP address\).

When using an SSH tunnel, you are configuring Airbyte to connect to an intermediate server \(a.k.a. a bastion sever\) that _does_ have direct access to the database. Airbyte connects to the bastion and then asks the bastion to connect directly to the server.

Using this feature requires additional configuration, when creating the destination. We will talk through what each piece of configuration means.

1. Configure all fields for the destination as you normally would, except `SSH Tunnel Method`.
2. `SSH Tunnel Method` defaults to `No Tunnel` \(meaning a direct connection\). If you want to use an SSH Tunnel choose `SSH Key Authentication` or `Password Authentication`.
   1. Choose `Key Authentication` if you will be using an RSA private key as your secret for establishing the SSH Tunnel \(see below for more information on generating this key\).
   2. Choose `Password Authentication` if you will be using a password as your secret for establishing the SSH Tunnel.
3. `SSH Tunnel Jump Server Host` refers to the intermediate \(bastion\) server that Airbyte will connect to. This should be a hostname or an IP Address.
4. `SSH Connection Port` is the port on the bastion server with which to make the SSH connection. The default port for SSH connections is `22`, so unless you have explicitly changed something, go with the default.
5. `SSH Login Username` is the username that Airbyte should use when connection to the bastion server. This is NOT the SurrealDB username.
6. If you are using `Password Authentication`, then `SSH Login Username` should be set to the password of the User from the previous step. If you are using `SSH Key Authentication` leave this blank. Again, this is not the SurrealDB password, but the password for the OS-user that Airbyte is using to perform commands on the bastion.
7. If you are using `SSH Key Authentication`, then `SSH Private Key` should be set to the RSA Private Key that you are using to create the SSH connection. This should be the full contents of the key file starting with `-----BEGIN RSA PRIVATE KEY-----` and ending with `-----END RSA PRIVATE KEY-----`.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                               | Subject                                                                                       |
| :------ | :--------- | :--------------------------------------------------------- | :-------------------------------------------------------------------------------------------- |
| 0.1.1 | 2025-12-09 | [67830](https://github.com/airbytehq/airbyte/pull/67830) | Update dependencies |
| 0.1.0   | 2025-05-09 | [\#59742](https://github.com/airbytehq/airbyte/pull/59742) | Added SurrealDB destination.                                                                       |

</details>
