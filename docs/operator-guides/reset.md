---
products: all
---

# Resetting your data

Resetting your data allows you to drop all previously synced data so that any ensuing sync can start syncing fresh. This is useful if you don't require the data replicated to your destination to be saved permanently or are just testing Airbyte.

Airbyte allows you to reset all streams in the connection, some, or only a single stream (when the connector support per-stream operations).

A sync will automatically start after a completed reset, which commonly backfills all historical data.

## Performing a Reset
To perform a full reset that resets all your streams, select `Reset your data` in the UI on a connection's status or job history tabs by selecting the three grey dots next to "Sync now". 

To reset a single stream, navigate to a Connection's status page, click the three grey dots next to any stream, and select "Reset this stream". This will perform a reset of only that stream. You will then need to sync the connection again in order to reload data for that stream. 

:::note
A single stream reset will sync all enabled streams on the next sync. 
:::

You will also automatically be prompted to reset affected streams if you edit any stream settings or approve any non-breaking schema changes. To ensure data continues to sync accurately, Airbyte recommends doing a reset of those streams as your streams could sync incorrectly if a reset is not performed. 

Similarly to a sync job, a reset can be completed as successful, failed, or cancelled. To resolve a failed reset, you should manually drop the tables in the destination so that Airbyte can continue syncing accurately into the destination. 

## Reset behavior
When a reset is successfully completed, all the records are deleted from your destination tables (and files, if using local JSON or local CSV as the destination), and then the next sync will begin.

:::tip
If you have any orphaned tables or files that are no longer being synced to, they should be cleaned up separately, as Airbyte will not clean them up for you. This can occur when the `Destination Namespace` or `Stream Prefix` connection configuration is changed for an existing connection.
:::
