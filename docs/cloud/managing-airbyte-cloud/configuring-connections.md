---
products: all
---

# Data Transfer Options

A connection links a source to a destination and defines how your data will sync. After you have created a connection, you can modify any of the configuration settings or stream settings.

## Configure Connection Settings

Configuring the connection settings allows you to manage various aspects of the sync, such as how often data syncs and where data is written.

To configure these settings:

1. In the Airbyte UI, click **Connections** and then click the connection you want to change.

2. Click the **Settings** tab.

3. Click the **Advanced seetings** dropdown to display all settings.

:::note

These settings apply to all streams in the connection.

:::

You can configure the following settings:

| Connection Setting                                                                                       | Description                                                            |
| --------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Connection Name                                                                               | A custom name for your connection                                      |
| [Schedule Type](/using-airbyte/core-concepts/sync-schedules.md)                               | Configure how often data syncs (can be scheduled, cron, or manually triggered) |
| [Destination Namespace](/using-airbyte/core-concepts/namespaces.md)                           | Determines where the replicated data is written to in the destination             |
| [Destination Stream Prefix](/using-airbyte/configuring-schema.md)                                                                     | (Optional) Adds a prefix to each table name in the destination                   |
| [Detect and propagate schema changes](using-airbyte/schema-change-management.md) | Set how Airbyte handles schema changes in the source                       |
| [Connection Data Residency](/cloud/managing-airbyte-cloud/manage-data-residency.md)           | Determines where data will be processed (Cloud only)                              |


## Configure Stream Settings

In addition to connection configuration settings, you apply the following specific settings per individual stream. This allows for greater flexibility in how your data syncs.

| Stream Setting | Description             |
| --------- | ----------- |
| [Stream selection](/using-airbyte/configuring-schema.md) | Determine if the stream syncs to your destination     |
| [Sync mode](/using-airbyte/core-concepts/sync-modes/README.md) | Configure how Airbyte reads data from the source and writes it     |
| [Cursor selection](/using-airbyte/configuring-schema.md) | Select what field the stream uses to incrementally read from the source     |
| [Primary key selection](/using-airbyte/configuring-schema.md) | Select what field the stream uses to determine uniqueness of a record     |
| [Field selection](/using-airbyte/configuring-schema.md) | (Optional) Disable a partial set of fields Airbyte should not sync to the destination     | 