# MongoDb Migration Guide

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

