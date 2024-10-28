# Source Oracle

:::info
Airbyte Enterprise Connectors are a selection of premium connectors available exclusively for Airbyte Self-Managed Enterprise and Airbyte Teams customers. These connectors, built and maintained by the Airbyte team, provide enhanced capabilities and support for critical enterprise systems. To learn more about enterprise connectors, please [talk to our sales team](https://airbyte.com/company/talk-to-sales).
:::


Airbyte's incubating Oracle enterprise source connector offers the following features:

- Incremental as well as Full Refresh
  [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes), providing
  flexibility in how data is delivered to your destination.
  Note that incremental syncs using [Change Data Capture (CDC)](https://docs.airbyte.com/understanding-airbyte/cdc) are not yet supported.
- Reliable replication at any table size with
  [checkpointing](https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/#state--checkpointing)
  and chunking of database reads.

The required minimum platform version is v0.58.0 for this connector.

## Features

| Feature                       | Supported   | Notes              |
| :---------------------------- | :---------- | :----------------- |
| Full Refresh Sync             | Yes         |                    |
| Incremental Sync - Append     | Yes         |                    |
| Replicate Incremental Deletes | Coming soon |                    |
| CDC (Change Data Capture)     | Coming soon |                    |
| SSL Support                   | Yes         |                    |
| SSH Tunnel Connection         | Yes         |                    |
| Namespaces                    | Yes         | Enabled by default |

The Oracle source does not alter the schema present in your database. Depending on the destination
connected to this source, however, the schema may be altered. See the destination's documentation
for more details.

## Getting Started

### Requirements

1. Oracle DB version 23ai, 21c or 19c.
2. Dedicated read-only Airbyte user with access to all tables needed for replication.

#### 1. Make sure your database is accessible from the machine running Airbyte

This is dependent on your networking setup. The easiest way to verify if Airbyte is able to connect
to your Oracle instance is by testing the connection in the UI.

#### 2. Create a dedicated read-only user with access to the relevant tables (Recommended but optional)

This step is optional but highly recommended to allow for better permission control and auditing. Alternatively, you can use Airbyte with an existing user in your database.

To create a dedicated database user, run the following commands against your database:

```sql
CREATE USER airbyte IDENTIFIED BY <your_password_here>;
GRANT CREATE SESSION TO airbyte;
```

Next, grant the user read-only access to the relevant tables. The simplest way is to grant read access to all tables in the schema as follows:

```sql
GRANT SELECT ANY TABLE TO airbyte;
```

Or you can be more granular:

```sql
GRANT SELECT ON "<schema_a>"."<table_1>" TO airbyte;
GRANT SELECT ON "<schema_b>"."<table_2>" TO airbyte;
```

Your database user should now be ready for use with Airbyte.

#### 3. Include the schemas Airbyte should look at when configuring the Airbyte Oracle Source.

Case sensitive. Defaults to the upper-cased user if empty. If the user does not have access to the configured schemas, no tables will be discovered and the connection test will fail.

### Airbyte Cloud

On Airbyte Cloud, only secured connections to your Oracle instance are supported in source
configuration.
Note that while the connector is still incubating, this may not yet be actively enforced.
You may configure your connection to either use SSL or an available encryption scheme, or by using an SSH tunnel.

## Oracle encryption schemes

The connection to the Oracle database instance can be established using the following schemes:

1. `Unencrypted` connections will be made using the TCP protocol where all data over the network will be transmitted unencrypted.
   Airbyte Cloud will only allow this if an SSH tunnel is also used.
2. `Native Network Encryption (NNE)` gives you the ability to encrypt database connections without
   the configuration overhead of SSL / TLS and without the need to open and listen on different ports.
   In this case, the _SQLNET.ENCRYPTION_CLIENT_ option will always be set as _REQUIRED_ by default:
   the client or server will only accept encrypted traffic, but gives you the opportunity to choose
   an `Encryption Algorithm` according to the security policies you require.
3. `TLS Encrypted (verify certificate)` gives you the ability to encrypt database connections using
   the TLS protocol, taking into account the handshake procedure and certificate verification.
   To use this option, insert the content of the certificate issued by the server into the
   `SSL PEM file` field.

## Connection to Oracle via an SSH Tunnel

Airbyte has the ability to connect to an Oracle instance via an SSH Tunnel. The reason you might want
to do this because it is not possible (or against security policy) to connect to the database
directly (e.g. it does not have a public IP address).

When using an SSH tunnel, you are configuring Airbyte to connect to an intermediate server (a.k.a.
a bastion sever) that _does_ have direct access to the database. Airbyte connects to the bastion
and then asks the bastion to connect directly to the server.

Using this feature requires additional configuration, when creating the source. We will talk through
what each piece of configuration means.

1. Configure all fields for the source as you normally would, except `SSH Tunnel Method`.

2. `SSH Tunnel Method` defaults to `No Tunnel` (meaning a direct connection). If you want to use
   an SSH Tunnel choose `SSH Key Authentication` or `Password Authentication`.

   1. Choose `Key Authentication` if you will be using an RSA private key as your secret for
      establishing the SSH Tunnel (see below for more information on generating this key).

   2. Choose `Password Authentication` if you will be using a password as your secret for
      establishing the SSH Tunnel.

3. `SSH Tunnel Jump Server Host` refers to the intermediate (bastion) server that Airbyte will
   connect to. This should be a hostname or an IP Address.

4. `SSH Connection Port` is the port on the bastion server with which to make the SSH connection.
   The default port for SSH connections is `22`, so unless you have explicitly changed something,
   go with the default.

5. `SSH Login Username` is the username that Airbyte should use when connection to the bastion
   server. This is NOT the Oracle username.

6. If you are using `Password Authentication`, then `SSH Login Username` should be set to the
   password of the User from the previous step. If you are using `SSH Key Authentication` leave this
   blank. Again, this is not the Oracle password, but the password for the OS-user that Airbyte is
   using to perform commands on the bastion.

7. If you are using `SSH Key Authentication`, then `SSH Private Key` should be set to the RSA
   private Key that you are using to create the SSH connection. This should be the full contents of
   the key file starting with `-----BEGIN RSA PRIVATE KEY-----` and ending
   with `-----END RSA PRIVATE KEY-----`.

### Generating an SSH Key Pair

The connector expects an RSA key in PEM format. To generate this key:

```text
ssh-keygen -t rsa -m PEM -f myuser_rsa
```

This produces the private key in pem format, and the public key remains in the standard format used
by the `authorized_keys` file on your bastion host. The public key should be added to your bastion
host to whichever user you want to use with Airbyte. The private key is provided via copy-and-paste
to the Airbyte connector configuration screen, so it may log in to the bastion.

## Change Data Capture (CDC)

We aim to support Oracle CDC soon. Please reach out to your sales engineer if you are interested in being a design partner for CDC support in Oracle.

## Data type mapping

Oracle data types are mapped to the following data types when synchronizing data.

| Oracle Type                      | Airbyte Type            | Notes                       |
| :------------------------------- | :---------------------- | :-------------------------- |
| `BFILE`                          | string                  | base-64 encoded binary data |
| `BINARY_FLOAT`                   | number                  |                             |
| `BINARY_DOUBLE`                  | number                  |                             |
| `BLOB`                           | string                  | base-64 encoded binary data |
| `BOOL`                           | boolean                 |                             |
| `BOOLEAN`                        | boolean                 |                             |
| `CHAR`                           | string                  |                             |
| `CHAR VARYING`                   | string                  |                             |
| `CHARACTER`                      | string                  |                             |
| `CHARACTER VARYING`              | string                  |                             |
| `CLOB`                           | string                  |                             |
| `DATE`                           | date                    |                             |
| `DEC`                            | number                  | integer when scale is 0     |
| `DECIMAL`                        | number                  | integer when scale is 0     |
| `FLOAT`                          | number                  |                             |
| `DOUBLE PRECISION`               | number                  |                             |
| `REAL`                           | number                  |                             |
| `INT`                            | number                  | integer                     |
| `INTEGER`                        | number                  | integer                     |
| `INTERVAL YEAR TO MONTH`         | string                  |                             |
| `INTERVAL DAY TO SECOND`         | string                  |                             |
| `INTERVALDS`                     | string                  |                             |
| `INTERVALYM`                     | string                  |                             |
| `JSON`                           | object                  |                             |
| `LONG`                           | string                  | base-64 encoded binary data |
| `LONG RAW`                       | string                  | base-64 encoded binary data |
| `NATIONAL CHAR`                  | string                  |                             |
| `NATIONAL CHAR VARYING`          | string                  |                             |
| `NATIONAL CHARACTER`             | string                  |                             |
| `NATIONAL CHARACTER VARYING`     | string                  |                             |
| `NCHAR`                          | string                  |                             |
| `NCHAR VARYING`                  | string                  |                             |
| `NCLOB`                          | string                  |                             |
| `NUMBER`                         | number                  | integer when scale is 0     |
| `NUMERIC`                        | number                  | integer when scale is 0     |
| `NVARCHAR2`                      | string                  |                             |
| `RAW`                            | string                  | base-64 encoded binary data |
| `ROWID`                          | string                  | base-64 encoded binary data |
| `SMALLINT`                       | number                  | integer                     |
| `TIMESTAMP`                      | timestamp               |                             |
| `TIMESTAMP WITH LOCAL TIME ZONE` | timestamp               |                             |
| `TIMESTAMP WITH LOCAL TZ`        | timestamp               |                             |
| `TIMESTAMP WITH TIME ZONE`       | timestamp with timezone |                             |
| `TIMESTAMP WITH TZ`              | timestamp with timezone |                             |
| `UROWID`                         | string                  | base-64 encoded binary data |
| `VARCHAR`                        | string                  |                             |
| `VARCHAR2`                       | string                  |                             |

Varray types are mapped to the corresponding Airbyte array type.
This applies also to multiple levels of nesting, i.e. varrays of varrays, and so forth.

If you do not see a type in this list, assume that it is coerced into a string. We are happy to take
feedback on preferred mappings.

## Changelog

<details>
  <summary>Expand to review</summary>

The connector is still incubating, this section only exists to satisfy Airbyte's QA checks.

- 0.0.1
- 0.0.2
- 0.0.3
- 0.0.4
- 0.0.5
- 0.0.6
- 0.0.7

</details>
