# Configuring connections

A connection links a source to a destination and defines how your data will sync. After you have created a connection, you can modify any of the [configuration settings](#configure-connection-settings) or  [stream settings](#modify-streams-in-your-connection).

## Configure Connection Settings

Configuring the connection settings allows you to manage various aspects of the sync, such as how often data syncs and where data is written. 

To configure these settings:

1. On the [Airbyte Cloud](http://cloud.airbyte.com) dashboard, click **Connections** and then click the connection you want to change. 

2. Click the **Replication** tab.

3. Click the **Configuration** dropdown to expand the options.

:::note

These settings apply to all streams in the connection.

:::

You can configure the following settings:

| Setting                              | Description                                                                         |
|--------------------------------------|-------------------------------------------------------------------------------------|
| Replication frequency                | How often the data syncs                                                            |
| Destination namespace                | Where the replicated data is written                                                |
| Destination stream prefix            | How you identify streams from different connectors                                  |
| [Detect and propagate schema changes](https://docs.airbyte.com/cloud/managing-airbyte-cloud/manage-schema-changes/#review-non-breaking-schema-changes) | How Airbyte handles syncs when it detects schema changes in the source |
| Connection Data Residency | Where data will be processed |

To use [cron scheduling](http://www.quartz-scheduler.org/documentation/quartz-2.3.0/tutorials/crontrigger.html):

1. In the **Replication Frequency** dropdown, click **Cron**. 

2. Enter a cron expression and choose a time zone to create a sync schedule.

:::note

* Only one sync per connection can run at a time. 
* If a sync is scheduled to run before the previous sync finishes, the scheduled sync will start after the completion of the previous sync.
* Reach out to [Sales](https://airbyte.com/company/talk-to-sales) if you require replication more frequently than once per hour. 

:::

## Modify streams in your connection

In the **Activate the streams you want to sync** table, you choose which streams to sync and how they are loaded to the destination.

:::info
A connection's schema consists of one or many streams. Each stream is most commonly associated with a database table or an API endpoint. Within a stream, there can be one or many fields or columns.
:::

To modify streams:

1. On the [Airbyte Cloud](http://cloud.airbyte.com) dashboard, click **Connections** and then click the connection you want to change. 

2. Click the **Replication** tab.

3. Scroll down to the **Activate the streams you want to sync** table.

Modify an individual stream:

1. In the **Activate the streams you want to sync** table, toggle **Sync** on or off for your selected stream. To select or deselect all streams, click the checkbox in the table header. To deselect an individual stream, deselect its checkbox in the table.

2. Click the **Sync mode** dropdown and select the sync mode you want to apply. Depending on the sync mode you select, you may need to choose a cursor or primary key.

:::info

Source-defined cursors and primary keys are selected automatically and cannot be changed in the table.

:::

3. Click on a stream to display the stream details panel. You'll see each column we detect from the source.

4. Toggle individual fields or columns to include or exclude them in the sync, or use the toggle in the table header to select all fields at once.

:::info

* You can only deselect top-level fields. You cannot deselect nested fields.
* The Airbyte platform may read all data from the source (depending on the source), but it will only write data to the destination from fields you selected. Deselecting fields will not prevent the Airbyte platform from reading them.
* When you refresh the schema, newly added fields will be selected by default, even if you have previously deselected fields in that stream.

:::

5. Click the **X** to close the stream details panel.

6. Click **Save changes**, or click **Cancel** to discard the changes.

7. The **Stream configuration changed** dialog displays. This gives you the option to reset streams when you save the changes.

:::caution

Airbyte recommends that you reset streams. A reset will delete data in the destination of the affected streams and then re-sync that data. Skipping a reset is discouraged and might lead to unexpected behavior.

:::

8. Click **Save connection**.
