# Oracle DB

## Features

| Feature | Supported | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | Yes |  |
| Replicate Incremental Deletes | Coming soon |  |
| Logical Replication \(WAL\) | Coming soon |  |
| SSL Support | Coming soon |  |
| SSH Tunnel Connection | Yes |  |
| LogMiner | Coming soon |  |
| Flashback | Coming soon |  |
| Namespaces | Yes | Enabled by default |

The Oracle source does not alter the schema present in your database. Depending on the destination connected to this source, however, the schema may be altered. See the destination's documentation for more details.

## Getting Started (Airbyte Cloud)
On Airbyte Cloud, only TLS connections to your Oracle instance are supported. Other than that, you can proceed with the open-source instructions below.

## Getting Started (Airbyte Open-Source)

#### Requirements

1. Oracle `11g` or above
2. Allow connections from Airbyte to your Oracle database \(if they exist in separate VPCs\)
3. Create a dedicated read-only Airbyte user with access to all tables needed for replication

#### 1. Make sure your database is accessible from the machine running Airbyte

This is dependent on your networking setup. The easiest way to verify if Airbyte is able to connect to your Oracle instance is via the check connection tool in the UI.

#### 2. Create a dedicated read-only user with access to the relevant tables \(Recommended but optional\)

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

Case sensitive. Defaults to the upper-cased user if empty. If the user does not have access to the configured schemas, no tables will be discovered.

## Connection via SSH Tunnel

Airbyte has the ability to connect to a Oracle instance via an SSH Tunnel. The reason you might want to do this because it is not possible (or against security policy) to connect to the database directly (e.g. it does not have a public IP address).

When using an SSH tunnel, you are configuring Airbyte to connect to an intermediate server (a.k.a. a bastion sever) that _does_ have direct access to the database. Airbyte connects to the bastion and then asks the bastion to connect directly to the server.

Using this feature requires additional configuration, when creating the source. We will talk through what each piece of configuration means.

1. Configure all fields for the source as you normally would, except `SSH Tunnel Method`.
2. `SSH Tunnel Method` defaults to `No Tunnel` (meaning a direct connection). If you want to use an SSH Tunnel choose `SSH Key Authentication` or `Password Authentication`.
   1. Choose `Key Authentication` if you will be using an RSA private key as your secret for establishing the SSH Tunnel (see below for more information on generating this key).
   2. Choose `Password Authentication` if you will be using a password as your secret for establishing the SSH Tunnel.
3. `SSH Tunnel Jump Server Host` refers to the intermediate (bastion) server that Airbyte will connect to. This should be a hostname or an IP Address.
4. `SSH Connection Port` is the port on the bastion server with which to make the SSH connection. The default port for SSH connections is `22`, so unless you have explicitly changed something, go with the default.
5. `SSH Login Username` is the username that Airbyte should use when connection to the bastion server. This is NOT the Oracle username.
6. If you are using `Password Authentication`, then `SSH Login Username` should be set to the password of the User from the previous step. If you are using `SSH Key Authentication` leave this blank. Again, this is not the Oracle password, but the password for the OS-user that Airbyte is using to perform commands on the bastion.
7. If you are using `SSH Key Authentication`, then `SSH Private Key` should be set to the RSA Private Key that you are using to create the SSH connection. This should be the full contents of the key file starting with `-----BEGIN RSA PRIVATE KEY-----` and ending with `-----END RSA PRIVATE KEY-----`.

### Generating an SSH Key Pair

The connector expects an RSA key in PEM format.  To generate this key:

    ssh-keygen -t rsa -m PEM -f myuser_rsa

This produces the private key in pem format, and the public key remains in the standard format used by the `authorized_keys` file on 
your bastion host.  The public key should be added to your bastion host to whichever user you want to use with Airbyte.  The private
key is provided via copy-and-paste to the Airbyte connector configuration screen, so it may log in to the bastion.

## Data Type Mapping

Oracle data types are mapped to the following data types when synchronizing data.
You can check the test values examples [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-oracle/src/test-integration/java/io/airbyte/integrations/source/oracle/OracleSourceComprehensiveTest.java).
If you can't find the data type you are looking for or have any problems feel free to add a new test!

| Oracle Type | Resulting Type | Notes |
| :--- | :--- | :--- |
| `binary_double` | number |  |
| `binary_float` | number |  |
| `blob` | string |  |
| `char` | string |  |
| `char(3 char)` | string |  |
| `clob` | string |  |
| `date` | string |  |
| `decimal` | number |  |
| `float` | number |  |
| `float(5)` | number |  |
| `integer` | number |  |
| `interval year to month` | string |  |
| `long raw` | string |  |
| `number` | number |  |
| `number(6, 2)` | number |  |
| `nvarchar(3)` | string |  |
| `raw` | string |  |
| `timestamp` | string |  |
| `timestamp with local time zone` | string |  |
| `timestamp with time zone` | string |  |
| `varchar2` | string |  |
| `varchar2(256)` | string |  |
| `xmltype` | string |  |

If you do not see a type in this list, assume that it is coerced into a string. We are happy to take feedback on preferred mappings.

## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.3.6   | 2021-09-30 | [6585](https://github.com/airbytehq/airbyte/pull/6585) | Improved SSH Tunnel key generation steps |
| 0.3.5   | 2021-09-22 | [6356](https://github.com/airbytehq/airbyte/pull/6356) | Added option to connect to DB via SSH. |
| 0.3.4   | 2021-09-01 | [6038](https://github.com/airbytehq/airbyte/pull/6038) | Remove automatic filtering of system schemas. |
| 0.3.3   | 2021-09-01 | [5779](https://github.com/airbytehq/airbyte/pull/5779) | Ability to only discover certain schemas. |
| 0.3.2   | 2021-08-13 | [4699](https://github.com/airbytehq/airbyte/pull/4699) | Added json config validator. |
