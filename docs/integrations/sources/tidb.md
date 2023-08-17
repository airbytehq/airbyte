# TiDB

## Overview

[TiDB](https://github.com/pingcap/tidb) (/’taɪdiːbi:/, "Ti" stands for Titanium) is an open-source, distributed, NewSQL database that supports Hybrid Transactional and Analytical Processing (HTAP) workloads. It is MySQL compatible and features horizontal scalability, strong consistency, and high availability. TiDB can be deployed on-premise or in-cloud.

The TiDB source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Resulting schema

The TiDB source does not alter the schema present in your database. Depending on the destination connected to this source, however, the schema may be altered. See the destination's documentation for more details.

### Features

| Feature                       | Supported | Notes |
| :---------------------------- | :-------- | :---- |
| Full Refresh Sync             | Yes       |       |
| Incremental - Append Sync     | Yes       |       |
| Replicate Incremental Deletes | Yes       |       |
| Change Data Capture           | No        |       |
| SSL Support                   | Yes       |       |
| SSH Tunnel Connection         | Yes       |       |

## Getting started

### Requirements

1. TiDB `v4.0` or above
2. Allow connections from Airbyte to your TiDB database \(if they exist in separate VPCs\)
3. (Optional) Create a dedicated read-only Airbyte user with access to all tables needed for replication

**Note:** When connecting to [TiDB Cloud](https://en.pingcap.com/tidb-cloud/) with TLS enabled, you need to specify TLS protocol, such as `enabledTLSProtocols=TLSv1.2` or `enabledTLSProtocols=TLSv1.3` in the JDBC parameters.

### Setup guide

#### 1. Make sure your database is accessible from the machine running Airbyte

This is dependent on your networking setup. The easiest way to verify if Airbyte is able to connect to your TiDB instance is via the check connection tool in the UI.

#### 2. Create a dedicated read-only user with access to the relevant tables \(Recommended but optional\)

This step is optional but highly recommended to allow for better permission control and auditing. Alternatively, you can use Airbyte with an existing user in your database.

To create a dedicated database user, run the following commands against your database:

```sql
CREATE USER 'airbyte'@'%' IDENTIFIED BY 'your_password_here';
```

Then give it access to the relevant database:

```sql
GRANT SELECT ON <database name>.* TO 'airbyte'@'%';
```

#### 3. That's it!

Your database user should now be ready for use with Airbyte.

### Connection via SSH Tunnel

Airbyte has the ability to connect to a TiDB instance via an SSH Tunnel. The reason you might want to do this because it is not possible \(or against security policy\) to connect to the database directly \(e.g. it does not have a public IP address\).

When using an SSH tunnel, you are configuring Airbyte to connect to an intermediate server \(a.k.a. a bastion sever\) that _does_ have direct access to the database. Airbyte connects to the bastion and then asks the bastion to connect directly to the server.

Using this feature requires additional configuration, when creating the source. We will talk through what each piece of configuration means.

1. Configure all fields for the source as you normally would, except `SSH Tunnel Method`.
2. `SSH Tunnel Method` defaults to `No Tunnel` \(meaning a direct connection\). If you want to use an SSH Tunnel choose `SSH Key Authentication` or `Password Authentication`.
    1. Choose `Key Authentication` if you will be using an RSA private key as your secret for establishing the SSH Tunnel \(see below for more information on generating this key\).
    2. Choose `Password Authentication` if you will be using a password as your secret for establishing the SSH Tunnel.
3. `SSH Tunnel Jump Server Host` refers to the intermediate \(bastion\) server that Airbyte will connect to. This should be a hostname or an IP Address.
4. `SSH Connection Port` is the port on the bastion server with which to make the SSH connection. The default port for SSH connections is `22`, so unless you have explicitly changed something, go with the default.
5. `SSH Login Username` is the username that Airbyte should use when connection to the bastion server. This is NOT the TiDB username.
6. If you are using `Password Authentication`, then `SSH Login Username` should be set to the password of the User from the previous step. If you are using `SSH Key Authentication` TiDB password, but the password for the OS-user that Airbyte is using to perform commands on the bastion.
7. If you are using `SSH Key Authentication`, then `SSH Private Key` should be set to the RSA Private Key that you are using to create the SSH connection. This should be the full contents of the key file starting with `-----BEGIN RSA PRIVATE KEY-----` and ending with `-----END RSA PRIVATE KEY-----`.

## Data type mapping

[TiDB data types](https://docs.pingcap.com/tidb/stable/data-type-overview) are mapped to the following data types when synchronizing data:

| TiDB Type                                 | Resulting Type         | Notes                                                        |
| :---------------------------------------- |:-----------------------| :----------------------------------------------------------- |
| `bit(1)`                                  | boolean                |                                                              |
| `bit(>1)`                                 | base64 binary string   |                                                              |
| `boolean`                                 | boolean                |                                                              |
| `tinyint(1)`                              | boolean                |                                                              |
| `tinyint`                                 | number                 |                                                              |
| `smallint`                                | number                 |                                                              |
| `mediumint`                               | number                 |                                                              |
| `int`                                     | number                 |                                                              |
| `bigint`                                  | number                 |                                                              |
| `float`                                   | number                 |                                                              |
| `double`                                  | number                 |                                                              |
| `decimal`                                 | number                 |                                                              |
| `binary`                                  | base64 binary string   |                                                              |
| `blob`                                    | base64 binary string   |                                                              |
| `date`                                    | string                 | ISO 8601 date string. ZERO-DATE value will be converted to NULL. If column is mandatory, convert to EPOCH. |
| `datetime`, `timestamp`                   | string                 | ISO 8601 datetime string. ZERO-DATE value will be converted to NULL. If column is mandatory, convert to EPOCH. |
| `time`                                    | string                 | ISO 8601 time string. Values are in range between 00:00:00 and 23:59:59. |
| `year`                                    | year string            | [Doc](https://docs.pingcap.com/tidb/stable/data-type-date-and-time#year-type)     |
| `char`, `varchar` with non-binary charset | string                 |                                                              |
| `char`, `varchar` with binary charset     | base64 binary string   |                                                              |
| `tinyblob`                                | base64 binary string   |                                                              |
| `blob`                                    | base64 binary string   |                                                              |
| `mediumblob`                              | base64 binary string   |                                                              |
| `longblob`                                | base64 binary string   |                                                              |
| `binary`                                  | base64 binary string   |                                                              |
| `varbinary`                               | base64 binary string   |                                                              |
| `tinytext`                                | string                 |                                                              |
| `text`                                    | string                 |                                                              |
| `mediumtext`                              | string                 |                                                              |
| `longtext`                                | string                 |                                                              |
| `json`                                    | serialized json string | E.g. `{"a": 10, "b": 15}`                                    |
| `enum`                                    | string                 |                                                              |
| `set`                                     | string                 | E.g. `blue,green,yellow`                                     |


**Note:** arrays for all the above types as well as custom types are supported, although they may be de-nested depending on the destination.

## External resources

Now that you have set up the TiDB source connector, check out the following TiDB tutorial:

- [Using Airbyte to Migrate Data from TiDB Cloud to Snowflake](https://en.pingcap.com/blog/using-airbyte-to-migrate-data-from-tidb-cloud-to-snowflake/)

## Changelog

| Version | Date | Pull Request | Subject |
|:--------| :--- | :----------- | ------- |
| 0.2.5   | 2023-06-20 | [27212](https://github.com/airbytehq/airbyte/pull/27212) | Fix silent exception swallowing in StreamingJdbcDatabase                                                                                                                  |
| 0.2.4   | 2023-03-22 | [20760](https://github.com/airbytehq/airbyte/pull/20760) | Removed redundant date-time datatypes formatting   |
| 0.2.3   | 2023-03-06 | [23455](https://github.com/airbytehq/airbyte/pull/23455)   | For network isolation, source connector accepts a list of hosts it is allowed to connect to |
| 0.2.2   | 2022-12-14 | [20436](https://github.com/airbytehq/airbyte/pull/20346)   | Consolidate date/time values mapping for JDBC sources                          |
|         | 2022-10-13 | [15535](https://github.com/airbytehq/airbyte/pull/16238) | Update incremental query to avoid data missing when new data is inserted at the same time as a sync starts under non-CDC incremental mode |
| 0.2.1   | 2022-09-01 | [16238](https://github.com/airbytehq/airbyte/pull/16238) | Emit state messages more frequently |
| 0.2.0   | 2022-07-26 | [14362](https://github.com/airbytehq/airbyte/pull/14362) | Integral columns are now discovered as int64 fields. |
| 0.1.5   | 2022-07-25 | [14996](https://github.com/airbytehq/airbyte/pull/14996) | Removed additionalProperties:false from spec |
| 0.1.4   | 2022-07-22 | [14714](https://github.com/airbytehq/airbyte/pull/14714) | Clarified error message when invalid cursor column selected |
| 0.1.3   | 2022-07-04 | [14243](https://github.com/airbytehq/airbyte/pull/14243) | Update JDBC string builder |
| 0.1.2   | 2022-06-17 | [13864](https://github.com/airbytehq/airbyte/pull/13864) | Updated stacktrace format for any trace message errors |
| 0.1.1   | 2022-04-29 | [12480](https://github.com/airbytehq/airbyte/pull/12480) | Query tables with adaptive fetch size to optimize JDBC memory consumption |
| 0.1.0   | 2022-04-19 | [11283](https://github.com/airbytehq/airbyte/pull/11283) | Initial Release |
