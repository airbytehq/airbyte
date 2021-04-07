# Postgres

## Overview

The Postgres source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This Postgres source is based on the [Singer Postgres Tap](https://github.com/singer-io/tap-postgres).

### Resulting schema

The Postgres source does not alter the schema present in your database. Depending on the destination connected to this source, however, the schema may be altered. See the destination's documentation for more details.

### Data type mapping

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
| Incremental - Append Sync | Yes |
| Replicate Incremental Deletes | Yes |
| Logical Replication \(WAL\) | Yes |
| SSL Support | Yes |
| SSH Tunnel Connection | Coming soon |

## Getting started

### Requirements

1. Postgres `v9.3.x` or above
2. Allow connections from Airbyte to your Postgres database \(if they exist in separate VPCs\)
3. Create a dedicated read-only Airbyte user with access to all tables needed for replication

### Setup guide

#### 1. Make sure your database is accessible from the machine running Airbyte

This is dependent on your networking setup. The easiest way to verify if Airbyte is able to connect to your Postgres instance is via the check connection tool in the UI.

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

Note that to replicate data from multiple Postgres schemas, you can re-run the command above to grant access to all the relevant schemas, but you'll need to set up multiple sources connecting to the same db on multiple schemas.

Next, grant the user read-only access to the relevant tables. The simplest way is to grant read access to all tables in the schema as follows:

```sql
GRANT SELECT ON ALL TABLES IN SCHEMA <schema_name> TO airbyte;

# Allow airbyte user to see tables created in the future
ALTER DEFAULT PRIVILEGES IN SCHEMA <schema_name> GRANT SELECT ON TABLES TO airbyte;
```

#### 3. Set up CDC \(Optional\)

Please read [the section on CDC below](#setting-up-cdc-for-postgres) for more information.

#### 4. That's it!

Your database user should now be ready for use with Airbyte.

## Change Data Capture (CDC) / Logical Replication / WAL Replication
We use [logical replication](https://www.postgresql.org/docs/10/logical-replication.html) of the Postgres write-ahead log (WAL) to incrementally capture deletes using the `pgoutput` plugin. 

We do not require installing custom plugins like `wal2json` or `test_decoding`. We use `pgoutput`, which is included in Postgres 10+ by default.

Please read the [CDC docs](../../architecture/cdc.md) for an overview of how Airbyte approaches CDC.

### Should I use CDC for Postgres?
* If you need a record of deletions and can accept the limitations posted below, you should to use CDC for Postgres.
* If your data set is small and you just want snapshot of your table in the destination, consider using Full Refresh replication for your table instead of CDC.
* If the limitations prevent you from using CDC and your goal is to maintain a snapshot of your table in the destination, consider using non-CDC incremental and occasionally reset the data and re-sync.

### CDC Limitations
* Make sure to read our [CDC docs](../../architecture/cdc.md) to see limitations that impact all databases using CDC replication.
* CDC is only available for Postgres 10+.
* Airbyte requires a replication slot configured only for its use. Only one source should be configured that uses this replication slot. Instructions on how to set up a replication slot can be found below.
* Log-based replication only works for master instances of Postgres.
* Using logical replication increases disk space used on the database server. The additional data is stored until it is consumed.

### Setting up CDC for Postgres

Follow one of these guides to enable logical replication:
* [Bare Metal, VMs (EC2/GCE/etc), Docker, etc.](#setting-up-cdc-on-bare-metal-vms-ec2gceetc-docker-etc)
* [AWS Postgres RDS or Aurora](#setting-up-cdc-on-aws-postgres-rds-or-aurora)
* [Azure Database for Postgres](#setting-up-cdc-on-azure-database-for-postgres)

Then, the Airbyte user for your instance needs to be granted `REPLICATION` and `LOGIN` permissions. Since we are using embedded Debezium under the hood for Postgres, we recommend reading the [permissioning section of the Debezium docs](https://debezium.io/documentation/reference/connectors/postgresql.html#postgresql-permissions) for more information on what is required.

Finally, you will need to create a replication slot. Here is the query used to create a replication slot called `airbyte_slot`: 
```
SELECT pg_create_logical_replication_slot('airbyte_slot', 'pgoutput');`
```

This slot **must** use `pgoutput`.

After providing the name of this slot when configuring the source, you should be ready to sync data with CDC!

### Setting up CDC on Bare Metal, VMs (EC2/GCE/etc), Docker, etc.
Three settings must be configured in the `postgresql.conf` file for your database:
```
wal_level = logical             
max_wal_senders = 1             
max_replication_slots = 1
```

* `wal_level` is the type of coding used within the Postgres write-ahead log. This must be set to `logical` for Airbyte CDC.
* `max_wal_senders` is the maximum number of processes used for handling WAL changes. This must be at least one.
* `max_replication_slots` is the maximum number of replication slots that are allowed to stream WAL changes. This must one if Airbyte will be the only service reading subscribing to WAL changes or more if other services are also reading from the WAL.

After setting these values you will need to restart your instance.

Finally, [follow the rest of steps above](#setting-up-cdc-for-postgres).

### Setting up CDC on AWS Postgres RDS or Aurora
* Go to the `Configuration` tab for your DB cluster. 
* Find your cluster parameter group. You will either edit the parameters for this group or create a copy of this parameter group to edit. If you create a copy you will need to change your cluster's parameter group before restarting. 
* Within the parameter group page, search for `rds.logical_replication`. Select this row and click on the `Edit parameters` button. Set this value to `1`.
* Wait for a maintenance window to automatically restart the instance or restart it manually.
* Finally, [follow the rest of steps above](#setting-up-cdc-for-postgres).

### Setting up CDC on Azure Database for Postgres
Use either the Azure CLI to:
```
az postgres server configuration set --resource-group group --server-name server --name azure.replication_support --value logical
az postgres server restart --resource-group group --name server
```

Finally, [follow the rest of steps above](#setting-up-cdc-for-postgres).

### Setting up CDC on Google CloudSQL

Unfortunately, logical replication is not configurable for Google CloudSQL. You can indicate your support for this feature on the [Google Issue Tracker](https://issuetracker.google.com/issues/120274585).

### Setting up CDC on other platforms
If you encounter one of those not listed below, please consider [contributing to our docs](https://github.com/airbytehq/airbyte/tree/master/docs) and providing setup instructions.
