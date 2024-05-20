# Mongo DB Migration Guide

## Upgrading to 1.0.0

This version introduces a general availability version of the MongoDB V2 source connector, which leverages
[Change Data Capture (CDC)](/understanding-airbyte/cdc) to improve the performance and
reliability of syncs. This version provides better error handling, incremental delivery of data and improved
reliability of large syncs via frequent checkpointing.

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
