# MySQL

This page contains the setup guide and reference information for MySQL.

There are two types of connection for this destination:

1. destination-mysql. Supports both SSL and non SSL connections.
2. destination-mysql-strict-encrypt. Pretty same as connector above, but supports SSL connections only.

## Prerequisites

* To sync data to MySQL **with normalization** you'll need MySQL 8.0.0 or above
* To sync data to MySQL **without normalization** you'll need MySQL 5.0 or above.
* Host
* Port
* Database
* Username
* Password

### Permission

You will need a MySQL user with `CREATE, INSERT, SELECT, DROP` permissions. We highly recommend creating a Daspire-specific user for this purpose.

### Network Access

Make sure your MySQL database can be accessed by Daspire. If your database is within a VPC, you may need to allow access from the IP you're using to expose Daspire.

### Target Database

MySQL doesn't differentiate between a database and schema. A database is essentially a schema where all the tables live in. You will need to choose an existing database or create a new database. This will act as a default database/schema where the tables will be created if the source doesn't provide a namespace.

## Features

| Feature | Supported? |
| --- | --- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |
| Incremental - Deduped History | No |
| Namespaces | Yes |
| SSH Tunnel Connection | Yes |

### Output Schema

Each stream will be output into its own table in MySQL. Each table will contain 3 columns:

* `_daspire_ab_id`: a uuid assigned by Daspire to each event that is processed. The column type in MySQL is `VARCHAR(256)`.

* `_daspire_emitted_at`: a timestamp representing when the event was pulled from the data source. The column type in MySQL is `TIMESTAMP(6)`.

* `_daspire_data`: a json blob representing with the event data. The column type in MySQL is `JSON`.

## Setup guide

Before setting up MySQL destination in Daspire, you need to set the [local_infile](https://dev.mysql.com/doc/refman/8.0/en/server-system-variables.html#sysvar_local_infile) system variable to true. You can do this by running the query `SET GLOBAL local_infile = true` with a user with [SYSTEM\_VARIABLES\_ADMIN](https://dev.mysql.com/doc/refman/8.0/en/privileges-provided.html#priv_system-variables-admin) permission. This is required cause Daspire uses `LOAD DATA LOCAL INFILE` to load data into table.

You should now have all the requirements needed to configure MySQL as a destination in the UI. You'll need the following information to configure the MySQL destination:

* **Host**
* **Port**
* **Username**
* **Password**
* **Database**
* **jdbc\_url\_params** (Optional)

### Default JDBC URL Parameters

The following JDBC URL parameters are set by Daspire and cannot be overridden by the `jdbc_url_params` field:

* `useSSL=true` (unless `ssl` is set to false)
* `requireSSL=true` (unless `ssl` is set to false)
* `verifyServerCertificate=false` (unless `ssl` is set to false)
* `zeroDateTimeBehavior=convertToNull`

## Limitations

Note that MySQL documentation discusses identifiers case sensitivity using the `lower_case_table_names` system variable. One of their recommendations is:

```
"It is best to adopt a consistent convention, such as always creating and referring to databases and tables using lowercase names.
This convention is recommended for maximum portability and ease of use."
``` 
[Source: MySQL docs](https://dev.mysql.com/doc/refman/8.0/en/identifier-case-sensitivity.html)

As a result, Daspire MySQL destination forces all identifier (table, schema and columns) names to be lowercase.

## Connection via SSH Tunnel

Daspire has the ability to connect to a MySQL instance via an SSH Tunnel. The reason you might want to do this because it is not possible (or against security policy) to connect to the database directly (e.g. it does not have a public IP address).

When using an SSH tunnel, you are configuring Daspire to connect to an intermediate server (a.k.a. a bastion server) that does have direct access to the database. Daspire connects to the bastion and then asks the bastion to connect directly to the server.

Using this feature requires additional configuration, when creating the destination. We will talk through what each piece of configuration means.

1. Configure all fields for the destination as you normally would, except `SSH Tunnel Method`.

2. `SSH Tunnel Method` defaults to `No Tunnel` (meaning a direct connection). If you want to use an SSH Tunnel choose `SSH Key Authentication` or `Password Authentication`.

  * Choose `Key Authentication` if you will be using an RSA private key as your secret for establishing the SSH Tunnel (see below for more information on generating this key).

  * Choose `Password Authentication` if you will be using a password as your secret for establishing the SSH Tunnel.

3. `SSH Tunnel Jump Server Host` refers to the intermediate (bastion) server that Daspire will connect to. This should be a hostname or an IP Address.

4. `SSH Connection Port` is the port on the bastion server with which to make the SSH connection. The default port for SSH connections is `22`, so unless you have explicitly changed something, go with the default.

5. `SSH Login Username` is the username that Daspire should use when connection to the bastion server. This is NOT the MySQL username.

6. If you are using `Password Authentication`, then `SSH Login Username` should be set to the password of the User from the previous step. If you are using `SSH Key Authentication` leave this blank. Again, this is not the MySQL password, but the password for the OS-user that Daspire is using to perform commands on the bastion.

7. If you are using `SSH Key Authentication`, then `SSH Private Key` should be set to the RSA Private Key that you are using to create the SSH connection. This should be the full contents of the key file starting with `-----BEGIN RSA PRIVATE KEY-----` and ending with `-----END RSA PRIVATE KEY-----`.