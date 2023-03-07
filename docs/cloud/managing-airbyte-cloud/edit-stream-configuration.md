# Edit stream configuration

By editing stream configurations, you can customize how your data syncs to the destination. This allows you to manage aspects of the sync, such as replication frequency, destination namespace, and ensuring your data is written to the correct location.

1. On the [Airbyte Cloud](http://cloud.airbyte.com) dashboard, click **Connections** and then click the connection you want to change.   

2. Click the **Replication** tab.

The **Transfer** and **Streams** settings include the following parameters:

| Parameter                            | Description                                                                         |
|--------------------------------------|-------------------------------------------------------------------------------------|
| Replication frequency                | How often the data syncs                                                            |
| [Non-breaking schema updates](https://docs.airbyte.com/cloud/managing-airbyte-cloud/manage-schema-changes/#review-non-breaking-schema-changes) detected | How Airbyte handles syncs when it detects non-breaking schema changes in the source |
| Destination Namespace                | Where the replicated data is written                                                |
| Destination Stream Prefix            | Helps you identify streams from different connectors                                |

:::note 
    
These parameters apply to all streams in the connection.

:::

If you need to use [cron scheduling](http://www.quartz-scheduler.org/documentation/quartz-2.3.0/tutorials/crontrigger.html):
1. In the **Replication Frequency** dropdown, click **Cron**. 
2. Enter a cron expression and choose a time zone to create a sync schedule.

:::note

* Only one sync per connection can run at a time. 
* If cron schedules a sync to run before the last one finishes, the scheduled sync will start after the last sync completes.
* Airbyte Cloud does not allow schedules that sync more than once per hour. 

:::

In the **Activate the streams you want to sync section**, you can make changes to any stream you choose.

To search for a stream:

1. Click the **Search stream name** search box. 

2. Type the name of the stream you want to find.

3. Streams matching your search are displayed in the list.

To change individual stream configuration:

![Single Edit Gif 7](https://user-images.githubusercontent.com/106352739/187313088-85c61a6d-1025-45fa-b14e-a7fe86defea4.gif)

1. In the **Sync** column of the stream, toggle the sync on or off. 

2. Click the dropdown arrow in the **Sync mode** column and select the sync mode you want to apply.

:::note 
    
Depending on the sync mode you select, you may need to choose a cursor or primary key.

:::

3. If there is a dropdown arrow in the **Cursor** or **Primary key** fields, click the dropdown arrow and choose the cursor or primary key. 

To change multiple stream configurations:

![Batch Edit gif 5](https://user-images.githubusercontent.com/106352739/187312110-d16b4f9a-9d43-4b23-b644-b64004f33b58.gif)

1. Click the first checkbox in the table header to select all streams in the connection.
    
2. Deselect the checkboxes of streams you do not want to apply these changes to.

3. In the highlighted header of the table, toggle the sync on or off. 

4. Click the dropdown arrow in the **Sync mode** column and select the sync mode you want to apply to these streams.

5. If there is a dropdown arrow in the **Cursor** or **Primary key** fields of the highlighted table header, click the dropdown arrow and choose the cursor or primary key.

6. Click **Apply** to apply these changes to the streams you selected, or click **Cancel** to discard the changes.

To save the changes:
1. Click **Save changes**, or click **Cancel** to discard the changes.

2. The **Stream configuration changed** dialog displays. This gives you the option to reset streams when you save the changes.

:::caution

Airbyte recommends that you reset streams. A reset will delete data in the destination of the affected streams and then re-sync that data. Skipping a reset is discouraged and might lead to unexpected behavior.

:::

3. Click **Save connection**, or click **Cancel** to close the dialog. 

To refresh the source schema:
1. Click **Refresh source schema** to fetch the schema of your data source.

2. If the schema has changed, the **Refreshed source schema** dialog displays them.
