import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# MongoDb Migration Guide

## Upgrading to 3.0.0

Version 3.0.0 is a rewrite of the MongoDB source on Airbyte's Bulk CDK. Change data capture now reads MongoDB change streams directly with the MongoDB driver instead of through Debezium.

In version 3.0.0, the Docker image changed from `airbyte/source-mongodb-v2` to `airbyte/source-mongodb`. If you run Self-Managed with a mirrored registry or an image allowlist, add `airbyte/source-mongodb` before upgrading.

**Most connections need no action.** Existing connections keep syncing from where they left off, with no clear or refresh: the saved change stream position, the progress of an initial snapshot and your saved settings are all read as they are. After upgrading, act if any of these apply to you:

- **Your connection syncs a view or a time series collection.** 3.0.0 no longer syncs them. MongoDB does not deliver changes to views or time series collections through the oplog, so they could never be synced incrementally; earlier versions discovered them by mistake, and only their Full Refresh syncs worked. After the upgrade, a view or time series stream still in your connection makes the sync fail ("could not be read due to catalog validation errors") until you refresh the source schema, which removes it. The data already in your destination is left in place but is no longer updated. For a view, sync the underlying collection instead.
- **Schema Enforced is on and your collections have boolean fields.** Boolean fields were declared as `string` in the schema while the records already carried JSON booleans. Refresh the source schema to retype them from `string` to `boolean`, and update downstream queries that compare them to `'true'`/`'false'`: once the column is boolean, `WHERE active = 'true'` silently matches nothing. The refresh changes the column type in typed destinations; most alter the column in place, but a destination that refuses the change (for example a table format with strict schema evolution) needs a refresh of the stream that keeps existing records, not a clear. Connections with Schema Enforced off are not affected: the document arrives as one `data` object.

  :::danger
  Do not clear an Incremental (CDC) stream to get past the retype. The new snapshot only contains the documents that exist now: the delete records (`_ab_cdc_deleted_at`) and the earlier versions of documents kept by an Append sync mode are lost for good, because MongoDB keeps no deleted documents. Take a snapshot of the destination table first if you must.
  :::

- **You had set "Capture mode" to "Post Image".** The setting is removed; update events always read the document's current state (the former "Lookup" default). Rapid successive updates to one document may now be captured as its latest state only, so some intermediate versions no longer reach a destination that keeps history.

What else changes, without any action on your part:

- **Removed settings.** "Initial Waiting Time in Seconds" and "Size of the queue" only existed for Debezium and are gone, with "Capture mode" (above). Saved values are ignored.
- **Decimals keep their full precision.** `Decimal128` values were previously converted through a double and could lose digits; they are now emitted exactly. Values in your destination may differ in the last digits after the upgrade.
- **JavaScript values with a scope keep their scope.** A `CodeWithScope` value was previously emitted with an empty `scope` object; it now carries the scope's variables.
- **`_ab_cdc_cursor` values change scale.** Earlier versions wrote a per-sync counter; 3.0.0 writes the MongoDB oplog time of the change (and, on snapshot rows, of the change stream position the sync saved). The new values are always larger than the old ones, so deduplication keeps ordering records correctly across the upgrade, and a change that is read twice now gets the same cursor both times.

### Downgrading to 2.1.1

A connection that was upgraded from 2.x can be pinned back to 2.1.1 with no clear or refresh: 3.0.0 keeps the change stream position 2.x saved before the upgrade, untouched, next to its own. After the downgrade, 2.1.1 resumes from that pre-upgrade position and replays every change made since; a deduplicated destination absorbs the replay, an Append destination receives the changes a second time. If the oplog no longer holds the pre-upgrade position, the **Invalid CDC position behavior** setting applies, as after any long pause. A connection created on 3.0.0, or reset on 3.0.0 with "Re-sync data", has no 2.x position: 2.1.1 then starts a new one at its first sync and the changes made before it are skipped. Collections whose `_id` type 2.1.1 does not support (double, decimal, date, timestamp, and types other than ObjectId, string, integer, binary and embedded document) fail on 2.1.1 as they did before the upgrade.

## Incident – March 20th, 2026

On March 20th, 2026 between 4:00 AM – 7:00 AM PT, a version change to the MongoDB source connector caused the source configuration page to be overwritten. This incident only impacted Airbyte Cloud users.

While the majority of our users were not impacted and synced as usual, if you had any jobs that ran during the incident window you may have seen the following error:

> `Checking source connection failed – please review this connection's configuration to prevent future syncs from failing.`

The issue has been identified and resolved.

**Am I affected?**

If you updated your source configuration during the incident window, you may find that your source config is now empty. In this case, simply re-enter your connection details and resume syncing as usual.

If you are using **CDC (Incremental) syncs** and your oplog position was lost during this window, you will need to [refresh your connection](https://docs.airbyte.com/platform/operator-guides/refreshes). If you needed to run a full refresh to recover your sync, please reach out to our [Support](https://support.airbyte.com).

If you have any further questions, don't hesitate to contact us.

## Upgrading to 2.0.0

This version introduces multiple database support for the MongoDB V2 source connector. Previously, the connector only accepted a single database as input, but now it can discover and sync collections from multiple databases in a single connection.

**THIS VERSION INCLUDES BREAKING CHANGES FROM PREVIOUS VERSIONS OF THE CONNECTOR!**

The changes will require you to reconfigure your existing MongoDB V2 source connectors to use the new `databases` array field instead of the previous `database` field.

### What to expect when upgrading

1. You will need to reconfigure your MongoDB source connector to use the new `databases` array field
2. If you're using CDC incremental sync mode, we recommend testing this upgrade in a staging environment first

### Migration steps

1. After upgrading, edit your MongoDB source configuration
2. Add your existing database to the new `databases` array field
3. Add any additional databases you want to sync
4. Save the configuration and run a sync

For more information, please refer to the [MongoDB v2 documentation](/integrations/sources/mongodb/).

## Upgrading to 1.0.0

This version introduces a general availability version of the MongoDB V2 source connector, which leverages
[Change Data Capture (CDC)](/platform/understanding-airbyte/cdc) to improve the performance and
reliability of syncs. This version provides better error handling, incremental delivery of data and improved
reliability of large syncs via frequent checkpointing.

MongoDB now supports incremental syncs. Alternatively you can also choose to use full refresh if your DB has lots of updates but in relatively
small volume.

**THIS VERSION INCLUDES BREAKING CHANGES FROM PREVIOUS VERSIONS OF THE CONNECTOR!**

The changes will require you to reconfigure your existing MongoDB V2 configured source connectors. To review the
breaking changes and to learn how to upgrade the connector, refer to the [MongoDB V2 source connector documentation](/integrations/sources/mongodb#changelog).
Additionally, you can manually update existing connections prior to the next scheduled sync to perform the upgrade or
re-create the source using the new configuration.

Worthy of specific mention, this version includes:

- Support for MongoDB replica sets only
- Use of Change Data Capture for incremental delivery of changes
- Frequent checkpointing of synced data
- Sampling of fields for schema discovery
- Required SSL/TLS connections

Learn more about what's new in the connector in the [MongoDB source documentation](/integrations/sources/mongodb/).

## Connector upgrade guide

<MigrationGuide />
