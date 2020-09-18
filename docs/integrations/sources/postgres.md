# Postgres

## Overview

The Postgres source supports Full Refresh syncs. That is, every time a sync is run, Dataline will copy all rows in the tables and columns you setup for replication into the destination in a new table.

This Postgres source is based on the [Singer Postgres Tap](https://github.com/singer-io/tap-postgres).

### Sync Overview

#### Resulting Schema

The Postgres source does not alter the schema present in your database. Depending on the destination connected to this source, however, the schema may be altered. See the destination's documentation for more details.

#### Data type mapping

Postgres data types are mapped to the following data types when synchronizing data:

| Postgres Type | Resulting Type | Notes |
| :--- | :--- | :--- |
| `bigint` | integer |  |
| `bit` | boolean |  |
| `boolean` | boolean |  |
| `character` | string |  |
| `character varying` | string |  |
| `cidr` | string |  |
| `citext` | string |  |
| `date` | string |  |
| `double precision` | string |  |
| `enum` | number |  |
| `hstore` | object | may be de-nested depending on the destination you are syncing into |
| `inet` | string |  |
| `int` | integer |  |
| `json` | string |  |
| `jsonb` | string |  |
| `macaddr` | string |  |
| `money` | string |  |
| `numeric` | number |  |
| `real` | number |  |
| `smallint` | integer |  |
| `text` | string |  |
| `time with timezone` | string | may be written as a native date type depending on the destination |
| `time without timezone` | string | may be written as a native date type depending on the destination |
| `timestamp with timezone` | string | may be written as a native date type depending on the destination |
| `timestamp without timezone` | string | may be written as a native date type depending on the destination |
| `uuid` | string |  |

**Note:** arrays for all the above types as well as custom types are supported, although they may be de-nested depending on the destination. Byte arrays are currently unsupported.

### Features

| Feature | Supported |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | No |
| Replicate Deletes | No |
| Logical Replication \(WAL\) | No |
| SSL Support | Yes |
| SSH Tunnel Connection | No |

#### Incremental Sync

Incremental sync \(copying only the data that has changed\) for this source is coming soon.

## Getting Started

### Requirements:

1. Postgres `v9.3.x` or above
2. Allow connections from Dataline to your Postgres database \(if they exist in separate VPCs\)
3. Create a dedicated read-only Dataline user with access to all tables needed for replication

### Setup Guide

### 1. Make sure your database is accessible from the machine running Dataline

This is dependent on your networking setup. The easiest way to verify if Dataline is able to connect to your Postgres instance is via the check connection tool in the UI.

### 2. Create a dedicated read-only user with access to the relevant tables \(Recommended but optional\)

This step is optional but highly recommended to allow for better permission control and auditing. Alternatively, you can use Dataline with an existing user in your database.

To create a dedicated database user, run the following commands against your database:

```sql
CREATE USER dataline PASSWORD 'your_password_here';
```

Then give it access to the relevant schema:

```sql
GRANT USAGE ON SCHEMA <schema_name> TO dataline
```

Note that to replicate data from multiple Postgres schemas, you can re-run the command above to grant access to all the relevant schemas, but you'll need to setup multiple sources connecting to the same db on multiple schemas.

Next, grant the user read-only access to the relevant tables. The simplest way is to grant read access to all tables in the schema as follows:

```sql
GRANT SELECT ON ALL TABLES IN SCHEMA <schema_name> TO dataline;

# Allow dataline user to see tables created in the future
ALTER DEFAULT PRIVILEGES IN SCHEMA <schema_name> GRANT SELECT ON TABLES TO dataline;
```

Your database user should now be ready for use with Dataline.

