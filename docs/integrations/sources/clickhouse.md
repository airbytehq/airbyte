# ClickHouse

## Overview

The ClickHouse source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This Clickhouse source connector is built on top of the source-jdbc code base and is configured to rely on JDBC v0.3.1 standard drivers provided by ClickHouse [here](https://github.com/ClickHouse/clickhouse-jdbc) as described in ClickHouse documentation [here](https://clickhouse.tech/docs/en/interfaces/jdbc/).

#### Resulting schema

The ClickHouse source does not alter the schema present in your warehouse. Depending on the destination connected to this source, however, the schema may be altered. See the destination's documentation for more details.

### Features

| Feature | Supported | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | Yes |  |
| Replicate Incremental Deletes | Coming soon |  |
| Logical Replication \(WAL\) | Coming soon |  |
| SSL Support | No |  |
| SSH Tunnel Connection | Coming soon |  |
| Namespaces | Yes | Enabled by default |

## Getting started

### Requirements

1. ClickHouse Server `21.3.10.1` or later.
2. Create a dedicated read-only Airbyte user with access to all tables needed for replication

### Setup guide

#### 1. Make sure your database is accessible from the machine running Airbyte

This is dependent on your networking setup. The easiest way to verify if Airbyte is able to connect to your ClickHouse instance is via the check connection tool in the UI.

#### 2. Create a dedicated read-only user with access to the relevant tables \(Recommended but optional\)

This step is optional but highly recommended to allow for better permission control and auditing. Alternatively, you can use Airbyte with an existing user in your database.

To create a dedicated database user, run the following commands against your database:

```sql
CREATE USER 'airbyte'@'%' IDENTIFIED BY 'your_password_here';
```

Then give it access to the relevant schema:

```sql
GRANT SELECT ON <database name>.* TO 'airbyte'@'%';
```

You can limit this grant down to specific tables instead of the whole database. Note that to replicate data from multiple ClickHouse databases, you can re-run the command above to grant access to all the relevant schemas, but you'll need to set up multiple sources connecting to the same db on multiple schemas.

Your database user should now be ready for use with Airbyte.


## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.1.2   | 2021-08-13 | [4699](https://github.com/airbytehq/airbyte/pull/4699) | Added json config validator |