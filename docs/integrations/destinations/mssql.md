# MSSQL

## Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | Yes |  |
| Incremental - Deduped History | No | As this connector does not support dbt, we don't support this sync mode on this destination. |
| Namespaces | Yes |  |

## Output Schema

Each stream will be output into its own table in SQL Server. Each table will contain 3 columns:

* `_airbyte_ab_id`: a uuid assigned by Airbyte to each event that is processed. The column type in SQL Server is `VARCHAR(64)`.
* `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source. The column type in SQL Server is `DATETIMEOFFSET(7)`.
* `_airbyte_data`: a JSON blob representing with the event data. The column type in SQL Server is `NVARCHAR(MAX)`.

#### Microsoft SQL Server specifics or why NVARCHAR type is used here:

* NVARCHAR is Unicode - 2 bytes per character, therefore max. of 1 billion characters; will handle East Asian, Arabic, Hebrew, Cyrillic etc. characters just fine.
* VARCHAR is non-Unicode - 1 byte per character, max. capacity is 2 billion characters, but limited to the character set you're SQL Server is using, basically - no support for those languages mentioned before

## Getting Started \(Airbyte Cloud\)

Airbyte Cloud only supports connecting to your MSSQL instance with TLS encryption. Other than that, you can proceed with the open-source instructions below.

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | Yes |  |
| Incremental - Deduped History | Yes |  |
| Namespaces | Yes |  |

## Getting Started \(Airbyte Open-Source\)

### Requirements

To use the SQL Server destination, you'll need:

MS SQL Server: `Azure SQL Database`, `Azure Synapse Analytics`, `Azure SQL Managed Instance`, `SQL Server 2019`, `SQL Server 2017`, `SQL Server 2016`, `SQL Server 2014`, `SQL Server 2012`, or `PDW 2008R2 AU34`.

### Normalization Requirements

To sync **with** normalization you'll need to use MS SQL Server of the following versions: `SQL Server 2019`, `SQL Server 2017`, `SQL Server 2016`, `SQL Server 2014`. The work of normalization on `SQL Server 2012` and bellow are not guaranteed.

### Setup guide

* MS SQL Server: `Azure SQL Database`, `Azure Synapse Analytics`, `Azure SQL Managed Instance`, `SQL Server 2019`, `SQL Server 2017`, `SQL Server 2016`, `SQL Server 2014`, `SQL Server 2012`, or `PDW 2008R2 AU34`.

#### Network Access

Make sure your SQL Server database can be accessed by Airbyte. If your database is within a VPC, you may need to allow access from the IP you're using to expose Airbyte.

#### **Permissions**

You need a user configured in SQL Server that can create tables and write rows. We highly recommend creating an Airbyte-specific user for this purpose.
In order to allow for normalization, please grant ALTER permissions for the user configured. 

#### Target Database

You will need to choose an existing database or create a new database that will be used to store synced data from Airbyte.

#### SSL configuration \(optional\)

Airbyte supports a SSL-encrypted connection to the database. If you want to use SSL to securely access your database, ensure that [the server is configured to use an SSL certificate.](https://support.microsoft.com/en-us/topic/how-to-enable-ssl-encryption-for-an-instance-of-sql-server-by-using-microsoft-management-console-1c7ae22f-8518-2b3e-93eb-d735af9e344c)

### Setup the MSSQL destination in Airbyte

You should now have all the requirements needed to configure SQL Server as a destination in the UI. You'll need the following information to configure the MSSQL destination:

* **Host**
* **Port**
* **Username**
* **Password**
* **Schema**
* **Database**
  * This database needs to exist within the schema provided.
* **SSL Method**:
  * The SSL configuration supports three modes: Unencrypted, Encrypted \(trust server certificate\), and Encrypted \(verify certificate\).
    * **Unencrypted**: Do not use SSL encryption on the database connection
    * **Encrypted \(trust server certificate\)**: Use SSL encryption without verifying the server's certificate.  This is useful for self-signed certificates in testing scenarios, but should not be used in production.
    * **Encrypted \(verify certificate\)**: Use the server's SSL certificate, after standard certificate verification.
  * **Host Name In Certificate** \(optional\): When using certificate verification, this property can be set to specify an expected name for added security.  If this value is present, and the server's certificate's host name does not match it, certificate verification will fail.

## Connection via SSH Tunnel

Airbyte has the ability to connect to the MS SQL Server instance via an SSH Tunnel. The reason you might want to do this because it is not possible \(or against security policy\) to connect to the database directly \(e.g. it does not have a public IP address\).

When using an SSH tunnel, you are configuring Airbyte to connect to an intermediate server \(a.k.a. a bastion sever\) that have direct access to the database. Airbyte connects to the bastion and then asks the bastion to connect directly to the server.

Using this feature requires additional configuration, when creating the source. We will talk through what each piece of configuration means.

1. Configure all fields for the source as you normally would, except `SSH Tunnel Method`.
2. `SSH Tunnel Method` defaults to `No Tunnel` \(meaning a direct connection\). If you want to use an SSH Tunnel choose `SSH Key Authentication` or `Password Authentication`.
3. Choose `Key Authentication` if you will be using an RSA private key as your secret for establishing the SSH Tunnel \(see below for more information on generating this key\).
4. Choose `Password Authentication` if you will be using a password as your secret for establishing the SSH Tunnel.
5. `SSH Tunnel Jump Server Host` refers to the intermediate \(bastion\) server that Airbyte will connect to. This should be a hostname or an IP Address.
6. `SSH Connection Port` is the port on the bastion server with which to make the SSH connection. The default port for SSH connections is `22`,

   so unless you have explicitly changed something, go with the default.

7. `SSH Login Username` is the username that Airbyte should use when connection to the bastion server. This is NOT the MS SQL Server username.
8. If you are using `Password Authentication`, then `SSH Login Username` should be set to the password of the User from the previous step.

   If you are using `SSH Key Authentication` leave this blank. Again, this is not the MS SQL Server password, but the password for the OS-user that

   Airbyte is using to perform commands on the bastion.

9. If you are using `SSH Key Authentication`, then `SSH Private Key` should be set to the RSA Private Key that you are using to create the SSH connection.

   This should be the full contents of the key file starting with `-----BEGIN RSA PRIVATE KEY-----` and ending with `-----END RSA PRIVATE KEY-----`.

## Changelog

| Version | Date | Pull Request                                             | Subject                                                                                             |
|:--------| :--- |:---------------------------------------------------------|:----------------------------------------------------------------------------------------------------|
| 0.1.22  | 2022-10-21 | [18275](https://github.com/airbytehq/airbyte/pull/18275)   | Upgrade commons-text for CVE 2022-42889                                                              |
| 0.1.20  | 2022-07-14 | [\#14618](https://github.com/airbytehq/airbyte/pull/14618) | Removed additionalProperties: false from JDBC destination connectors                                 |
| 0.1.19  | 2022-05-25 | [13054](https://github.com/airbytehq/airbyte/pull/13054)   | Destination MSSQL: added custom JDBC parameters support.                                             |
| 0.1.18  | 2022-05-17 | [12820](https://github.com/airbytehq/airbyte/pull/12820)   | Improved 'check' operation performance                                                               |
| 0.1.17  | 2022-04-05 | [11729](https://github.com/airbytehq/airbyte/pull/11729)   | Bump mina-sshd from 2.7.0 to 2.8.0                                                                   |
| 0.1.15  | 2022-02-25 | [10421](https://github.com/airbytehq/airbyte/pull/10421)   | Refactor JDBC parameters handling                                                                    |
| 0.1.14  | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256)   | Add `-XX:+ExitOnOutOfMemoryError` JVM option                                                         |
| 0.1.13  | 2021-12-28 | [\#9158](https://github.com/airbytehq/airbyte/pull/9158)   | Update connector fields title/description                                                            |
| 0.1.12  | 2021-12-01 | [\#8371](https://github.com/airbytehq/airbyte/pull/8371)   | Fixed incorrect handling "\n" in ssh key                                                             |
| 0.1.11  | 2021-11-08 | [#7719](https://github.com/airbytehq/airbyte/pull/7719)    | Improve handling of wide rows by buffering records based on their byte size rather than their count  |
| 0.1.10  | 2021-10-11 | [\#6877](https://github.com/airbytehq/airbyte/pull/6877)   | Add `normalization` capability, add `append+deduplication` sync mode                                 |
| 0.1.9   | 2021-09-29 | [\#5970](https://github.com/airbytehq/airbyte/pull/5970)   | Add support & test cases for MSSQL Destination via SSH tunnels                                       |
| 0.1.8   | 2021-08-07 | [\#5272](https://github.com/airbytehq/airbyte/pull/5272)   | Add batch method to insert records                                                                   |
| 0.1.7   | 2021-07-30 | [\#5125](https://github.com/airbytehq/airbyte/pull/5125)   | Enable `additionalPropertities` in spec.json                                                         |
| 0.1.6   | 2021-06-21 | [\#3555](https://github.com/airbytehq/airbyte/pull/3555)   | Partial Success in BufferedStreamConsumer                                                            |
| 0.1.5   | 2021-07-20 | [\#4874](https://github.com/airbytehq/airbyte/pull/4874)   | declare object types correctly in spec                                                               |
| 0.1.4   | 2021-06-17 | [\#3744](https://github.com/airbytehq/airbyte/pull/3744)   | Fix doc/params in specification file                                                                 |
| 0.1.3   | 2021-05-28 | [\#3728](https://github.com/airbytehq/airbyte/pull/3973)   | Change dockerfile entrypoint                                                                         |
| 0.1.2   | 2021-05-13 | [\#3367](https://github.com/airbytehq/airbyte/pull/3671)   | Fix handle symbols unicode                                                                           |
| 0.1.1   | 2021-05-11 | [\#3566](https://github.com/airbytehq/airbyte/pull/3195)   | MS SQL Server Destination Release!                                                                   |

### Changelog (Strict Encrypt)

| Version | Date | Pull Request | Subject                                                                                             |
|:--------| :--- | :--- |:----------------------------------------------------------------------------------------------------|
| 0.1.22  | 2022-10-21 | [18275](https://github.com/airbytehq/airbyte/pull/18275)   | Upgrade commons-text for CVE 2022-42889                                                              |
| 0.1.21  | 2022-09-14 | [15668](https://github.com/airbytehq/airbyte/pull/15668)   | Wrap logs in AirbyteLogMessage                                                                       |
| 0.1.20  | 2022-07-14 | [\#15260](https://github.com/airbytehq/airbyte/pull/15260) | Align version of strict encrypt connector with regular connector                                     |
| 0.1.10  | 2022-07-14 | [\#14618](https://github.com/airbytehq/airbyte/pull/14618) | Removed additionalProperties: false from JDBC destination connectors                                 |
| 0.1.9   | 2022-06-17 | [13864](https://github.com/airbytehq/airbyte/pull/13864)   | Updated stacktrace format for any trace message errors                                               |
| 0.1.8   | 2022-05-25 | [13054](https://github.com/airbytehq/airbyte/pull/13054)   | Destination MSSQL: added custom JDBC parameters support.                                             |
| 0.1.6   | 2022-05-17 | [12820](https://github.com/airbytehq/airbyte/pull/12820)   | Improved 'check' operation performance                                                               |
| 0.1.5   | 2022-02-25 | [10421](https://github.com/airbytehq/airbyte/pull/10421)   | Refactor JDBC parameters handling                                                                    |
| 0.1.4   | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256)   | Add `-XX:+ExitOnOutOfMemoryError` JVM option                                                         |
| 0.1.3   | 2021-12-28 | [\#9158](https://github.com/airbytehq/airbyte/pull/9158)   | Update connector fields title/description                                                            |
| 0.1.2   | 2021-12-01 | [8371](https://github.com/airbytehq/airbyte/pull/8371)     | Fixed incorrect handling "\n" in ssh key                                                             |
| 0.1.1   | 2021-11-08 | [#7719](https://github.com/airbytehq/airbyte/pull/7719)    | Improve handling of wide rows by buffering records based on their byte size rather than their count  |
