# Manage schema changes

Once every 24 hours, Airbyte checks for changes in your source schema and allows you to review the changes and fix breaking changes. This process helps ensure accurate and efficient data syncs, minimizing errors and saving you time and effort in managing your data pipelines.

:::note 

Schema changes are flagged in your connection but are not propagated to your destination.
    
:::

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

:::note 

Breaking changes can only occur in the **Cursor** or **Primary key** fields.
    
:::

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
