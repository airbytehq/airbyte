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

| Connection Setting                                                                        | Description                                                                    |
| ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| Connection Name                                                                           | A custom name for your connection                                              |
| [Schedule Type](/platform/using-airbyte/core-concepts/sync-schedules)                     | Configure how often data syncs (can be scheduled, cron, or manually triggered) |
| [Destination Namespace](/platform/using-airbyte/core-concepts/namespaces)                 | Determines where the replicated data is written to in the destination          |
| [Destination Stream Prefix](/platform/using-airbyte/configuring-schema)                   | (Optional) Adds a prefix to each table name in the destination                 |
| [Detect and propagate schema changes](/platform/using-airbyte/schema-change-management)   | Set how Airbyte handles schema changes in the source                           |
| [Connection Data Residency](/platform/cloud/managing-airbyte-cloud/manage-data-residency) | Determines where data will be processed (Cloud only)                           |

## Configure Stream Settings

In addition to connection configuration settings, you apply the following specific settings per individual stream. This allows for greater flexibility in how your data syncs.

| Stream Setting                                                      | Description                                                                           |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| [Stream selection](/platform/using-airbyte/configuring-schema)      | Determine if the stream syncs to your destination                                     |
| [Sync mode](/platform/using-airbyte/core-concepts/sync-modes)       | Configure how Airbyte reads data from the source and writes it                        |
| [Cursor selection](/platform/using-airbyte/configuring-schema)      | Select what field the stream uses to incrementally read from the source               |
| [Primary key selection](/platform/using-airbyte/configuring-schema) | Select what field the stream uses to determine uniqueness of a record                 |
| [Field selection](/platform/using-airbyte/configuring-schema)       | (Optional) Disable a partial set of fields Airbyte should not sync to the destination |
