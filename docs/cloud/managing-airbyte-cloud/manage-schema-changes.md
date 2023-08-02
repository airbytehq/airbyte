# Manage schema changes

You can specify for each connection how Airbyte should handle any change of schema in the source. This process helps ensure accurate and efficient data syncs, minimizing errors and saving you time and effort in managing your data pipelines.

Airbyte checks for any changes in your source schema before syncing, at most once every 24 hours.

Based on your configured settings for "Detect and propagate schema changes", Airbyte can automatically sync those changes or ignore them: 
* **Propagate all changes** automatically propagates stream changes (additions or deletions) or column changes (additions or deletions) detected in the source
* **Propagate column changes only** automatically propagates column changes detected in the source
* **Ignore** any schema change, in which case the schema you’ve set up will not change even if the source schema changes until you approve the changes manually
* **Pause connection** disables the connection from syncing further once a change is detected

When a new column is detected and propagated, values for that column will be filled in for the updated rows. If you are missing values for rows not updated, a backfill can be done by completing a full refresh.

When a column is deleted, the values for that column will stop updating for the updated rows and be filled with Null values.

When a new stream is detected and propagated, the first sync will fill all data in as if it is a historical sync. When a stream is deleted from the source, the stream will stop updating, and we leave any existing data in the destination. The rest of the enabled streams will continue syncing.

In all cases, if a breaking change is detected, the connection will be paused for manual review to prevent future syncs from failing. Breaking schema changes occur when:
* An existing primary key is removed from the source
* An existing cursor is removed from the source

See "Fix breaking schema changes" to understand how to resolve these types of changes.

## Review non-breaking schema changes

To review non-breaking schema changes:
1. On the [Airbyte Cloud](http://cloud.airbyte.com/) dashboard, click **Connections** and select the connection with non-breaking changes (indicated by a **yellow exclamation mark** icon).

2. Click **Review changes**.

3. The **Refreshed source schema** dialog displays the changes. 

4. Review the changes and click **OK** to close the dialog.

5. Scroll to the bottom of the page and click **Save changes**.

:::note 
    
 By default, Airbyte ignores non-breaking changes and continues syncing. You can configure how Airbyte handles syncs when it detects non-breaking changes by [editing the stream configuration](https://docs.airbyte.com/cloud/managing-airbyte-cloud/edit-stream-configuration).
    
:::

## Fix breaking schema changes

Breaking schema changes occur when:
* An existing primary key is removed from the source
* An existing cursor is removed from the source

To review and fix breaking schema changes:
1. On the [Airbyte Cloud](http://cloud.airbyte.com/) dashboard, click **Connections** and select the connection with breaking changes (indicated by a **red exclamation mark** icon).

2. Click **Review changes**.

3. The **Refreshed source schema** dialog displays the changes.

4. Review the changes and click **OK** to close the dialog.

5. In the streams table, the stream with a breaking change is highlighted.

6. Fix the breaking change by selecting a new **Cursor** or **Primary key**.

7. Scroll to the bottom of the page and click **Save changes**.

:::note 
    
If a connection’s source schema has breaking changes, it will stop syncing. You must review and fix the changes before editing the connection or resuming syncs.
    
:::

### Manually refresh the source schema

In addition to Airbyte Cloud’s automatic schema change detection, you can manually refresh the source schema to stay up to date with changes in your schema. 

 To manually refresh the source schema:

 1. On the [Airbyte Cloud](http://cloud.airbyte.com) dashboard, click **Connections** and then click the connection you want to refresh.

 2. Click the **Replication** tab.

 3. In the **Activate the streams you want to sync** table, click **Refresh source schema** to fetch the schema of your data source.

 4. If there are changes to the schema, you can review them in the **Refreshed source schema** dialog.

## Manage Schema Change Notifications
[Refer to our notification documentation](https://docs.airbyte.com/cloud/managing-airbyte-cloud/manage-airbyte-cloud-notifications#enable-schema-update-notifications) to understand how to stay updated on any schema updates to your connections.