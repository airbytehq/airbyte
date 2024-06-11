---
products: all
---

# Review the connection status

The Status page for a connection displays information about the connection and the status of each stream being synced. Reviewing this page allows you to assess the connection's current status, understand when the next sync will be run, and observe sync trends.

![Connection Status](./assets/connection-status-page.png)

:::note
The Streams status and Records loaded graphs are available in Airbyte Cloud and Airbyte Enterprise.
:::

To view the connection status:

1. In the Airbyte UI, click **Connections**.

2. Click a connection in the list to view its status. You can also filter for a specific status to see specific connections.

| Status      | Description                                                                                         |
| ----------- | --------------------------------------------------------------------------------------------------- |
| **Healthy** | The most recent sync for this connection succeeded                                                  |
| **Failed**  | The most recent sync for this stream failed                                                         |
| **Running** | The connection is currently actively syncing                                                        |
| **Paused**  | The connection is disabled and is not scheduled to run automatically                                |

3. On the Status tab for a connection, the status is displayed as an icon to the left of the connection name. 

## Review the stream status

The stream status allows you to monitor an individual stream's latest status. Most connections will be syncing more than one stream, and this allows you to .

| Status                   | Description                                                                                         |
| ------------------------ | --------------------------------------------------------------------------------------------------- |
| **On time**              | The stream is operating within the expected timeframe expectations set by the replication frequency |
| **Syncing**              | The stream is currently actively syncing. The stream will also be highlighted in grey to indicate the sync is actively extracting or loading data.    |
| **Queued**               | The stream has not synced yet, and is scheduled to be synced in the current ongoing sync            |
| **Queued for next sync** | The stream has not synced yet, and is scheduled to be synced in the next scheduled sync             |
| **On track**             | The connection is slightly delayed but is expected to catch up before the next sync. This can occur when a transient sync error occurs.    |
| **Late**               | The connection has not loaded data within the scheduled replication frequency. For example, if the replication frequency is 1 hour, the connection has not loaded data for more than 1 hour                                     |
| **Error**              | The connection has not loaded data in more than two times the scheduled replication frequency. For example, if the replication frequency is 1 hour, the connection has not loaded data for more than 2 hours                    |
| **Action Required**    | A breaking change related to the source or destination requires attention to resolve                |
| **Pending**            | The stream has not been synced yet, so not status exists                                            |


Once the sync is complete, each stream displays the time since the last record was loaded to the destination. You can click **Last record loaded** in the header to optionally display the exact datetime the last record was loaded.

In addition to the stream status, Airbyte offers several stream-specific actions that allow for precise management of your data. Clicking the three grey dots next to any stream opens the available options for the stream.
- **Show in replication table** navigates you to the **Schema** tab of the connection, where the stream you selected is highlighted
- **Open details** opens the field selection pane for the stream
- [Refresh stream](/operator-guides/refresh) repulls all historical data for the stream
- [Clear data](/operator-guides/clear) removes previously synced data from your destination for the stream

You can also navigate directly to the stream's configuration by click the three grey dots next to any stream and selecting "Open details" to be redirected to the stream configuration.


## Resolving Connection Errors

If the most recent sync failed, you'll see the error message that will help to diagnose if the failure is due to a configuration or system error. If the failure is due to a configuration error, Airbyte recommends navigating to the related source or destination to re-test and save before attempting another sync.  If a sync starts to fail, it will automatically be disabled after multiple consecutive failures or several consecutive days of failure.

If a new major version of the connector has been released in Cloud, you will also see a banner on this page indicating the cutoff date for the version. Airbyte recommends upgrading before the cutoff date to ensure your data continues syncing. If you do not upgrade before the cutoff date, Airbyte will automatically disable your connection.

Learn more about version upgrades in our [resolving breaking change documentation](/using-airbyte/schema-change-management.md#resolving-breaking-changes).