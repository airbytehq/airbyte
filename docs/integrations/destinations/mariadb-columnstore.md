# Mariadb Columnstore

## Sync overview

### Output schema

Each stream will be output into its own table in MariaDB ColumnStore. Each table will contain 3 columns:

* `_airbyte_ab_id`: a uuid assigned by Airbyte to each event that is processed. The column type in MariaDB ColumnStore is VARCHAR(256).
* `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source. The column type in MariaDB ColumnStore is TIMESTAMP.
* `_airbyte_data`: a json blob representing with the event data. The column type in MariaDB ColumnStore is LONGTEXT.

### Features

| Feature | Supported?(Yes/No) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | Yes |  |
| Replicate Incremental Deletes | Yes |  |
| SSL connection | No |  |
| SSH Tunnel Support | Yes |  |

### Performance considerations

Could this connector hurt the user's database/API/etc... or put too much strain on it in certain circumstances? For example, if there are a lot of tables or rows in a table? What is the breaking point (e.g: 100mm&gt; records)? What can the user do to prevent this? (e.g: use a read-only replica, or schedule frequent syncs, etc..)

## Getting started

### Requirements

To use the MariaDB ColumnStore destination, you'll need to sync data to MariaDB ColumnStore 5.5.3 or above.

#### Network Access

Make sure your MariaDB ColumnStore database can be accessed by Airbyte. If your database is within a VPC, you may need to allow access from the IP you're using to expose Airbyte.

#### **Permissions**

You need a MariaDB user with `CREATE, INSERT, SELECT, DROP` permissions. We highly recommend creating an Airbyte-specific user for this purpose.

#### Target Database

MariaDB ColumnStore doesn't differentiate between a database and schema. A database is essentially a schema where all the tables live in. You will need to choose an existing database or create a new database. This will act as a default database/schema where the tables will be created if the source doesn't provide a namespace.

### Setup the MariaDB ColumnStore destination in Airbyte

Before setting up MariaDB ColumnStore destination in Airbyte, you need to set the [local\_infile](https://mariadb.com/kb/en/server-system-variables/#local_infile) system variable to true. You can do this by running the query `SET GLOBAL local_infile = true` . This is required cause Airbyte uses `LOAD DATA LOCAL INFILE` to load data into table.

You should now have all the requirements needed to configure MariaDB ColumnStore as a destination in the UI. You'll need the following information to configure the MariaDB ColumnStore destination:

* **Host**
* **Port**
* **Username**
* **Password**
* **Database**

## Connection via SSH Tunnel

Airbyte has the ability to connect to a MariaDB instance via an SSH Tunnel. The reason you might want to do this because it is not possible \(or against security policy\) to connect to the database directly \(e.g. it does not have a public IP address\).

When using an SSH tunnel, you are configuring Airbyte to connect to an intermediate server \(a.k.a. a bastion sever\) that _does_ have direct access to the database. Airbyte connects to the bastion and then asks the bastion to connect directly to the server.

Using this feature requires additional configuration, when creating the destination. We will talk through what each piece of configuration means.

1. Configure all fields for the destination as you normally would, except `SSH Tunnel Method`.
2. `SSH Tunnel Method` defaults to `No Tunnel` \(meaning a direct connection\). If you want to use an SSH Tunnel choose `SSH Key Authentication` or `Password Authentication`.
   1. Choose `Key Authentication` if you will be using an RSA private key as your secret for establishing the SSH Tunnel \(see below for more information on generating this key\).
   2. Choose `Password Authentication` if you will be using a password as your secret for establishing the SSH Tunnel.
3. `SSH Tunnel Jump Server Host` refers to the intermediate \(bastion\) server that Airbyte will connect to. This should be a hostname or an IP Address.
4. `SSH Connection Port` is the port on the bastion server with which to make the SSH connection. The default port for SSH connections is `22`, so unless you have explicitly changed something, go with the default.
5. `SSH Login Username` is the username that Airbyte should use when connection to the bastion server. This is NOT the MySQl username.
6. If you are using `Password Authentication`, then `SSH Login Username` should be set to the password of the User from the previous step. If you are using `SSH Key Authentication` leave this blank. Again, this is not the MariaDB password, but the password for the OS-user that Airbyte is using to perform commands on the bastion.
7. If you are using `SSH Key Authentication`, then `SSH Private Key` should be set to the RSA Private Key that you are using to create the SSH connection. This should be the full contents of the key file starting with `-----BEGIN RSA PRIVATE KEY-----` and ending with `-----END RSA PRIVATE KEY-----`.

## CHANGELOG

| Version | Date       | Pull Request                                             | Subject                                      |
|:--------|:-----------|:---------------------------------------------------------|:---------------------------------------------|
| 0.1.7 | 2022-09-07 | [16391](https://github.com/airbytehq/airbyte/pull/16391) | Add custom JDBC parameters field |
| 0.1.6 | 2022-06-17 | [13864](https://github.com/airbytehq/airbyte/pull/13864) | Updated stacktrace format for any trace message errors |
| 0.1.5   | 2022-05-17 | [12820](https://github.com/airbytehq/airbyte/pull/12820) | Improved 'check' operation performance |
| 0.1.4   | 2022-02-25 | [10421](https://github.com/airbytehq/airbyte/pull/10421) | Refactor JDBC parameters handling            |
| 0.1.3   | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256) | Add `-XX:+ExitOnOutOfMemoryError` JVM option |
| 0.1.2   | 2021-12-30 | [\#8809](https://github.com/airbytehq/airbyte/pull/8809) | Update connector fields title/description    |
| 0.1.1   | 2021-12-01 | [\#8371](https://github.com/airbytehq/airbyte/pull/8371) | Fixed incorrect handling "\n" in ssh key.    |
| 0.1.0   | 2021-11-15 | [\#7961](https://github.com/airbytehq/airbyte/pull/7961) | Added MariaDB ColumnStore destination.       |

