# MongoDb Migration Guide

## Incident – March 20th, 2026

On March 20th, 2026 between 4:00 AM – 7:00 AM PT, a version change to the MongoDB source connector caused the source configuration page to be overwritten. This incident only impacted Airbyte Cloud users.

While the majority of our users were not impacted and synced as usual, if you had any jobs that ran during the incident window you may have seen the following error:

> `Checking source connection failed – please review this connection's configuration to prevent future syncs from failing.`

The issue has been identified and resolved.

**Am I affected?**

If you updated your source configuration during the incident window, you may find that your source config is now empty. In this case, simply re-enter your connection details and resume syncing as usual.

If you are using **CDC (Incremental) syncs** and your oplog position was lost during this window, you will need to [refresh your connection](https://docs.airbyte.com/platform/operator-guides/refreshes). If you needed to run a full refresh to recover your sync, please reach out to our [Support](https://support.airbyte.com).

If you have any further questions, don't hesitate to contact us.

## Upgrading to 3.0.0

Version 3.0.0 is a rewrite of the MongoDB source on Airbyte's Bulk CDK, the same foundation as the certified Postgres, MySQL and SQL Server sources. Change data capture now reads MongoDB change streams directly with the MongoDB driver instead of through Debezium.

**No reset is required.** Existing connections keep syncing from where they left off: the saved change stream position, the progress of an initial snapshot and the source configuration are all read as-is. Configurations that still contain the removed settings are accepted.

What changes for you:

- **Removed settings.** "Initial Waiting Time in Seconds" and "Size of the queue" only existed for Debezium and are gone. Saved values are ignored.
- **Views are no longer synced.** Earlier versions discovered views as streams by mistake; views cannot be read incrementally or resumed. Streams for views disappear from the catalog when you refresh the source schema. Sync the underlying collection instead.
- **Booleans are typed as `boolean`.** Boolean fields were previously declared as `string` in the schema while the records already carried true JSON booleans. Refresh the source schema to pick up the new type; the values themselves do not change.
- **Decimals keep their full precision.** `Decimal128` values were previously converted through a double and could lose digits; they are now emitted exactly. Values in your destination may differ in the last digits after the upgrade.
- **Dates are always rendered in UTC** with millisecond precision, for example `2024-01-01T00:00:00.000Z`. This matches what earlier versions produced in practice.
- **One `_id` type per collection.** All documents in a collection must use the same BSON type for `_id` (integers, longs, doubles and decimals count as one type). Earlier versions logged a warning for mixed collections and could miss documents when a sync resumed; 3.0.0 fails the sync with an error that names the types found. Fix the data or deselect the collection.
- **Sharded clusters are supported** when connected through `mongos`. A standalone server, which has no change streams, now fails the connection test with a message saying so instead of failing later.
- **Privileges are unchanged**: the `read` role on the database when you sync one database, `readAnyDatabase` when you sync several. See [Step 1 of the setup guide](/integrations/sources/mongodb-v2#step-1-create-a-dedicated-read-only-mongodb-user).

No action is required to upgrade. After upgrading, refresh the source schema once to pick up the boolean types and drop any view streams.

## Upgrading to 2.0.0

This version introduces multiple database support for the MongoDB V2 source connector. Previously, the connector only accepted a single database as input, but now it can discover and sync collections from multiple databases in a single connection.

**THIS VERSION INCLUDES BREAKING CHANGES FROM PREVIOUS VERSIONS OF THE CONNECTOR!**

The changes will require you to reconfigure your existing MongoDB V2 source connectors to use the new `databases` array field instead of the previous `database` field.

### What to expect when upgrading:

1. You will need to reconfigure your MongoDB source connector to use the new `databases` array field
2. If you're using CDC incremental sync mode, we recommend testing this upgrade in a staging environment first

### Migration steps:

1. After upgrading, edit your MongoDB source configuration
2. Add your existing database to the new `databases` array field
3. Add any additional databases you want to sync
4. Save the configuration and run a sync

For more information, please refer to the [MongoDB v2 documentation](/integrations/sources/mongodb-v2/).

## Upgrading to 1.0.0

This version introduces a general availability version of the MongoDB V2 source connector, which leverages
[Change Data Capture (CDC)](/platform/understanding-airbyte/cdc) to improve the performance and
reliability of syncs. This version provides better error handling, incremental delivery of data and improved
reliability of large syncs via frequent checkpointing.

MongoDB now supports incremental syncs. Alternatively you can also choose to use full refresh if your DB has lots of updates but in relatively 
small volume.

**THIS VERSION INCLUDES BREAKING CHANGES FROM PREVIOUS VERSIONS OF THE CONNECTOR!**

The changes will require you to reconfigure your existing MongoDB V2 configured source connectors. To review the
breaking changes and to learn how to upgrade the connector, refer to the [MongoDB V2 source connector documentation](/integrations/sources/mongodb-v2#upgrade-from-previous-version).
Additionally, you can manually update existing connections prior to the next scheduled sync to perform the upgrade or
re-create the source using the new configuration.

Worthy of specific mention, this version includes:

- Support for MongoDB replica sets only
- Use of Change Data Capture for incremental delivery of changes
- Frequent checkpointing of synced data
- Sampling of fields for schema discovery
- Required SSL/TLS connections

Learn more about what's new in the connection, view the updated documentation [here](/integrations/sources/mongodb-v2/).

