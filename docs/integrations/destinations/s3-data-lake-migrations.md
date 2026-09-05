import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# S3 Data Lake Migration Guide

<!--
TK: the version headings below use 0.3.54 as a best guess. Update them, the `unsafeDowngrades`
entry in `metadata.yaml`, and the changelog once the real release version is settled.
-->

## Upgrading to 0.3.54

Version 0.3.54 writes the nested fields of the `_airbyte_meta` column — `sync_id`, `changes`, and the
`field`, `change`, and `reason` members of each `changes` entry — as **optional** Iceberg fields
instead of required ones.

### Why

Some external catalog consumers cannot read Iceberg tables whose nested struct fields are required.
Registering an Airbyte-written table through AWS Glue federation in BigQuery, for example, fails or
returns a table whose nested `_airbyte_meta` fields are unreadable. Iceberg treats
required → optional as a compatible evolution, so relaxing these fields makes the tables readable by
those consumers without changing any data.

### Who is affected

All users of this destination. The change applies to the `_airbyte_meta` column of every stream; no
other column's nullability changes, and no record values change.

### Upgrading

No user action is required to upgrade. Existing tables are migrated in place on the first sync after the upgrade: the connector
detects the required nested fields on the live table and relaxes them, with no table recreation, no
data rewrite, and no full refresh. Newly created tables get optional nested fields from the start.

### Downgrading

Downgrading past version 0.3.54 is unsafe. Once a table has been migrated, connector versions earlier than this release **cannot write to it**.
Older versions still declare the nested `_airbyte_meta` fields as required, and Iceberg does not
allow optional → required evolution, so the sync fails at schema evolution time with:

```
Schema evolution for column "_airbyte_meta" between
struct<sync_id: optional long, changes: optional list<...>> and
struct<sync_id: required long, changes: required list<...>> is not allowed.
```

The failure is a hard sync failure, not a degraded sync, and it affects every stream in the
connection. If you pin this destination to a specific version, do not pin it back to an earlier
version after upgrading. Recovering from a downgrade requires dropping and recreating the affected
tables, which loses their history.

## Connector upgrade guide

<MigrationGuide />
