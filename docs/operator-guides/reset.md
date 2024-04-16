---
products: all
---

# Clearing your data

Clearing your data allows you to drop all previously synced data so that any ensuing sync can start syncing fresh. This is useful if you don't require the data replicated to your destination to be saved permanently or are just testing Airbyte.

Airbyte allows you to clear all streams in the connection, some, or only a single stream.

In order to backfill all historical data, a sync should be initiated after your clear succeeds.

## Clearing your data
To perform a full removal of the data for all your streams, navigate to a connection's `Settings` tab and click "Clear data". Confirm the selection to remove all previously synced data from the destination for that connection.

To clear data for a single stream, navigate to a Connection's status page, click the three grey dots next to any stream, and select "Clear data". This will clear the data for just that stream. You will then need to sync the connection again in order to reload data for that stream. 

:::note
A single stream clear will sync all enabled streams on the next sync. 
:::

You will also automatically be prompted to clear affected streams if you edit any stream settings or approve any non-breaking schema changes. To ensure data continues to sync accurately, Airbyte recommends doing a clear of those streams as your streams could sync incorrectly if a clear is not performed. 

Similarly to a sync, a clear can be completed as successful, failed, or cancelled. To resolve a failed clear, you should manually drop the tables in the destination so that Airbyte can continue syncing accurately into the destination. 

## Clear behavior
When clearing data is successfully completed, all the records are deleted from your destination tables (and files, if using local JSON or local CSV as the destination).

:::tip
If you have any orphaned tables or files that are no longer being synced to, they should be cleaned up separately, as Airbyte will not clean them up for you. This can occur when the `Destination Namespace` or `Stream Prefix` connection configuration is changed for an existing connection.
:::
