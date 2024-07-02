# OceanBase

## Features

| Feature                        | Supported?\(Yes/No\) | Notes |
| :----------------------------- | :------------------- | :---- |
| Full Refresh Sync              | Yes                  |       |
| Incremental - Append Sync      | Yes                  |       |
| Incremental - Append + Deduped | Yes                  |       |
| Namespaces                     | Yes                  |       |


## Getting Started \(Airbyte Open Source\)

### Requirements

To use the OceanBase destination, you'll need:

OceanBase: `OcanBase EE`, `OcanBase CE`, `OceanBase Cloud`

### Setup guide

- OceanBase: `OcanBase EE`, `OcanBase CE`, `OceanBase Cloud`

#### Network Access

Make sure your OceanBase database can be accessed by Airbyte. If your database is within a VPC, you may need to allow access from the IP you're using to expose Airbyte.

#### **Permissions**

You need a user configured in OceanBase that can create tables and write rows. We highly recommend creating an Airbyte-specific user for this purpose.
In order to allow for normalization, please grant ALTER permissions for the user configured.

#### Target Database

You will need to choose an existing database or create a new database that will be used to store synced data from Airbyte.

#### SSL configuration \(optional\)

Airbyte supports a SSL-encrypted connection to the database. 

You should now have all the requirements needed to configure OceanBase as a destination in the UI. You'll need the following information to configure the OceanBase destination:

- **Host**
- **Port**
- **Username**
- **Password**
- **Schema**
- **Database**
  - This database needs to exist within the schema provided.
- **SSL Method**:
  - The SSL configuration supports three modes: Unencrypted, Encrypted \(trust server certificate\), and Encrypted \(verify certificate\).
    - **Unencrypted**: Do not use SSL encryption on the database connection
    - **Encrypted \(trust server certificate\)**: Use SSL encryption without verifying the server's certificate. This is useful for self-signed certificates in testing scenarios, but should not be used in production.
    - **Encrypted \(verify certificate\)**: Use the server's SSL certificate, after standard certificate verification.
  - **Host Name In Certificate** \(optional\): When using certificate verification, this property can be set to specify an expected name for added security. If this value is present, and the server's certificate's host name does not match it, certificate verification will fail.

## Connection via SSH Tunnel

Airbyte has the ability to connect to the OceanBase instance via an SSH Tunnel. The reason you might want to do this because it is not possible \(or against security policy\) to connect to the database directly \(e.g. it does not have a public IP address\).

When using an SSH tunnel, you are configuring Airbyte to connect to an intermediate server \(a.k.a. a bastion sever\) that have direct access to the database. Airbyte connects to the bastion and then asks the bastion to connect directly to the server.

Using this feature requires additional configuration, when creating the source. We will talk through what each piece of configuration means.

1. Configure all fields for the source as you normally would, except `SSH Tunnel Method`.
2. `SSH Tunnel Method` defaults to `No Tunnel` \(meaning a direct connection\). If you want to use an SSH Tunnel choose `SSH Key Authentication` or `Password Authentication`.
3. Choose `Key Authentication` if you will be using an RSA private key as your secret for establishing the SSH Tunnel \(see below for more information on generating this key\).
4. Choose `Password Authentication` if you will be using a password as your secret for establishing the SSH Tunnel.
5. `SSH Tunnel Jump Server Host` refers to the intermediate \(bastion\) server that Airbyte will connect to. This should be a hostname or an IP Address.
6. `SSH Connection Port` is the port on the bastion server with which to make the SSH connection. The default port for SSH connections is `22`,

   so unless you have explicitly changed something, go with the default.

7. `SSH Login Username` is the username that Airbyte should use when connection to the bastion server. This is NOT the OceanBase username.
8. If you are using `Password Authentication`, then `SSH Login Username` should be set to the password of the User from the previous step.

   If you are using `SSH Key Authentication` leave this blank. Again, this is not the OceanBase password, but the password for the OS-user that

   Airbyte is using to perform commands on the bastion.

9. If you are using `SSH Key Authentication`, then `SSH Private Key` should be set to the RSA Private Key that you are using to create the SSH connection.

   This should be the full contents of the key file starting with `-----BEGIN RSA PRIVATE KEY-----` and ending with `-----END RSA PRIVATE KEY-----`.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                               | Subject                                                                                        |
| :------ |:-----------|:-----------------------------------------------------------|:-----------------------------------------------------------------------------------------------|
| 1.0.0   | 2024-06-25 | [\#40256](https://github.com/airbytehq/airbyte/pull/40256) |New dest oceanbase                                                                                                |

</details>