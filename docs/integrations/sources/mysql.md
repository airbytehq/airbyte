# MySQL

Airbyte's certified MySQL connector offers the following features:

- Multiple methods of keeping your data fresh, including [Change Data Capture (CDC)](https://docs.airbyte.com/understanding-airbyte/cdc) using the [binlog](https://dev.mysql.com/doc/refman/8.0/en/binary-log.html).
- All available [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes), providing flexibility in how data is delivered to your destination.
- Reliable replication at any table size with [checkpointing](https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/#state--checkpointing) and chunking of database reads.

The contents below include a 'Quick Start' guide, advanced setup steps, and reference information (data type mapping and changelogs).
<!-- env:oss -->
**Please note the minimum required platform version is v0.58.0 to run source-mysql 3.4.0.**
<!-- /env:oss -->

## Quick Start

Here is an outline of the minimum required steps to configure a MySQL connector:

1. Create a dedicated read-only MySQL user with permissions for replicating data
2. Create a new MySQL source in the Airbyte UI using CDC logical replication
3. (Airbyte Cloud Only) Allow inbound traffic from Airbyte IPs

Once this is complete, you will be able to select MySQL as a source for replicating data.

<FieldAnchor field="username,password">

#### Step 1: Create a dedicated read-only MySQL user

These steps create a dedicated read-only user for replicating data. Alternatively, you can use an existing MySQL user in your database.

The following commands will create a new user:

```roomsql
CREATE USER <user_name> IDENTIFIED BY 'your_password_here';
```

Now, provide this user with read-only access to relevant schemas and tables:

```roomsql
GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO <user_name>;
```

If choosing to run using the `STANDARD` replication method (not recommended), only the `SELECT` permission is required.

</FieldAnchor>

<FieldAnchor field="replication_method[CDC]">

#### Step 2: Enable binary logging on your MySQL server

You must enable binary logging for MySQL replication using CDC. Most cloud providers (AWS, GCP, etc.) provide easy one-click options for enabling the binlog on your source MySQL database.

If you are self-managing your MySQL server, configure your MySQL server configuration file with the following properties:

<details>
  <summary>Configuring MySQL server config files to enable binlog</summary>

```text
server-id                  = 223344
log_bin                    = mysql-bin
binlog_format              = ROW
binlog_row_image           = FULL
binlog_expire_logs_seconds  = 864000
```

- server-id : The value for the server-id must be unique for each server and replication client in the MySQL cluster. The `server-id` should be a non-zero value. If the `server-id` is already set to a non-zero value, you don't need to make any change. You can set the `server-id` to any value between 1 and 4294967295. For more information refer [mysql doc](https://dev.mysql.com/doc/refman/8.0/en/replication-options.html#sysvar_server_id)
- log_bin : The value of log_bin is the base name of the sequence of binlog files. If the `log_bin` is already set, you don't need to make any change. For more information refer [mysql doc](https://dev.mysql.com/doc/refman/8.0/en/replication-options-binary-log.html#option_mysqld_log-bin)
- binlog_format : The `binlog_format` must be set to `ROW`. For more information refer [mysql doc](https://dev.mysql.com/doc/refman/8.0/en/replication-options-binary-log.html#sysvar_binlog_format)
- binlog_row_image : The `binlog_row_image` must be set to `FULL`. It determines how row images are written to the binary log. For more information refer [mysql doc](https://dev.mysql.com/doc/refman/5.7/en/replication-options-binary-log.html#sysvar_binlog_row_image)
- binlog_expire_logs_seconds : This is the number of seconds for automatic binlog file removal. We recommend 864000 seconds (10 days) so that in case of a failure in sync or if the sync is paused, we still have some bandwidth to start from the last point in incremental sync. We also recommend setting frequent syncs for CDC.

</details>

</FieldAnchor>

<FieldAnchor field="host, port, database">

#### Step 3: Create a new MySQL source in Airbyte UI

From your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) or Airbyte Open Source account, select `Sources` from the left navigation bar, search for `MySQL`, then create a new MySQL source.

To fill out the required information:

1. Enter the hostname, port number, and name for your MySQL database.
2. Enter the username and password you created in [Step 1](#step-1-create-a-dedicated-read-only-mysql-user).
3. Select an SSL mode. You will most frequently choose `require` or `verify-ca`. Both of these always require encryption. `verify-ca` also requires certificates from your MySQL database. See [here](#ssl-modes) to learn about other SSL modes and SSH tunneling.
4. Select `Read Changes using Binary Log (CDC)` from available replication methods.

<!-- env:cloud -->

#### Step 4: (Airbyte Cloud Only) Allow inbound traffic from Airbyte IPs.

If you are on Airbyte Cloud, you will always need to modify your database configuration to allow inbound traffic from Airbyte IPs. You can find a list of all IPs that need to be allowlisted in
our [Airbyte Security docs](../../operating-airbyte/security#network-security-1).

Now, click `Set up source` in the Airbyte UI. Airbyte will now test connecting to your database. Once this succeeds, you've configured an Airbyte MySQL source!

<!-- /env:cloud -->

</FieldAnchor>

## MySQL Replication Modes

### Change Data Capture \(CDC\)

Airbyte uses logical replication of the [MySQL binlog](https://dev.mysql.com/doc/refman/8.0/en/binary-log.html) to incrementally capture deletes. To learn more how Airbyte implements CDC, refer to [Change Data Capture (CDC)](https://docs.airbyte.com/understanding-airbyte/cdc/). We generally recommend configure your MySQL source with CDC whenever possible, as it provides:

- A record of deletions, if needed.
- Scalable replication to large tables (1 TB and more).
- A reliable cursor not reliant on the nature of your data. For example, if your table has a primary key but doesn't have a reasonable cursor field for incremental syncing \(i.e. `updated_at`\), CDC allows you to sync your table incrementally.

<FieldAnchor field="replication_method[STANDARD]">

### Standard

Airbyte offers incremental replication using a custom cursor available in your source tables (e.g. `updated_at`). We generally recommend against this replication method, but it is well suited for the following cases:

- Your MySQL server does not expose the binlog.
- Your data set is small, and you just want snapshot of your table in the destination.

</FieldAnchor>

## Connecting with SSL or SSH Tunneling

<FieldAnchor field="ssl">

### SSL Modes

Airbyte Cloud uses SSL by default. You are not permitted to `disable` SSL while using Airbyte Cloud.

Here is a breakdown of available SSL connection modes:

- `disable` to disable encrypted communication between Airbyte and the source
- `allow` to enable encrypted communication only when required by the source
- `prefer` to allow unencrypted communication only when the source doesn't support encryption
- `require` to always require encryption. Note: The connection will fail if the source doesn't support encryption.
- `verify-ca` to always require encryption and verify that the source has a valid SSL certificate
- `verify-full` to always require encryption and verify the identity of the source

</FieldAnchor>

### Connection via SSH Tunnel

You can connect to a MySQL server via an SSH tunnel.

When using an SSH tunnel, you are configuring Airbyte to connect to an intermediate server (also called a bastion or a jump server) that has direct access to the database. Airbyte connects to the bastion and then asks the bastion to connect directly to the server.

To connect to a MySQL server via an SSH tunnel:

1. While setting up the MySQL source connector, from the SSH tunnel dropdown, select:
   - SSH Key Authentication to use a private as your secret for establishing the SSH tunnel
   - Password Authentication to use a password as your secret for establishing the SSH Tunnel
2. For **SSH Tunnel Jump Server Host**, enter the hostname or IP address for the intermediate (bastion) server that Airbyte will connect to.
3. For **SSH Connection Port**, enter the port on the bastion server. The default port for SSH connections is 22.
4. For **SSH Login Username**, enter the username to use when connecting to the bastion server. **Note:** This is the operating system username and not the MySQL username.
5. For authentication:
   - If you selected **SSH Key Authentication**, set the **SSH Private Key** to the [private Key](#generating-a-private-key-for-ssh-tunneling) that you are using to create the SSH connection.
   - If you selected **Password Authentication**, enter the password for the operating system user to connect to the bastion server. **Note:** This is the operating system password and not the MySQL password.

#### Generating a private key for SSH Tunneling

The connector expects an RSA key in PEM format. To generate this key:

```text
ssh-keygen -t rsa -m PEM -f myuser_rsa
```

This produces the private key in pem format, and the public key remains in the standard format used by the `authorized_keys` file on your bastion host. The public key should be added to your bastion host to whichever user you want to use with Airbyte. The private key is provided via copy-and-paste to the Airbyte connector configuration screen, so it may log in to the bastion.

## Limitations & Troubleshooting

To see connector limitations, or troubleshoot your MySQL connector, see more [in our MySQL troubleshooting guide](/integrations/sources/mysql/mysql-troubleshooting).

## Data Type Mapping

MySQL data types are mapped to the following data types when synchronizing data. You can check test example values [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-mysql/src/test-integration/java/io/airbyte/integrations/io/airbyte/integration_tests/sources/MySqlSourceDatatypeTest.java). If you can't find the data type you are looking for, feel free to add a new test.
If you do not see a type in this list, assume that it is coerced into a string. We are happy to take feedback on preferred mappings.

Any database or table encoding combination of charset and collation is supported. Charset setting however will not be carried over to destination and data will be encoded with whatever is configured by the destination. Please note that byte arrays are not yet supported.

<details>
    <summary>MySQL Data Type Mapping</summary>

| MySQL Type                                | Resulting Type         | Notes                                                                                                          |
| :---------------------------------------- | :--------------------- | :------------------------------------------------------------------------------------------------------------- |
| `bit(1)`                                  | boolean                |                                                                                                                |
| `bit(>1)`                                 | base64 binary string   |                                                                                                                |
| `boolean`                                 | boolean                |                                                                                                                |
| `tinyint(1)`                              | boolean                |                                                                                                                |
| `tinyint(>1)`                             | number                 |                                                                                                                |
| `tinyint(>=1) unsigned`                   | number                 |                                                                                                                |
| `smallint`                                | number                 |                                                                                                                |
| `mediumint`                               | number                 |                                                                                                                |
| `int`                                     | number                 |                                                                                                                |
| `bigint`                                  | number                 |                                                                                                                |
| `float`                                   | number                 |                                                                                                                |
| `double`                                  | number                 |                                                                                                                |
| `decimal`                                 | number                 |                                                                                                                |
| `binary`                                  | string                 |                                                                                                                |
| `blob`                                    | string                 |                                                                                                                |
| `date`                                    | string                 | ISO 8601 date string. ZERO-DATE value will be converted to NULL. If column is mandatory, convert to EPOCH.     |
| `datetime`, `timestamp`                   | string                 | ISO 8601 datetime string. ZERO-DATE value will be converted to NULL. If column is mandatory, convert to EPOCH. |
| `time`                                    | string                 | ISO 8601 time string. Values are in range between 00:00:00 and 23:59:59.                                       |
| `year`                                    | year string            | [Doc](https://dev.mysql.com/doc/refman/8.0/en/year.html)                                                       |
| `char`, `varchar` with non-binary charset | string                 |                                                                                                                |
| `tinyblob`                                | base64 binary string   |                                                                                                                |
| `blob`                                    | base64 binary string   |                                                                                                                |
| `mediumblob`                              | base64 binary string   |                                                                                                                |
| `longblob`                                | base64 binary string   |                                                                                                                |
| `binary`                                  | base64 binary string   |                                                                                                                |
| `varbinary`                               | base64 binary string   |                                                                                                                |
| `tinytext`                                | string                 |                                                                                                                |
| `text`                                    | string                 |                                                                                                                |
| `mediumtext`                              | string                 |                                                                                                                |
| `longtext`                                | string                 |                                                                                                                |
| `json`                                    | serialized json string | E.g. `{"a": 10, "b": 15}`                                                                                      |
| `enum`                                    | string                 |                                                                                                                |
| `set`                                     | string                 | E.g. `blue,green,yellow`                                                                                       |
| `geometry`                                | base64 binary string   |                                                                                                                |

</details>

## Changelog

<details>
  <summary>Expand to review</summary>

| Version     | Date       | Pull Request                                               | Subject                                                                                                                                         |
|:------------|:-----------|:-----------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------|
| 3.11.0 | 2025-01-14 | [51545](https://github.com/airbytehq/airbyte/pull/51545) | Promoting release candidate 3.11.0-rc.1 to a main version. |
| 3.11.0-rc.1 | 2025-01-09 | [51029](https://github.com/airbytehq/airbyte/pull/51029) | Fix unnecessary schema change when upgrading from legacy mysql source.                                                                          |
| 3.10.1      | 2025-01-10 | [51510](https://github.com/airbytehq/airbyte/pull/51510) | Use a non root base image |
| 3.10.0      | 2025-01-09 | [51008](https://github.com/airbytehq/airbyte/pull/51008) | Promoting release candidate 3.10.0-rc.9 to a main version. |
| 3.10.0-rc.9 | 2025-01-08 | [50987](https://github.com/airbytehq/airbyte/pull/50987)   | Increase Debezium shutdown timeout.                                                                                                             |
| 3.10.0-rc.8 | 2025-01-07 | [50965](https://github.com/airbytehq/airbyte/pull/50965)   | Fix bug introduced in 3.10.0-rc.3.                                                                                                              |
| 3.10.0-rc.7 | 2024-12-27 | [50437](https://github.com/airbytehq/airbyte/pull/50437)   | Compatibility with MySQL Views.                                                                                                                 |
| 3.10.0-rc.6 | 2024-12-18 | [49892](https://github.com/airbytehq/airbyte/pull/49892)   | Use a base image: airbyte/java-connector-base:1.0.0                                                                                             |
| 3.10.0-rc.5 | 2025-01-03 | [50868](https://github.com/airbytehq/airbyte/pull/50868)   | Fix exception handling rules declaration.                                                                                                       |
| 3.10.0-rc.4 | 2024-12-23 | [48587](https://github.com/airbytehq/airbyte/pull/48587)   | Fix minor state counting mechanism.                                                                                                             |
| 3.10.0-rc.3 | 2024-12-20 | [49918](https://github.com/airbytehq/airbyte/pull/49918)   | Fix minor datatype handling and conversion bugs, maintain big number precision.                                                                 |
| 3.10.0-rc.2 | 2024-12-20 | [49950](https://github.com/airbytehq/airbyte/pull/49950)   | Remove unused configuration field, streamline SSL certificate key store logic.                                                                  |
| 3.10.0-rc.1 | 2024-12-20 | [49948](https://github.com/airbytehq/airbyte/pull/49948)   | Pin Bulk CDK version to 231, adopt required changes.                                                                                            |
| 3.9.4       | 2024-12-18 | [49939](https://github.com/airbytehq/airbyte/pull/49939)   | Pin Bulk CDK version to 226, rename classes.                                                                                                    |
| 3.9.3       | 2024-12-18 | [49932](https://github.com/airbytehq/airbyte/pull/49932)   | Backward compatibility for saved states with timestamp that include timezone offset.                                                            |
| 3.9.2       | 2024-12-16 | [49830](https://github.com/airbytehq/airbyte/pull/49830)   | Fixes an issue with auto generated tinyint columns                                                                                              |
| 3.9.1       | 2024-12-12 | [49456](https://github.com/airbytehq/airbyte/pull/49456)   | Bump version to re-relase                                                                                                                       |
| 3.9.0       | 2024-12-12 | [49423](https://github.com/airbytehq/airbyte/pull/49423)   | Promoting release candidate 3.9.0-rc.27 to a main version.                                                                                      |
| 3.9.0-rc    | 2024-11-05 | [48369](https://github.com/airbytehq/airbyte/pull/48369)   | Progressive rollout test.                                                                                                                       |
| 3.7.3       | 2024-09-17 | [45639](https://github.com/airbytehq/airbyte/pull/45639)   | Adopt latest CDK to use the latest apache sshd mina to handle tcpkeepalive requests.                                                            |
| 3.7.2       | 2024-09-05 | [45181](https://github.com/airbytehq/airbyte/pull/45181)   | Fix incorrect categorizing resumable/nonresumable full refresh streams.                                                                         |
| 3.7.1       | 2024-08-27 | [44841](https://github.com/airbytehq/airbyte/pull/44841)   | Adopt latest CDK.                                                                                                                               |
| 3.7.0       | 2024-08-13 | [44013](https://github.com/airbytehq/airbyte/pull/44013)   | Upgrading to Debezium 2.7.1.Final                                                                                                               |
| 3.6.9       | 2024-08-08 | [43410](https://github.com/airbytehq/airbyte/pull/43410)   | Adopt latest CDK.                                                                                                                               |
| 3.6.8       | 2024-07-30 | [42869](https://github.com/airbytehq/airbyte/pull/42869)   | Adopt latest CDK.                                                                                                                               |
| 3.6.7       | 2024-07-30 | [42550](https://github.com/airbytehq/airbyte/pull/42550)   | Correctly report stream states.                                                                                                                 |
| 3.6.6       | 2024-07-29 | [42852](https://github.com/airbytehq/airbyte/pull/42852)   | Bump CDK version to latest to use new bug fixes on error translation.                                                                           |
| 3.6.5       | 2024-07-24 | [42417](https://github.com/airbytehq/airbyte/pull/42417)   | Handle null error message in ConnectorExceptionHandler.                                                                                         |
| 3.6.4       | 2024-07-23 | [42421](https://github.com/airbytehq/airbyte/pull/42421)   | Remove final transient error emitter iterators.                                                                                                 |
| 3.6.3       | 2024-07-22 | [42024](https://github.com/airbytehq/airbyte/pull/42024)   | Fix a NPE bug on resuming from a failed attempt.                                                                                                |
| 3.6.2       | 2024-07-17 | [42087](https://github.com/airbytehq/airbyte/pull/42087)   | Adding more error translations for MySql source.                                                                                                |
| 3.6.1       | 2024-07-19 | [42122](https://github.com/airbytehq/airbyte/pull/42122)   | Improve wass error message + logging.                                                                                                           |
| 3.6.0       | 2024-07-17 | [40208](https://github.com/airbytehq/airbyte/pull/40208)   | Start using the new error MySql source error handler that comes with a new error translation layer.                                             | 
| 3.5.1       | 2024-07-17 | [42043](https://github.com/airbytehq/airbyte/pull/42043)   | Adopt latest CDK + fixes.                                                                                                                       |
| 3.5.0       | 2024-07-11 | [38240](https://github.com/airbytehq/airbyte/pull/38240)   | Implement WASS.                                                                                                                                 |
| 3.4.12      | 2024-07-01 | [40516](https://github.com/airbytehq/airbyte/pull/40516)   | Remove dbz heartbeat.                                                                                                                           |
| 3.4.11      | 2024-06-26 | [40561](https://github.com/airbytehq/airbyte/pull/40561)   | Support PlanetScale MySQL's per-query row limit.                                                                                                |
| 3.4.10      | 2024-06-14 | [39349](https://github.com/airbytehq/airbyte/pull/39349)   | Full refresh stream sending internal count metadata.                                                                                            |
| 3.4.9       | 2024-06-11 | [39405](https://github.com/airbytehq/airbyte/pull/39405)   | Adopt latest CDK.                                                                                                                               |
| 3.4.8       | 2024-06-05 | [39144](https://github.com/airbytehq/airbyte/pull/39144)   | Upgrade Debezium to 2.5.4                                                                                                                       |
| 3.4.7       | 2024-05-29 | [38584](https://github.com/airbytehq/airbyte/pull/38584)   | Set is_resumable flag in discover.                                                                                                              |
| 3.4.6       | 2024-05-29 | [38538](https://github.com/airbytehq/airbyte/pull/38538)   | Exit connector when encountering a config error.                                                                                                |
| 3.4.5       | 2024-05-23 | [38198](https://github.com/airbytehq/airbyte/pull/38198)   | Sync sending trace status messages indicating progress.                                                                                         |
| 3.4.4       | 2024-05-15 | [38208](https://github.com/airbytehq/airbyte/pull/38208)   | disable counts in full refresh stream in state message.                                                                                         |
| 3.4.3       | 2024-05-13 | [38104](https://github.com/airbytehq/airbyte/pull/38104)   | Handle transient error messages.                                                                                                                |
| 3.4.2       | 2024-05-07 | [38046](https://github.com/airbytehq/airbyte/pull/38046)   | Resumeable refresh should run only if there is source defined pk.                                                                               |
| 3.4.1       | 2024-05-03 | [37824](https://github.com/airbytehq/airbyte/pull/37824)   | Fixed a bug on Resumeable full refresh where cursor based source throw NPE.                                                                     |
| 3.4.0       | 2024-05-02 | [36932](https://github.com/airbytehq/airbyte/pull/36932)   | Resumeable full refresh. Note please upgrade your platform - minimum platform version is 0.58.0.                                                |
| 3.3.25      | 2024-05-02 | [37781](https://github.com/airbytehq/airbyte/pull/37781)   | Adopt latest CDK.                                                                                                                               |
| 3.3.24      | 2024-05-01 | [37742](https://github.com/airbytehq/airbyte/pull/37742)   | Adopt latest CDK. Remove Debezium retries.                                                                                                      |
| 3.3.23      | 2024-04-23 | [37507](https://github.com/airbytehq/airbyte/pull/37507)   | Better errors when user switches from CDC to non-CDC mode.                                                                                      |
| 3.3.22      | 2024-04-22 | [37541](https://github.com/airbytehq/airbyte/pull/37541)   | Adopt latest CDK. reduce excessive logs.                                                                                                        |
| 3.3.21      | 2024-04-22 | [37476](https://github.com/airbytehq/airbyte/pull/37476)   | Adopt latest CDK.                                                                                                                               |
| 3.3.20      | 2024-04-16 | [37111](https://github.com/airbytehq/airbyte/pull/37111)   | Populate null values in record message.                                                                                                         |
| 3.3.19      | 2024-04-15 | [37328](https://github.com/airbytehq/airbyte/pull/37328)   | Populate airbyte_meta.changes                                                                                                                   |
| 3.3.18      | 2024-04-15 | [37324](https://github.com/airbytehq/airbyte/pull/37324)   | Refactor source operations.                                                                                                                     |
| 3.3.17      | 2024-04-10 | [36919](https://github.com/airbytehq/airbyte/pull/36919)   | Fix a bug in conversion of null values.                                                                                                         |
| 3.3.16      | 2024-04-05 | [36872](https://github.com/airbytehq/airbyte/pull/36872)   | Update to connector's metadat definition.                                                                                                       |
| 3.3.15      | 2024-04-05 | [36577](https://github.com/airbytehq/airbyte/pull/36577)   | Config error will not send out system trace message                                                                                             |
| 3.3.14      | 2024-04-04 | [36742](https://github.com/airbytehq/airbyte/pull/36742)   | To use new kotlin CDK                                                                                                                           |
| 3.3.13      | 2024-02-29 | [35529](https://github.com/airbytehq/airbyte/pull/35529)   | Refactor state iterator messages.                                                                                                               |
| 3.3.12      | 2024-02-27 | [35675](https://github.com/airbytehq/airbyte/pull/35675)   | Fix invalid cdc error message.                                                                                                                  |
| 3.3.11      | 2024-02-23 | [35527](https://github.com/airbytehq/airbyte/pull/35527)   | Adopt 0.23.1 and shutdown timeouts.                                                                                                             |
| 3.3.10      | 2024-02-22 | [35569](https://github.com/airbytehq/airbyte/pull/35569)   | Fix logging bug.                                                                                                                                |
| 3.3.9       | 2024-02-21 | [35525](https://github.com/airbytehq/airbyte/pull/35338)   | Adopt 0.21.4 and reduce cdc state compression threshold to 1MB.                                                                                 |
| 3.3.8       | 2024-02-20 | [35338](https://github.com/airbytehq/airbyte/pull/35338)   | Add config to throw an error on invalid CDC position.                                                                                           |
| 3.3.7       | 2024-02-13 | [35036](https://github.com/airbytehq/airbyte/pull/34751)   | Emit analytics message for invalid CDC cursor.                                                                                                  |
| 3.3.6       | 2024-02-13 | [34869](https://github.com/airbytehq/airbyte/pull/34573)   | Don't emit state in SourceStateIterator when there is an underlying stream failure.                                                             |
| 3.3.5       | 2024-02-12 | [34580](https://github.com/airbytehq/airbyte/pull/34580)   | Support special chars in db name                                                                                                                |
| 3.3.4       | 2024-02-08 | [34750](https://github.com/airbytehq/airbyte/pull/34750)   | Adopt CDK 0.19.0                                                                                                                                |
| 3.3.3       | 2024-01-26 | [34573](https://github.com/airbytehq/airbyte/pull/34573)   | Adopt CDK v0.16.0.                                                                                                                              |
| 3.3.2       | 2024-01-08 | [33005](https://github.com/airbytehq/airbyte/pull/33005)   | Adding count stats for incremental sync in AirbyteStateMessage                                                                                  |
| 3.3.1       | 2024-01-03 | [33312](https://github.com/airbytehq/airbyte/pull/33312)   | Adding count stats in AirbyteStateMessage                                                                                                       |
| 3.3.0       | 2023-12-19 | [33436](https://github.com/airbytehq/airbyte/pull/33436)   | Remove LEGACY state flag                                                                                                                        |
| 3.2.4       | 2023-12-12 | [33356](https://github.com/airbytehq/airbyte/pull/33210)   | Support for better debugging tools..                                                                                                            |
| 3.2.3       | 2023-12-08 | [33210](https://github.com/airbytehq/airbyte/pull/33210)   | Update MySql driver property value for zero date handling.                                                                                      |
| 3.2.2       | 2023-12-06 | [33082](https://github.com/airbytehq/airbyte/pull/33082)   | Improvements to MySQL schema snapshot error handling.                                                                                           |
| 3.2.1       | 2023-11-28 | [32610](https://github.com/airbytehq/airbyte/pull/32610)   | Support initial syncs using binary as primary key.                                                                                              |
| 3.2.0       | 2023-11-29 | [31062](https://github.com/airbytehq/airbyte/pull/31062)   | enforce SSL on Airbyte Cloud                                                                                                                    |
| 3.1.9       | 2023-11-27 | [32662](https://github.com/airbytehq/airbyte/pull/32662)   | Apply initial setup time to debezium engine warmup time.                                                                                        |
| 3.1.8       | 2023-11-22 | [32656](https://github.com/airbytehq/airbyte/pull/32656)   | Adopt java CDK version 0.5.0.                                                                                                                   |
| 3.1.7       | 2023-11-08 | [32125](https://github.com/airbytehq/airbyte/pull/32125)   | fix compilation warnings                                                                                                                        |
| 3.1.6       | 2023-11-06 | [32193](https://github.com/airbytehq/airbyte/pull/32193)   | Adopt java CDK version 0.4.1.                                                                                                                   |
| 3.1.5       | 2023-10-31 | [32024](https://github.com/airbytehq/airbyte/pull/32024)   | Upgrade to Debezium version 2.4.0.                                                                                                              |
| 3.1.4       | 2023-10-30 | [31960](https://github.com/airbytehq/airbyte/pull/31960)   | Adopt java CDK version 0.2.0.                                                                                                                   |
| 3.1.3       | 2023-10-11 | [31322](https://github.com/airbytehq/airbyte/pull/31322)   | Correct pevious release                                                                                                                         |
| 3.1.2       | 2023-09-29 | [30806](https://github.com/airbytehq/airbyte/pull/30806)   | Cap log line length to 32KB to prevent loss of records                                                                                          |
| 3.1.1       | 2023-09-26 | [30744](https://github.com/airbytehq/airbyte/pull/30744)   | Update MySQL JDBC connection configs to keep default auto-commit behavior                                                                       |
| 3.1.0       | 2023-09-21 | [30270](https://github.com/airbytehq/airbyte/pull/30270)   | Enhanced Standard Sync with initial load via Primary Key with a switch to cursor for incremental syncs                                          |
| 3.0.9       | 2023-09-20 | [30620](https://github.com/airbytehq/airbyte/pull/30620)   | Airbyte Certified MySQL Source connector                                                                                                        |
| 3.0.8       | 2023-09-14 | [30333](https://github.com/airbytehq/airbyte/pull/30333)   | CDC : Update the correct timezone parameter passed to Debezium to `database.connectionTimezone`                                                 |
| 3.0.7       | 2023-09-13 | [30375](https://github.com/airbytehq/airbyte/pull/30375)   | Fix a bug causing a failure when DB views are included in sync                                                                                  |
| 3.0.6       | 2023-09-12 | [30308](https://github.com/airbytehq/airbyte/pull/30308)   | CDC : Enable compression of schema history blob in state                                                                                        |
| 3.0.5       | 2023-09-12 | [30289](https://github.com/airbytehq/airbyte/pull/30289)   | CDC : Introduce logic for compression of schema history blob in state                                                                           |
| 3.0.4       | 2023-09-06 | [30213](https://github.com/airbytehq/airbyte/pull/30213)   | CDC : Checkpointable initial snapshot                                                                                                           |
| 3.0.3       | 2023-08-31 | [29821](https://github.com/airbytehq/airbyte/pull/29821)   | Set replication_method display_type to radio                                                                                                    |
| 3.0.2       | 2023-08-30 | [30015](https://github.com/airbytehq/airbyte/pull/30015)   | Logging : Log storage engines associated with tables in the sync                                                                                |
| 3.0.1       | 2023-08-21 | [29308](https://github.com/airbytehq/airbyte/pull/29308)   | CDC: Enable frequent state emissions during incremental runs                                                                                    |
| 3.0.0       | 2023-08-08 | [28756](https://github.com/airbytehq/airbyte/pull/28756)   | CDC: Set a default cursor                                                                                                                       |
| 2.1.2       | 2023-08-08 | [29220](https://github.com/airbytehq/airbyte/pull/29220)   | Add indicator that CDC is the recommended update method                                                                                         |
| 2.1.1       | 2023-07-31 | [28882](https://github.com/airbytehq/airbyte/pull/28882)   | Improve replication method labels and descriptions                                                                                              |
| 2.1.0       | 2023-06-26 | [27737](https://github.com/airbytehq/airbyte/pull/27737)   | License Update: Elv2                                                                                                                            |
| 2.0.25      | 2023-06-20 | [27212](https://github.com/airbytehq/airbyte/pull/27212)   | Fix silent exception swallowing in StreamingJdbcDatabase                                                                                        |
| 2.0.24      | 2023-05-25 | [26473](https://github.com/airbytehq/airbyte/pull/26473)   | CDC : Limit queue size                                                                                                                          |
| 2.0.23      | 2023-05-24 | [25586](https://github.com/airbytehq/airbyte/pull/25586)   | No need to base64 encode strings on databases sorted with binary collation                                                                      |
| 2.0.22      | 2023-05-22 | [25859](https://github.com/airbytehq/airbyte/pull/25859)   | Allow adding sessionVariables JDBC parameters                                                                                                   |
| 2.0.21      | 2023-05-10 | [25460](https://github.com/airbytehq/airbyte/pull/25460)   | Handle a decimal number with 0 decimal points as an integer                                                                                     |
| 2.0.20      | 2023-05-01 | [25740](https://github.com/airbytehq/airbyte/pull/25740)   | Disable index logging                                                                                                                           |
| 2.0.19      | 2023-04-26 | [25401](https://github.com/airbytehq/airbyte/pull/25401)   | CDC : Upgrade Debezium to version 2.2.0                                                                                                         |
| 2.0.18      | 2023-04-19 | [25345](https://github.com/airbytehq/airbyte/pull/25345)   | Logging : Log database indexes per stream                                                                                                       |
| 2.0.17      | 2023-04-19 | [24582](https://github.com/airbytehq/airbyte/pull/24582)   | CDC : refactor for performance improvement                                                                                                      |
| 2.0.16      | 2023-04-17 | [25220](https://github.com/airbytehq/airbyte/pull/25220)   | Logging changes : Log additional metadata & clean up noisy logs                                                                                 |
| 2.0.15      | 2023-04-12 | [25131](https://github.com/airbytehq/airbyte/pull/25131)   | Make Client Certificate and Client Key always show                                                                                              |
| 2.0.14      | 2023-04-11 | [24656](https://github.com/airbytehq/airbyte/pull/24656)   | CDC minor refactor                                                                                                                              |
| 2.0.13      | 2023-04-06 | [24820](https://github.com/airbytehq/airbyte/pull/24820)   | Fix data loss bug during an initial failed non-CDC incremental sync                                                                             |
| 2.0.12      | 2023-04-04 | [24833](https://github.com/airbytehq/airbyte/pull/24833)   | Fix Debezium retry policy configuration                                                                                                         |
| 2.0.11      | 2023-03-28 | [24166](https://github.com/airbytehq/airbyte/pull/24166)   | Fix InterruptedException bug during Debezium shutdown                                                                                           |
| 2.0.10      | 2023-03-27 | [24529](https://github.com/airbytehq/airbyte/pull/24373)   | Preparing the connector for CDC checkpointing                                                                                                   |
| 2.0.9       | 2023-03-24 | [24529](https://github.com/airbytehq/airbyte/pull/24529)   | Set SSL Mode to required on strict-encrypt variant                                                                                              |
| 2.0.8       | 2023-03-22 | [20760](https://github.com/airbytehq/airbyte/pull/20760)   | Removed redundant date-time datatypes formatting                                                                                                |
| 2.0.7       | 2023-03-21 | [24207](https://github.com/airbytehq/airbyte/pull/24207)   | Fix incorrect schema change warning in CDC mode                                                                                                 |
| 2.0.6       | 2023-03-21 | [23984](https://github.com/airbytehq/airbyte/pull/23984)   | Support CDC heartbeats                                                                                                                          |
| 2.0.5       | 2023-03-21 | [24147](https://github.com/airbytehq/airbyte/pull/24275)   | Fix error with CDC checkpointing                                                                                                                |
| 2.0.4       | 2023-03-20 | [24147](https://github.com/airbytehq/airbyte/pull/24147)   | Support different table structure during "DESCRIBE" query                                                                                       |
| 2.0.3       | 2023-03-15 | [24082](https://github.com/airbytehq/airbyte/pull/24082)   | Fixed NPE during cursor values validation                                                                                                       |
| 2.0.2       | 2023-03-14 | [23908](https://github.com/airbytehq/airbyte/pull/23908)   | Log warning on null cursor values                                                                                                               |
| 2.0.1       | 2023-03-10 | [23939](https://github.com/airbytehq/airbyte/pull/23939)   | For network isolation, source connector accepts a list of hosts it is allowed to connect                                                        |
| 2.0.0       | 2023-03-06 | [23112](https://github.com/airbytehq/airbyte/pull/23112)   | Upgrade Debezium version to 2.1.2                                                                                                               |
| 1.0.21      | 2023-01-25 | [20939](https://github.com/airbytehq/airbyte/pull/20939)   | Adjust batch selection memory limits databases.                                                                                                 |
| 1.0.20      | 2023-01-24 | [20593](https://github.com/airbytehq/airbyte/pull/20593)   | Handle ssh time out exception                                                                                                                   |
| 1.0.19      | 2022-12-14 | [20436](https://github.com/airbytehq/airbyte/pull/20346)   | Consolidate date/time values mapping for JDBC sources                                                                                           |
| 1.0.18      | 2022-12-14 | [20378](https://github.com/airbytehq/airbyte/pull/20378)   | Improve descriptions                                                                                                                            |
| 1.0.17      | 2022-12-13 | [20289](https://github.com/airbytehq/airbyte/pull/20289)   | Mark unknown column exception as config error                                                                                                   |
| 1.0.16      | 2022-12-12 | [18959](https://github.com/airbytehq/airbyte/pull/18959)   | CDC : Don't timeout if snapshot is not complete.                                                                                                |
| 1.0.15      | 2022-12-06 | [20000](https://github.com/airbytehq/airbyte/pull/20000)   | Add check and better messaging when user does not have permission to access binary log in CDC mode                                              |
| 1.0.14      | 2022-11-22 | [19514](https://github.com/airbytehq/airbyte/pull/19514)   | Adjust batch selection memory limits databases.                                                                                                 |
| 1.0.13      | 2022-11-14 | [18956](https://github.com/airbytehq/airbyte/pull/18956)   | Clean up Tinyint Unsigned data type identification                                                                                              |
| 1.0.12      | 2022-11-07 | [19025](https://github.com/airbytehq/airbyte/pull/19025)   | Stop enforce SSL if ssl mode is disabled                                                                                                        |
| 1.0.11      | 2022-11-03 | [18851](https://github.com/airbytehq/airbyte/pull/18851)   | Fix bug with unencrypted CDC connections                                                                                                        |
| 1.0.10      | 2022-11-02 | [18619](https://github.com/airbytehq/airbyte/pull/18619)   | Fix bug with handling Tinyint(1) Unsigned values as boolean                                                                                     |
| 1.0.9       | 2022-10-31 | [18538](https://github.com/airbytehq/airbyte/pull/18538)   | Encode database name                                                                                                                            |
| 1.0.8       | 2022-10-25 | [18383](https://github.com/airbytehq/airbyte/pull/18383)   | Better SSH error handling + messages                                                                                                            |
| 1.0.7       | 2022-10-21 | [18263](https://github.com/airbytehq/airbyte/pull/18263)   | Fixes bug introduced in [15833](https://github.com/airbytehq/airbyte/pull/15833) and adds better error messaging for SSH tunnel in Destinations |
| 1.0.6       | 2022-10-19 | [18087](https://github.com/airbytehq/airbyte/pull/18087)   | Better error messaging for configuration errors (SSH configs, choosing an invalid cursor)                                                       |
| 1.0.5       | 2022-10-17 | [18041](https://github.com/airbytehq/airbyte/pull/18041)   | Fixes bug introduced 2022-09-12 with SshTunnel, handles iterator exception properly                                                             |
|             | 2022-10-13 | [15535](https://github.com/airbytehq/airbyte/pull/16238)   | Update incremental query to avoid data missing when new data is inserted at the same time as a sync starts under non-CDC incremental mode       |
| 1.0.4       | 2022-10-11 | [17815](https://github.com/airbytehq/airbyte/pull/17815)   | Expose setting server timezone for CDC syncs                                                                                                    |
| 1.0.3       | 2022-10-07 | [17236](https://github.com/airbytehq/airbyte/pull/17236)   | Fix large table issue by fetch size                                                                                                             |
| 1.0.2       | 2022-10-03 | [17170](https://github.com/airbytehq/airbyte/pull/17170)   | Make initial CDC waiting time configurable                                                                                                      |
| 1.0.1       | 2022-10-01 | [17459](https://github.com/airbytehq/airbyte/pull/17459)   | Upgrade debezium version to 1.9.6 from 1.9.2                                                                                                    |
| 1.0.0       | 2022-09-27 | [17164](https://github.com/airbytehq/airbyte/pull/17164)   | Certify MySQL Source as Beta                                                                                                                    |
| 0.6.15      | 2022-09-27 | [17299](https://github.com/airbytehq/airbyte/pull/17299)   | Improve error handling for strict-encrypt mysql source                                                                                          |
| 0.6.14      | 2022-09-26 | [16954](https://github.com/airbytehq/airbyte/pull/16954)   | Implement support for snapshot of new tables in CDC mode                                                                                        |
| 0.6.13      | 2022-09-14 | [15668](https://github.com/airbytehq/airbyte/pull/15668)   | Wrap logs in AirbyteLogMessage                                                                                                                  |
| 0.6.12      | 2022-09-13 | [16657](https://github.com/airbytehq/airbyte/pull/16657)   | Improve CDC record queueing performance                                                                                                         |
| 0.6.11      | 2022-09-08 | [16202](https://github.com/airbytehq/airbyte/pull/16202)   | Adds error messaging factory to UI                                                                                                              |
| 0.6.10      | 2022-09-08 | [16007](https://github.com/airbytehq/airbyte/pull/16007)   | Implement per stream state support.                                                                                                             |
| 0.6.9       | 2022-09-03 | [16216](https://github.com/airbytehq/airbyte/pull/16216)   | Standardize spec for CDC replication. See upgrade instructions [above](#upgrading-from-0.6.8-and-older-versions-to-0.6.9-and-later-versions).   |
| 0.6.8       | 2022-09-01 | [16259](https://github.com/airbytehq/airbyte/pull/16259)   | Emit state messages more frequently                                                                                                             |
| 0.6.7       | 2022-08-30 | [16114](https://github.com/airbytehq/airbyte/pull/16114)   | Prevent traffic going on an unsecured channel in strict-encryption version of source mysql                                                      |
| 0.6.6       | 2022-08-25 | [15993](https://github.com/airbytehq/airbyte/pull/15993)   | Improved support for connecting over SSL                                                                                                        |
| 0.6.5       | 2022-08-25 | [15917](https://github.com/airbytehq/airbyte/pull/15917)   | Fix temporal data type default value bug                                                                                                        |
| 0.6.4       | 2022-08-18 | [14356](https://github.com/airbytehq/airbyte/pull/14356)   | DB Sources: only show a table can sync incrementally if at least one column can be used as a cursor field                                       |
| 0.6.3       | 2022-08-12 | [15044](https://github.com/airbytehq/airbyte/pull/15044)   | Added the ability to connect using different SSL modes and SSL certificates                                                                     |
| 0.6.2       | 2022-08-11 | [15538](https://github.com/airbytehq/airbyte/pull/15538)   | Allow additional properties in db stream state                                                                                                  |
| 0.6.1       | 2022-08-02 | [14801](https://github.com/airbytehq/airbyte/pull/14801)   | Fix multiple log bindings                                                                                                                       |
| 0.6.0       | 2022-07-26 | [14362](https://github.com/airbytehq/airbyte/pull/14362)   | Integral columns are now discovered as int64 fields.                                                                                            |
| 0.5.17      | 2022-07-22 | [14714](https://github.com/airbytehq/airbyte/pull/14714)   | Clarified error message when invalid cursor column selected                                                                                     |
| 0.5.16      | 2022-07-14 | [14574](https://github.com/airbytehq/airbyte/pull/14574)   | Removed additionalProperties:false from JDBC source connectors                                                                                  |
| 0.5.15      | 2022-06-23 | [14077](https://github.com/airbytehq/airbyte/pull/14077)   | Use the new state management                                                                                                                    |
| 0.5.13      | 2022-06-21 | [13945](https://github.com/airbytehq/airbyte/pull/13945)   | Aligned datatype test                                                                                                                           |
| 0.5.12      | 2022-06-17 | [13864](https://github.com/airbytehq/airbyte/pull/13864)   | Updated stacktrace format for any trace message errors                                                                                          |
| 0.5.11      | 2022-05-03 | [12544](https://github.com/airbytehq/airbyte/pull/12544)   | Prevent source from hanging under certain circumstances by adding a watcher for orphaned threads.                                               |
| 0.5.10      | 2022-04-29 | [12480](https://github.com/airbytehq/airbyte/pull/12480)   | Query tables with adaptive fetch size to optimize JDBC memory consumption                                                                       |
| 0.5.9       | 2022-04-06 | [11729](https://github.com/airbytehq/airbyte/pull/11729)   | Bump mina-sshd from 2.7.0 to 2.8.0                                                                                                              |
| 0.5.6       | 2022-02-21 | [10242](https://github.com/airbytehq/airbyte/pull/10242)   | Fixed cursor for old connectors that use non-microsecond format. Now connectors work with both formats                                          |
| 0.5.5       | 2022-02-18 | [10242](https://github.com/airbytehq/airbyte/pull/10242)   | Updated timestamp transformation with microseconds                                                                                              |
| 0.5.4       | 2022-02-11 | [10251](https://github.com/airbytehq/airbyte/issues/10251) | bug Source MySQL CDC: sync failed when has Zero-date value in mandatory column                                                                  |
| 0.5.2       | 2021-12-14 | [6425](https://github.com/airbytehq/airbyte/issues/6425)   | MySQL CDC sync fails because starting binlog position not found in DB                                                                           |
| 0.5.1       | 2021-12-13 | [8582](https://github.com/airbytehq/airbyte/pull/8582)     | Update connector fields title/description                                                                                                       |
| 0.5.0       | 2021-12-11 | [7970](https://github.com/airbytehq/airbyte/pull/7970)     | Support all MySQL types                                                                                                                         |
| 0.4.13      | 2021-12-03 | [8335](https://github.com/airbytehq/airbyte/pull/8335)     | Source-MySql: do not check cdc required param binlog_row_image for standard replication                                                         |
| 0.4.12      | 2021-12-01 | [8371](https://github.com/airbytehq/airbyte/pull/8371)     | Fixed incorrect handling "\n" in ssh key                                                                                                        |
| 0.4.11      | 2021-11-19 | [8047](https://github.com/airbytehq/airbyte/pull/8047)     | Source MySQL: transform binary data base64 format                                                                                               |
| 0.4.10      | 2021-11-15 | [7820](https://github.com/airbytehq/airbyte/pull/7820)     | Added basic performance test                                                                                                                    |
| 0.4.9       | 2021-11-02 | [7559](https://github.com/airbytehq/airbyte/pull/7559)     | Correctly process large unsigned short integer values which may fall outside java's `Short` data type capability                                |
| 0.4.8       | 2021-09-16 | [6093](https://github.com/airbytehq/airbyte/pull/6093)     | Improve reliability of processing various data types like decimals, dates, datetime, binary, and text                                           |
| 0.4.7       | 2021-09-30 | [6585](https://github.com/airbytehq/airbyte/pull/6585)     | Improved SSH Tunnel key generation steps                                                                                                        |
| 0.4.6       | 2021-09-29 | [6510](https://github.com/airbytehq/airbyte/pull/6510)     | Support SSL connection                                                                                                                          |
| 0.4.5       | 2021-09-17 | [6146](https://github.com/airbytehq/airbyte/pull/6146)     | Added option to connect to DB via SSH                                                                                                           |
| 0.4.1       | 2021-07-23 | [4956](https://github.com/airbytehq/airbyte/pull/4956)     | Fix log link                                                                                                                                    |
| 0.3.7       | 2021-06-09 | [3179](https://github.com/airbytehq/airbyte/pull/3973)     | Add AIRBYTE_ENTRYPOINT for Kubernetes support                                                                                                   |
| 0.3.6       | 2021-06-09 | [3966](https://github.com/airbytehq/airbyte/pull/3966)     | Fix excessive logging for CDC method                                                                                                            |
| 0.3.5       | 2021-06-07 | [3890](https://github.com/airbytehq/airbyte/pull/3890)     | Fix CDC handle tinyint\(1\) and boolean types                                                                                                   |
| 0.3.4       | 2021-06-04 | [3846](https://github.com/airbytehq/airbyte/pull/3846)     | Fix max integer value failure                                                                                                                   |
| 0.3.3       | 2021-06-02 | [3789](https://github.com/airbytehq/airbyte/pull/3789)     | MySQL CDC poll wait 5 minutes when not received a single record                                                                                 |
| 0.3.2       | 2021-06-01 | [3757](https://github.com/airbytehq/airbyte/pull/3757)     | MySQL CDC poll 5s to 5 min                                                                                                                      |
| 0.3.1       | 2021-06-01 | [3505](https://github.com/airbytehq/airbyte/pull/3505)     | Implemented MySQL CDC                                                                                                                           |
| 0.3.0       | 2021-04-21 | [2990](https://github.com/airbytehq/airbyte/pull/2990)     | Support namespaces                                                                                                                              |
| 0.2.5       | 2021-04-15 | [2899](https://github.com/airbytehq/airbyte/pull/2899)     | Fix bug in tests                                                                                                                                |
| 0.2.4       | 2021-03-28 | [2600](https://github.com/airbytehq/airbyte/pull/2600)     | Add NCHAR and NVCHAR support to DB and cursor type casting                                                                                      |
| 0.2.3       | 2021-03-26 | [2611](https://github.com/airbytehq/airbyte/pull/2611)     | Add an optional `jdbc_url_params` in parameters                                                                                                 |
| 0.2.2       | 2021-03-26 | [2460](https://github.com/airbytehq/airbyte/pull/2460)     | Destination supports destination sync mode                                                                                                      |
| 0.2.1       | 2021-03-18 | [2488](https://github.com/airbytehq/airbyte/pull/2488)     | Sources support primary keys                                                                                                                    |
| 0.2.0       | 2021-03-09 | [2238](https://github.com/airbytehq/airbyte/pull/2238)     | Protocol allows future/unknown properties                                                                                                       |
| 0.1.10      | 2021-02-02 | [1887](https://github.com/airbytehq/airbyte/pull/1887)     | Migrate AbstractJdbcSource to use iterators                                                                                                     |
| 0.1.9       | 2021-01-25 | [1746](https://github.com/airbytehq/airbyte/pull/1746)     | Fix NPE in State Decorator                                                                                                                      |
| 0.1.8       | 2021-01-19 | [1724](https://github.com/airbytehq/airbyte/pull/1724)     | Fix JdbcSource handling of tables with same names in different schemas                                                                          |
| 0.1.7       | 2021-01-14 | [1655](https://github.com/airbytehq/airbyte/pull/1655)     | Fix JdbcSource OOM                                                                                                                              |
| 0.1.6       | 2021-01-08 | [1307](https://github.com/airbytehq/airbyte/pull/1307)     | Migrate Postgres and MySQL to use new JdbcSource                                                                                                |
| 0.1.5       | 2020-12-11 | [1267](https://github.com/airbytehq/airbyte/pull/1267)     | Support incremental sync                                                                                                                        |
| 0.1.4       | 2020-11-30 | [1046](https://github.com/airbytehq/airbyte/pull/1046)     | Add connectors using an index YAML file                                                                                                         |

</details>
