# CockroachDB

## Overview

The CockroachDB source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Resulting schema

The CockroachDb source does not alter the schema present in your database. Depending on the destination connected to this source, however, the schema may be altered. See the destination's documentation for more details.

### Data type mapping

CockroachDb data types are mapped to the following data types when synchronizing data:

| CockroachDb Type | Resulting Type | Notes |
| :--- | :--- | :--- |
| `bigint` | integer |  |
| `bit` | boolean |  |
| `boolean` | boolean |  |
| `character` | string |  |
| `character varying` | string |  |
| `date` | string |  |
| `double precision` | string |  |
| `enum` | number |  |
| `inet` | string |  |
| `int` | integer |  |
| `json` | string |  |
| `jsonb` | string |  |
| `numeric` | number |  |
| `smallint` | integer |  |
| `text` | string |  |
| `time with timezone` | string | may be written as a native date type depending on the destination |
| `time without timezone` | string | may be written as a native date type depending on the destination |
| `timestamp with timezone` | string | may be written as a native date type depending on the destination |
| `timestamp without timezone` | string | may be written as a native date type depending on the destination |
| `uuid` | string |  |

**Note:** arrays for all the above types as well as custom types are supported, although they may be de-nested depending on the destination.

### Features

| Feature | Supported | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync| Yes |  |
| Change Data Capture | No |  |
| SSL Support | Yes |  |


## Getting started

### Requirements

1. CockroachDb `v1.15.x` or above
2. Allow connections from Airbyte to your CockroachDb database \(if they exist in separate VPCs\)
3. Create a dedicated read-only Airbyte user with access to all tables needed for replication

### Setup guide

#### 1. Make sure your database is accessible from the machine running Airbyte

This is dependent on your networking setup. The easiest way to verify if Airbyte is able to connect to your CockroachDb instance is via the check connection tool in the UI.

#### 2. Create a dedicated read-only user with access to the relevant tables \(Recommended but optional\)

This step is optional but highly recommended to allow for better permission control and auditing. Alternatively, you can use Airbyte with an existing user in your database.

To create a dedicated database user, run the following commands against your database:

```sql
CREATE USER airbyte PASSWORD 'your_password_here';
```

Then give it access to the relevant schema:

```sql
GRANT USAGE ON SCHEMA <schema_name> TO airbyte
```

Note that to replicate data from multiple CockroachDb schemas, you can re-run the command above to grant access to all the relevant schemas, but you'll need to set up multiple sources connecting to the same db on multiple schemas.

Next, grant the user read-only access to the relevant tables. The simplest way is to grant read access to all tables in the schema as follows:

```sql
GRANT SELECT ON ALL TABLES IN SCHEMA <schema_name> TO airbyte;

# Allow airbyte user to see tables created in the future
ALTER DEFAULT PRIVILEGES IN SCHEMA <schema_name> GRANT SELECT ON TABLES TO airbyte;
```

#### 3. That's it!

Your database user should now be ready for use with Airbyte.

## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.1.2   | 2021-08-13 | [4699](https://github.com/airbytehq/airbyte/pull/4699) | Added json config validator |
