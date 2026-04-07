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

