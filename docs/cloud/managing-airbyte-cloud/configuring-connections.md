---
products: all
---

# Configuring Connections

A connection links a source to a destination and defines how your data will sync. After you have created a connection, you can modify any of the configuration settings or stream settings.

## Configure Connection Settings

Configuring the connection settings allows you to manage various aspects of the sync, such as how often data syncs and where data is written.

To configure these settings:

1. In the Airbyte UI, click **Connections** and then click the connection you want to change.

2. Click the **Settings** tab.

3. Click the **Configuration** dropdown to expand the options.

:::note

These settings apply to all streams in the connection.

:::

You can configure the following settings:

| Setting                                                                                       | Description                                                            |
| --------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Connection Name                                                                               | A custom name for your connection                                      |
| [Schedule Type](/using-airbyte/core-concepts/sync-schedules.md)                               | How often data syncs (can be scheduled, cron, API-triggered or manual) |
| [Destination Namespace](/using-airbyte/core-concepts/namespaces.md)                           | Where the replicated data is written to in the destination             |
| Destination Stream Prefix                                                                     | A prefix added to each table name in the destination                   |
| [Detect and propagate schema changes](using-airbyte/schema-change-management.md) | How Airbyte handles schema changes in the source                       |
| [Connection Data Residency](/cloud/managing-airbyte-cloud/manage-data-residency.md)           | Where data will be processed (Cloud only)                              |

## Modify Streams

On the "Schema" tab, you choose which streams to sync and how they are loaded to the destination.

:::info
A connection's schema consists of one or many streams. Each stream is most commonly associated with a database table or an API endpoint. Within a stream, there can be one or many fields or columns.
:::

To modify streams, click **Connections** and then click the connection you want to change. Click the **Schema** tab to see all the streams Airbyte can sync. To modify an individual stream:

1. Toggle **Sync** on or off for your selected stream. To select or deselect all streams at once, use "Hide disabled streams" in the table header. To deselect an individual stream, use the toggle in its row.

2. Click the **Sync mode** dropdown and select the sync mode you want to apply. Depending on the sync mode you select, you may need to choose a cursor or primary key.

:::info

Source-defined cursors and primary keys are selected automatically and cannot be changed in the table.

:::

3. Click on a stream to display the stream details panel. You'll see each column we detect from the source.

4. Column selection is available to protect PII or sensitive data from being synced to the destination. Toggle individual fields to include or exclude them in the sync, or use the toggle in the table header to select all fields at once.

:::info

- You can only deselect top-level fields. You cannot deselect nested fields.
- The Airbyte platform may read all data from the source (depending on the source), but it will only write data to the destination from fields you selected. Deselecting fields will not prevent the Airbyte platform from reading them.
- When you refresh the schema, newly added fields will be selected by default, even if you have previously deselected fields in that stream.

:::

5. Click the **X** to close the stream details panel.

6. Click **Save changes**, or click **Cancel** to discard the changes.

7. The **Stream configuration changed** dialog displays. This gives you the option to reset streams when you save the changes.

:::tip

When editing the stream configuration, Airbyte recommends that you reset streams. A reset will delete data in the destination of the affected streams and then re-sync that data. Skipping a reset is discouraged and might lead to unexpected behavior.

:::

8. Click **Save connection**.
