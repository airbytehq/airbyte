# S3 Data Lake Migration Guide

## Upgrading to 0.4.3

Version 0.4.3 writes the `sync_id` and `changes` fields of the `_airbyte_meta` column as **optional** Iceberg fields instead of required ones. Earlier versions already wrote the fields nested inside each `changes` entry as optional.

### Why

Some warehouses can't read Iceberg tables whose nested struct fields are required. Snowflake, BigQuery and Databricks reject or fail to query Airbyte-written tables while `_airbyte_meta.sync_id` and `_airbyte_meta.changes` are required. Iceberg treats required → optional as a compatible schema change, so relaxing these fields makes the tables readable without changing any data.

### Who is affected

All users of this destination. The change applies to the `_airbyte_meta` column of every stream. No other column's nullability changes, and no record values change.

### Upgrading

No user action is required to upgrade. The first sync of each stream after the upgrade relaxes the nested `_airbyte_meta` fields on the existing table in place, with no table recreation, data rewrite or refresh. New tables get optional fields from the start.

### Downgrading

Downgrading below version 0.4.3 is unsafe. Once a stream has synced on 0.4.3 or later, earlier connector versions **can't write to its table**. Earlier versions still declare the nested `_airbyte_meta` fields as required, and Iceberg doesn't allow optional → required changes, so the sync fails with an error like:

```text
Schema evolution for column "_airbyte_meta" between
struct<sync_id: optional long, changes: optional list<...>> and
struct<sync_id: required long, changes: required list<...>> is not allowed
```

This is a hard sync failure on every stream whose table was relaxed. Don't pin this destination back to a version below 0.4.3 after upgrading. If a connection was already downgraded, upgrade it to 0.4.3 or later again to restore syncs.
