# SingleStore

## Overview

[SingleStore](https://www.singlestore.com/) is a distributed SQL database that offers
high-throughput transactions (inserts and upserts), low-latency analytics and context from real-time
vector data.

## Features

| Feature                   | Supported | Notes |
|:--------------------------|:----------|:------|
| Full Refresh Sync         | Yes       |       |
| Incremental - Append Sync | Yes       |       |
| Change Data Capture       | No        |       |
| SSL Support               | Yes       |       |
| SSH Tunnel Connection     | Yes       |       |

The contents below include a 'Quick Start' guide, advanced setup steps, and reference information (
data type mapping and changelogs).

## Getting Started

#### Requirements

1. SingleStore instance
2. Allow connections from Airbyte to your SingleStore database \(if they exist in separate VPCs\)
3. Create a dedicated read-only Airbyte user with access to all tables needed for replication

#### 1. Make sure your database is accessible from the machine running Airbyte

This is dependent on your networking setup. The easiest way to verify if Airbyte is able to connect
to your SingleStore instance is via the check connection tool in the UI.

#### 2. Create a dedicated read-only user with access to the relevant tables \(Recommended but optional\)

This step is optional but highly recommended to allow for better permission control and auditing.
Alternatively, you can use Airbyte with an existing user in your database.

To create a dedicated database user, run the following commands against your database:

```sql
CREATE
USER airbyte IDENTIFIED BY <your_password_here>;
```

Next, grant the user read-only access to the relevant tables. The simplest way is to grant read
access to all tables in the database as follows:

```sql
GRANT
SELECT
ON <your_database_name_here>.* TO airbyte;
```

Or you can be more granular:

```sql
GRANT SELECT ON "<database_a>"."<table_1>" TO airbyte;
GRANT SELECT ON "<database_b>"."<table_2>" TO airbyte;
```

Your database user should now be ready for use with Airbyte.

## Connecting with SSL or SSH Tunneling

<FieldAnchor field="ssl">

### SSL Modes

Here is a breakdown of available SSL connection modes:

- `disable` to disable encrypted communication between Airbyte and the source
- `required` to always require encryption. Note: The connection will fail if the source doesn't
  support encryption.
- `verify-ca` to always require encryption and verify that the source has a valid SSL certificate
- `verify-full` to always require encryption and verify the identity of the source

</FieldAnchor>

### Connection via SSH Tunnel

Airbyte has the ability to connect to a SingleStore instance via an SSH Tunnel. The reason you might
want
to do this because it is not possible \(or against security policy\) to connect to the database
directly \(e.g. it does not have a public IP address\).

When using an SSH tunnel, you are configuring Airbyte to connect to an intermediate server \(a.k.a.
a bastion sever\) that _does_ have direct access to the database. Airbyte connects to the bastion
and then asks the bastion to connect directly to the server.

Using this feature requires additional configuration, when creating the source. We will talk through
what each piece of configuration means.

1. Configure all fields for the source as you normally would, except `SSH Tunnel Method`.
2. `SSH Tunnel Method` defaults to `No Tunnel` \(meaning a direct connection\). If you want to use
   an SSH Tunnel choose `SSH Key Authentication` or `Password Authentication`.
    1. Choose `Key Authentication` if you will be using an RSA private key as your secret for
       establishing the SSH Tunnel \(see below for more information on generating this key\).
    2. Choose `Password Authentication` if you will be using a password as your secret for
       establishing the SSH Tunnel.
3. `SSH Tunnel Jump Server Host` refers to the intermediate \(bastion\) server that Airbyte will
   connect to. This should be a hostname or an IP Address.
4. `SSH Connection Port` is the port on the bastion server with which to make the SSH connection.
   The default port for SSH connections is `22`, so unless you have explicitly changed something, go
   with the default.
5. `SSH Login Username` is the username that Airbyte should use when connection to the bastion
   server. This is NOT the SingleStore username.
6. If you are using `Password Authentication`, then `SSH Login Username` should be set to the
   password of the User from the previous step. If you are using `SSH Key Authentication` leave this
   blank. Again, this is not the SingleStore password, but the password for the OS-user that Airbyte
   is
   using to perform commands on the bastion.
7. If you are using `SSH Key Authentication`, then `SSH Private Key` should be set to the RSA
   Private Key that you are using to create the SSH connection. This should be the full contents of
   the key file starting with `-----BEGIN RSA PRIVATE KEY-----` and ending
   with `-----END RSA PRIVATE KEY-----`.

#### Generating a private key for SSH Tunneling

The connector expects an RSA key in PEM format. To generate this key:

```text
ssh-keygen -t rsa -m PEM -f myuser_rsa
```

This produces the private key in pem format, and the public key remains in the standard format used
by the `authorized_keys` file on your bastion host. The public key should be added to your bastion
host to whichever user you want to use with Airbyte. The private key is provided via copy-and-paste
to the Airbyte connector configuration screen, so it may log in to the bastion.

## Data Type Mapping

SingleStore data types are mapped to the following data types when synchronizing data.

| SingleStore<br/> Type | Resulting Type         | Notes |
|:----------------------|:-----------------------|:------|
| `BIT`                 | base64 binary string   |       |
| `TINYINT`             | number                 |       |
| `SMALLINT`            | number                 |       |
| `MEDIUMINT`           | number                 |       |
| `INT`                 | number                 |       |
| `BIGINT`              | number                 |       |
| `FLOAT`               | number                 |       |
| `DOUBLE`              | number                 |       |
| `DECIMAL`             | number                 |       |
| `DATE`                | string                 |       |
| `TIME`                | string                 |       |
| `DATETIME`            | string                 |       |
| `TIMESTAMP`           | string                 |       |
| `YEAR`                | year string            |       |
| `CHAR`                | string                 |       |
| `VARCHAR`             | string                 |       |
| `LONGTEXT`            | string                 |       |
| `MEDIUMTEXT`          | string                 |       |
| `TEXT`                | string                 |       |
| `TINYTEXT`            | string                 |       |
| `BINARY`              | base64 binary string   |       |
| `VARBINARY`           | base64 binary string   |       |
| `LONGBLOB`            | base64 binary string   |       |
| `MEDIUMBLOB`          | base64 binary string   |       |
| `BLOB`                | base64 binary string   |       |
| `TINYBLOB`            | base64 binary string   |       |
| `JSON`                | serialized json string |       |
| `ENUM`                | string                 |       |
| `SET`                 | string                 |       |
| `GEOGRAPHYPOINT`      | string                 |       |
| `GEOGRAPHY`           | string                 |       |
| `VECTOR`              | string                 |       |

## Changelog

| Version | Date       | Pull Request                                           | Subject                          |
|:--------|:-----------|:-------------------------------------------------------|:---------------------------------|
| 0.1.0   | 2024-04-16 | [37337](https://github.com/airbytehq/airbyte/pull/37337) | Add SingleStore source connector |
 