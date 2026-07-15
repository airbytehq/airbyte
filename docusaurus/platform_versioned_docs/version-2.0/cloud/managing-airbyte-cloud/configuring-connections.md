---
products: all
---

# Manage existing connections

After you set up a connection, you may need to monitor, update, or repair it. You can do this from any connections' page. Airbyte also takes you to this page after you finish configuring a connection.

The connections page has the following tabs.

- **Status**: Shows you an overview of your connector's sync health.
- **Timeline**: Track connection events. If you encounter any errors or unexpected behaviors during a sync, checking the errors and related logs is a good first step to finding the cause and solution.
- **Schema**: Modify the streams you chose during connection setup. This tab isn't available if the connection syncs to a data activation destination. In that case, use the Mappings tab to configure your schema.
- **Mappings**: Map fields between your source and your destination.
- **Transformation**: Set up custom post-sync transformations using dbt.
- **Settings**: Connection settings, and the option to delete the connection if you no longer wish to use it.

## Modify a connection

After you set up a connection, you can modify it.

1. In the left navigation, click **Connections**.

2. Find and click the connection you want to modify.

3. Configure your connection.

## Delete a connection

If you no longer need a connection, you can delete it.

:::warning
Deleting a connection is irreversible. Your source and destination connector remain, and the data remains in your destination. However, reestablishing this connection later requires a full re-sync.
:::

1. In the left navigation, click **Connections**.

2. Find and click the connection you want to modify.

3. Click **Settings**.

4. Click **Delete this connection**.

5. Type **delete** into the text box.

6. Click **Delete**.

## Other ways to manage connections

Airbyte has other options to manage connections, too.

- [Airbyte API](https://reference.airbyte.com/reference/createsource#/)
- [Terraform](/developers/terraform-documentation)

## Connection Settings

You can configure the following settings:

| Connection Setting                                                               | Description                                                                    |
| -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| Connection Name                                                                  | A custom name for your connection                                              |
| [Schedule Type](../../using-airbyte/core-concepts/sync-schedules)                   | Configure how often data syncs (can be scheduled, cron, or manually triggered)  |
| [Destination Namespace](../../using-airbyte/core-concepts/namespaces)               | Determines where the replicated data is written to in the destination          |
| [Destination Stream Prefix](../../using-airbyte/configuring-schema)                   | (Optional) Adds a prefix to each table name in the destination                  |
| [Detect and propagate schema changes](../../using-airbyte/schema-change-management) | Set how Airbyte handles schema changes in the source                           |

## Stream Settings

In addition to connection configuration settings, you apply the following specific settings per individual stream. This allows for greater flexibility in how your data syncs.

| Stream Setting                                              | Description                                                                          |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| [Stream selection](../../using-airbyte/configuring-schema)      | Determine if the stream syncs to your destination                                     |
| [Sync mode](../../using-airbyte/core-concepts/sync-modes)      | Configure how Airbyte reads data from the source and writes it                         |
| [Cursor selection](../../using-airbyte/configuring-schema)      | Select what field the stream uses to incrementally read from the source                |
| [Primary key selection](../../using-airbyte/configuring-schema) | Select what field the stream uses to determine uniqueness of a record                  |
| [Field selection](../../using-airbyte/configuring-schema)       | (Optional) Disable a partial set of fields Airbyte should not sync to the destination  |
