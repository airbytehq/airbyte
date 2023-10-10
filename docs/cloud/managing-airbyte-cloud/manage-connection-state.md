# Manage the connection state

The connection state provides additional information about incremental syncs. It includes the most recent values for the global or stream-level cursors, which can aid in debugging or determining which data will be included in the next sync. 

To review the connection state:
1. On the [Airbyte Cloud](http://cloud.airbyte.com) dashboard, click **Connections** and then click the connection you want to display.

2. Click the **Settings** tab on the Connection page.

3. Click the **Advanced** dropdown arrow. 

    **Connection State** displays.

To edit the connection state:

:::warning
Updates to connection state should be handled with extreme care. Updates may break your syncs, requiring a reset to fix. Make changes only as directed by the Airbyte team.
:::

1. Click anywhere in the Connection state to start editing.

2. Confirm changes by clicking "Update state". Discard any changes by clikcing "Revert changes".

3. Confirm the changes to the connection state update. 