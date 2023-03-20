# Manage syncs

After you have created a connection, you can change how your data syncs to the destination by modifying the [configuration settings](#manage-configuration) and the [stream settings](#manage-streams-in-your-connection).

## Manage configuration

The configuration settings allow you to manage aspects of the sync, such as how often the data syncs and where the data is written. 

To reconfigure these settings for your connection:

1. On the [Airbyte Cloud](http://cloud.airbyte.com) dashboard, click **Connections** and then click the connection you want to change.   

2. Click the **Replication** tab.

3. Click the **Configuration** dropdown.

You can configure the following settings:

:::note

These settings apply to all streams in the connection.

:::

| Setting                              | Description                                                                         |
|--------------------------------------|-------------------------------------------------------------------------------------|
| Replication frequency                | How often the data syncs                                                            |
| Destination namespace                | Where the replicated data is written                                                |
| Destination stream prefix            | How you identify streams from different connectors                                  |
| [Non-breaking schema updates](https://docs.airbyte.com/cloud/managing-airbyte-cloud/manage-schema-changes/#review-non-breaking-schema-changes) detected | How Airbyte handles syncs when it detects non-breaking schema changes in the source |

To use [cron scheduling](http://www.quartz-scheduler.org/documentation/quartz-2.3.0/tutorials/crontrigger.html):

1. In the **Replication Frequency** dropdown, click **Cron**. 

2. Enter a cron expression and choose a time zone to create a sync schedule.

:::note

* Only one sync per connection can run at a time. 
* If a sync is scheduled to run before the previous sync finishes, the scheduled sync will start after the completion of the previous sync.
* Airbyte Cloud does not support schedules that sync more than once per hour. 

:::

## Manage streams in your connection

In the **Activate the streams you want to sync** table, you can choose which streams to sync and how they are organized in the destination.

### Configure streams

You can reconfigure a single stream, or you can reconfigure multiple streams at once.

To configure streams:

1. On the [Airbyte Cloud](http://cloud.airbyte.com) dashboard, click **Connections** and then click the connection you want to change.   

2. Click the **Replication** tab.

3. Scroll down to the **Activate the streams you want to sync** table.

#### Configure an individual stream

![Single Edit Gif 7](https://user-images.githubusercontent.com/106352739/187313088-85c61a6d-1025-45fa-b14e-a7fe86defea4.gif)

To configure an individual stream:

1. In the the **Activate the streams you want to sync** table, toggle **Sync** on or off for your selected stream.

2. Click the **Sync mode** dropdown and select the sync mode you want to apply.

:::note 
    
Depending on the sync mode you select, you may need to choose a cursor or primary key.

:::

3. Select the **Cursor** or **Primary key** if there are dropdowns in those fields.

:::note

Source-defined cursors or primary keys are selected automatically and cannot be changed in the table.

:::

4. Click on a stream to display the stream details panel.

5. Toggle on the fields you want to include in the sync, toggle off the fields you do not want to include, or toggle all fields on or off by using the toggle in the table header.

:::note

* You can only deselect top-level fields. You cannot deselect nested fields.
* The Airbyte platform may read all data from the source (depending on the source), but it will only write data to the destination from fields you selected. Deselecting fields will not prevent the Airbyte platform from reading them.
* When you refresh the schema, new fields will be selected by default, even if you have previously deselected fields in that stream.

:::

6. Select the **Cursor** or **Primary key** if there are dropdowns in those fields.

:::note

If the cursor or primary key are source defined, you cannot change them in the stream details panel.

:::

7. Click the **X** to close the stream details panel.

8. Click **Save changes**, or click **Cancel** to discard the changes.

9. The **Stream configuration changed** dialog displays. This gives you the option to reset streams when you save the changes.

:::caution

Airbyte recommends that you reset streams. A reset will delete data in the destination of the affected streams and then re-sync that data. Skipping a reset is discouraged and might lead to unexpected behavior.

:::

10. Click **Save connection**.

#### Configure multiple streams

![Batch Edit gif 5](https://user-images.githubusercontent.com/106352739/187312110-d16b4f9a-9d43-4b23-b644-b64004f33b58.gif)

To configure multiple streams:

1. In the **Activate the streams you want to sync** table, select the checkboxes of streams that you want to apply changes to.

:::note

To select or deselect all streams, click the checkbox in the table header. You can also deselect individual streams by deselecting their checkbox in the table. 

:::

* In the highlighted footer of the table:
    
    1. Toggle **Sync** on or off.

    2. Click the **Sync mode** dropdown and select the sync mode you want to apply.

    3. Select the **Cursor** and **Primary key** if there are dropdowns in those fields.

    :::note

    Source-defined cursors or primary keys cannot be changed while configuring mutliple streams.

    :::

    4. Click Apply to apply these changes to the streams you selected, or click Cancel to discard the changes.

2. Click **Save changes**, or click **Cancel** to discard the changes.

3. The **Stream configuration changed** dialog displays. This gives you the option to reset streams when you save the changes.

:::caution

Airbyte recommends that you reset streams. A reset will delete data in the destination of the affected streams and then re-sync that data. Skipping a reset is discouraged and might lead to unexpected behavior.

:::

4. Click **Save connection**.
