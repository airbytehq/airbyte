# MySQL

## Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | Yes |  |
| Incremental - Deduped History | Yes |  |
| Namespaces | Yes |  |
| SSH Tunnel Connection | Yes |  |

#### Output Schema

Each stream will be output into its own table in MySQL. Each table will contain 3 columns:

* `_airbyte_ab_id`: a uuid assigned by Airbyte to each event that is processed. The column type in MySQL is `VARCHAR(256)`.
* `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source. The column type in MySQL is `TIMESTAMP(6)`.
* `_airbyte_data`: a json blob representing with the event data. The column type in MySQL is `JSON`.

## Getting Started (Airbyte Cloud)
Airbyte Cloud only supports connecting to your MySQL instance with TLS encryption. Other than that, you can proceed with the open-source instructions below.

## Getting Started (Airbyte Open-Source)

### Requirements

To use the MySQL destination, you'll need:

* To sync data to MySQL **with** normalization MySQL database 8.0.0 or above
* To sync data to MySQL **without** normalization you'll need MySQL 5.0 or above.

#### Network Access

Make sure your MySQL database can be accessed by Airbyte. If your database is within a VPC, you may need to allow access from the IP you're using to expose Airbyte.

#### **Permissions**

You need a MySQL user with `CREATE, INSERT, SELECT, DROP` permissions. We highly recommend creating an Airbyte-specific user for this purpose.

#### Target Database

MySQL doesn't differentiate between a database and schema. A database is essentially a schema where all the tables live in. You will need to choose an existing database or create a new database. This will act as a default database/schema where the tables will be created if the source doesn't provide a namespace.

### Setup the MySQL destination in Airbyte

Before setting up MySQL destination in Airbyte, you need to set the [local\_infile](https://dev.mysql.com/doc/refman/8.0/en/server-system-variables.html#sysvar_local_infile) system variable to true. You can do this by running the query `SET GLOBAL local_infile = true` with a user with [SYSTEM\_VARIABLES\_ADMIN](https://dev.mysql.com/doc/refman/8.0/en/privileges-provided.html#priv_system-variables-admin) permission. This is required cause Airbyte uses `LOAD DATA LOCAL INFILE` to load data into table.

You should now have all the requirements needed to configure MySQL as a destination in the UI. You'll need the following information to configure the MySQL destination:

* **Host**
* **Port**
* **Username**
* **Password**
* **Database**

## Known Limitations

Note that MySQL documentation discusses identifiers case sensitivity using the `lower_case_table_names` system variable.
One of their recommendations is:

    "It is best to adopt a consistent convention, such as always creating and referring to databases and tables using lowercase names.
     This convention is recommended for maximum portability and ease of use."

[Source: MySQL docs](https://dev.mysql.com/doc/refman/8.0/en/identifier-case-sensitivity.html)

As a result, Airbyte MySQL destination forces all identifier (table, schema and columns) names to be lowercase.

## Connection via SSH Tunnel

Airbyte has the ability to connect to a MySQl instance via an SSH Tunnel. The reason you might want to do this because it is not possible (or against security policy) to connect to the database directly (e.g. it does not have a public IP address).

When using an SSH tunnel, you are configuring Airbyte to connect to an intermediate server (a.k.a. a bastion sever) that _does_ have direct access to the database. Airbyte connects to the bastion and then asks the bastion to connect directly to the server.

Using this feature requires additional configuration, when creating the destination. We will talk through what each piece of configuration means.
1. Configure all fields for the destination as you normally would, except `SSH Tunnel Method`.
2. `SSH Tunnel Method` defaults to `No Tunnel` (meaning a direct connection). If you want to use an SSH Tunnel choose `SSH Key Authentication` or `Password Authentication`.
    1. Choose `Key Authentication` if you will be using an RSA private key as your secret for establishing the SSH Tunnel (see below for more information on generating this key).
    2. Choose `Password Authentication` if you will be using a password as your secret for establishing the SSH Tunnel.
3. `SSH Tunnel Jump Server Host` refers to the intermediate (bastion) server that Airbyte will connect to. This should be a hostname or an IP Address.
4. `SSH Connection Port` is the port on the bastion server with which to make the SSH connection. The default port for SSH connections is `22`, so unless you have explicitly changed something, go with the default.
5. `SSH Login Username` is the username that Airbyte should use when connection to the bastion server. This is NOT the MySQl username.
6. If you are using `Password Authentication`, then `SSH Login Username` should be set to the password of the User from the previous step. If you are using `SSH Key Authentication` leave this blank. Again, this is not the MySQl password, but the password for the OS-user that Airbyte is using to perform commands on the bastion.
7. If you are using `SSH Key Authentication`, then `SSH Private Key` should be set to the RSA Private Key that you are using to create the SSH connection. This should be the full contents of the key file starting with `-----BEGIN RSA PRIVATE KEY-----` and ending with `-----END RSA PRIVATE KEY-----`.

## CHANGELOG

| Version | Date | Pull Request | Subject |
| :--- | :---  | :--- | :--- |
| 0.1.13 | 2021-09-28 | [#6506](https://github.com/airbytehq/airbyte/pull/6506) | Added support for MySQL destination via TLS/SSL |
| 0.1.12 | 2021-09-24 | [#6317](https://github.com/airbytehq/airbyte/pull/6317) | Added option to connect to DB via SSH |
| 0.1.11 | 2021-07-30 | [#5125](https://github.com/airbytehq/airbyte/pull/5125) | Enable `additionalPropertities` in spec.json |
| 0.1.10 | 2021-07-28 | [#5026](https://github.com/airbytehq/airbyte/pull/5026) | Add sanitized json fields in raw tables to handle quotes in column names |
| 0.1.7 | 2021-07-09 | [#4651](https://github.com/airbytehq/airbyte/pull/4651) | Switch normalization flag on so users can use normalization. |
| 0.1.6 | 2021-07-03 | [#4531](https://github.com/airbytehq/airbyte/pull/4531) | Added normalization for MySQL. |
| 0.1.5 | 2021-07-03 | [#3973](https://github.com/airbytehq/airbyte/pull/3973) | Added `AIRBYTE_ENTRYPOINT` for kubernetes support. |
| 0.1.4 | 2021-07-03 | [#3290](https://github.com/airbytehq/airbyte/pull/3290) | Switched to get states from destination instead of source. |
| 0.1.3 | 2021-07-03 | [#3387](https://github.com/airbytehq/airbyte/pull/3387) | Fixed a bug for message length checking. |
| 0.1.2 | 2021-07-03 | [#3327](https://github.com/airbytehq/airbyte/pull/3327) | Fixed LSEP unicode characters. |
| 0.1.1 | 2021-07-03 | [#3289](https://github.com/airbytehq/airbyte/pull/3289) | Added support for outputting messages. |
| 0.1.0 | 2021-05-06 | [#3242](https://github.com/airbytehq/airbyte/pull/3242) | Added MySQL destination. |
