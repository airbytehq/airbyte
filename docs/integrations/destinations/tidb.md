# MySQL

There are two flavors of connectors for this destination:
1. destination-mysql connector. Supports both SSL and non SSL connections.
2. destination-mysql-strict-encrypt connector. Pretty same as connector above, but supports SSL connections only.


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

## Getting Started \(Airbyte Cloud\)

Airbyte Cloud only supports connecting to your MySQL instance with TLS encryption. Other than that, you can proceed with the open-source instructions below.

## Getting Started \(Airbyte Open-Source\)

### Requirements

To use the MySQL destination, you'll need:

* To sync data to MySQL **with** normalization MySQL database 8.0.0 or above
* To sync data to MySQL **without** normalization you'll need MySQL 5.0 or above.

#### Troubleshooting

Some users reported that they could not connect to Amazon RDS MySQL or MariaDB. This can be diagnosed with the error message: `Cannot create a PoolableConnectionFactory`.
To solve this issue add `enabledTLSProtocols=TLSv1.2` in the JDBC parameters.

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
* **jdbc_url_params** (Optional)

### Default JDBC URL Parameters

The following JDBC URL parameters are set by Airbyte and cannot be overridden by the `jdbc_url_params` field:

* `useSSL=true` (unless `ssl` is set to false)
* `requireSSL=true` (unless `ssl` is set to false)
* `verifyServerCertificate=false` (unless `ssl` is set to false)
* `zeroDateTimeBehavior=convertToNull`

## Known Limitations

Note that MySQL documentation discusses identifiers case sensitivity using the `lower_case_table_names` system variable. One of their recommendations is:

```text
"It is best to adopt a consistent convention, such as always creating and referring to databases and tables using lowercase names.
 This convention is recommended for maximum portability and ease of use."
```

[Source: MySQL docs](https://dev.mysql.com/doc/refman/8.0/en/identifier-case-sensitivity.html)

As a result, Airbyte MySQL destination forces all identifier \(table, schema and columns\) names to be lowercase.

## Connection via SSH Tunnel

Airbyte has the ability to connect to a MySQl instance via an SSH Tunnel. The reason you might want to do this because it is not possible \(or against security policy\) to connect to the database directly \(e.g. it does not have a public IP address\).

When using an SSH tunnel, you are configuring Airbyte to connect to an intermediate server \(a.k.a. a bastion sever\) that _does_ have direct access to the database. Airbyte connects to the bastion and then asks the bastion to connect directly to the server.

Using this feature requires additional configuration, when creating the destination. We will talk through what each piece of configuration means.

1. Configure all fields for the destination as you normally would, except `SSH Tunnel Method`.
2. `SSH Tunnel Method` defaults to `No Tunnel` \(meaning a direct connection\). If you want to use an SSH Tunnel choose `SSH Key Authentication` or `Password Authentication`.
    1. Choose `Key Authentication` if you will be using an RSA private key as your secret for establishing the SSH Tunnel \(see below for more information on generating this key\).
    2. Choose `Password Authentication` if you will be using a password as your secret for establishing the SSH Tunnel.
3. `SSH Tunnel Jump Server Host` refers to the intermediate \(bastion\) server that Airbyte will connect to. This should be a hostname or an IP Address.
4. `SSH Connection Port` is the port on the bastion server with which to make the SSH connection. The default port for SSH connections is `22`, so unless you have explicitly changed something, go with the default.
5. `SSH Login Username` is the username that Airbyte should use when connection to the bastion server. This is NOT the MySQl username.
6. If you are using `Password Authentication`, then `SSH Login Username` should be set to the password of the User from the previous step. If you are using `SSH Key Authentication` leave this blank. Again, this is not the MySQl password, but the password for the OS-user that Airbyte is using to perform commands on the bastion.
7. If you are using `SSH Key Authentication`, then `SSH Private Key` should be set to the RSA Private Key that you are using to create the SSH connection. This should be the full contents of the key file starting with `-----BEGIN RSA PRIVATE KEY-----` and ending with `-----END RSA PRIVATE KEY-----`.

## CHANGELOG

| Version | Date       | Pull Request                                       | Subject                 |
|:--------|:-----------|:---------------------------------------------------|:------------------------|
| 0.1.0   | 2022-08-10 | []()                                               | Added TiDB destination. |

## CHANGELOG destination-mysql-strict-encrypt

| Version | Date | Pull Request                                              | Subject |
|:--------|:-----|:----------------------------------------------------------|:--------|
