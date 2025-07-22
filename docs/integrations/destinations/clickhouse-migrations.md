# Clickhouse Migration Guide

## SSH Support :warning:

SSH is implementation for the new connector is in Beta. If you upgrade and SSH
does not work for you, please reach out to support.

## Upgrading to 2.0.0

This version differs from 1.0.0 radically. Whereas 1.0.0 wrote all your data
as JSON to raw tables in airbyte_internal database, 2.0.0 will properly separate
your schema into typed columns and write to the specified database in the
configuration and the un-prefixed table name. You will no longer see
`airbyte_internal.{database}_raw__stream_{table}` and will instead see
`{database}.{table}`.

While is treated as a "breaking change", connections should continue to function
with no changes, albeit writing data to a completely different location and in a
different form. So any downstream pipelines will need updating to ingest the new
data location / format.

## Migrating existing data to the new format

Unfortunately Airbyte has no way to migrate the existing raw tables to the new
typed format. The only "out of the box" way to get your data into the new format
is to re-sync it from scratch.

## Removing the old tables

Because the new destination has no knowledge of the old destination's table
naming semantics, we will not remove existing data. If you would like to, you
will need to delete all the tables saved in the old format, which for most
people should be under `airbyte_internal.{database}_raw__`, but may vary based
on your specific configuration.

## Gotchas

### Namespaces and the default database

In V2 namespaces are treated as equivalent to a ClickHouse "database". This
means if you set a custom namespace for your connection that will be the
database the connector will use for queries instead of the "database"
configured in the Destination settings.

Previously, namespaces where added as a prefix to the table name. If you have
existing connections configured in this fashion you may want to remove them.

### Hostname

If the "Hostname" property in your configuration contains the protocol ("http
or "https"), you will need to remove it.

The previous versions incidentally tolerated the protocol being stored in the
hostname field.