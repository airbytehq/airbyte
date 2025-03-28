---
products: all
---

# Review connection statuses

The Connections page, and each connection within, give you tools to monitor the health of your connections. If something goes wrong, you can investigate further and find the root of the problem.

## Review all connection statuses

The Connections page provides a dashboard to monitor the health of all connections in your Airbyte workspace. This is a great way to identify problems at a high level, especially when you want to review intermittent failures after a connection has become healthy again.

To access the connection dashboard:

1. Click **Connections**.

2. Optionally, filter the connections on the page and on the dashboard based on connection status, source, destination, tag, and name.

3. Click on any bar in the dashboard to open a side panel with every sync from that point in time.

4. Click on the sync you want to know more about. Airbyte goes to the Connection Timeline page and filters on that particular sync.

Here's an example of how you can put this dashboard to work.

<Arcade id="u3EEEqQoPRA4aoAAFFLO" title="Connection page dashboard" paddingBottom="calc(60% + 41px)" />

## Review one connection's status

Each connection you've set up in your Workspace has a **Status** page that displays the connection's current status, timing of the next scheduled sync, and a summary of historic sync trends. Reviewing this page allows you to monitor the health of your connection.

![Connection Status](./assets/cloud-status-page.png)

:::note
The Streams status and Records loaded graphs are only available in Airbyte Cloud and Airbyte Self-Managed Enterprise.
:::

To view the connection status:

1. In the Airbyte UI, click **Connections**.

2. Optionally, filter the connections on the page and on the dashboard based on connection status, source, destination, tag, and name.

3. Select a single connection to view more details about the connection and for a breakdown of the status of each Stream in that connection.  

    | Icon                                               | Status      | Description                                                         |
    | -------------------------------------------------- | ----------- | ------------------------------------------------------------------- |
    | ![Healthy](./assets/connection_synced.png)         | **Healthy** | The most recent sync for this connection succeeded                  |
    | ![Failed](./assets/connection_action_required.png) | **Failed**  | The most recent sync for this connection failed                     |
    | ![Running](./assets/connection_syncing.png)        | **Running** | The connection is currently actively syncing                        |
    | ![Paused](./assets/connection_disabled.png)        | **Paused**  | The connection is disabled and isn't scheduled to run automatically |

4. On the **Status** tab for a connection, there is a list of associated Streams. To the left of the name for each Stream, there is an icon that displays its status.

## Review one stream's status

The stream status allows you to monitor an individual stream's latest status. Connections often sync more than one stream. This view allows you to more easily determine if there is a problem with a given stream that could be causing problems with the connection.

| Icon                                                            | Status                   | Description                                                                                                                                        |
| --------------------------------------------------------------- | ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| ![Synced](./assets/connection_synced.png)                       | **Synced**               | The stream's last sync was successful.                                                                                                             |
| ![Syncing](./assets/connection_syncing.png)                     | **Syncing**              | The stream is currently actively syncing. Airbyte highlights the stream in grey to indicate the sync is actively extracting or loading data. |
| ![Queued](./assets/connection_not_yet_synced.png)               | **Queued**               | The stream hasn't synced yet, and is going to sync in the current ongoing sync                                                           |
| ![Queued for next sync](./assets/connection_not_yet_synced.png) | **Queued for next sync** | The stream hasn't synced yet, and is going to sync in the next scheduled sync                                                            |
| ![Error](./assets/connection_incomplete.png)                    | **Error**                | The connection didn't succeed on its most recent sync, but Airbyte expects it to recover on the next one                                                 |
| ![Action Required](./assets/connection_action_required.png)     | **Action Required**      | A breaking change related to the source or destination requires attention to resolve                                                               |

Once the sync is complete, each stream displays the time since Airbyte loaded the last record to the destination. You can click **Last record loaded** in the header to optionally display the exact datetime the last record loaded.

## Per-stream actions

In addition to the stream status, Airbyte offers stream-specific actions that allow for precise management of your data. Clicking the three grey dots next to any stream opens the available options for the stream.

- **Show in replication table** navigates you to the **Schema** tab of the connection, where Airbyte highlights the stream you selected
- **Open details** opens the field selection pane for the stream.
- [Refresh stream](/operator-guides/refreshes) re-syncs all historical data for the stream.
- [Clear data](/operator-guides/clear) removes previously synced data from your destination for the stream.

## Connection troubleshooting

The Status page offers users visibility into the recent history of your syncs. For Cloud and Enterprise users, Airbyte shows the **Streams status** and **Records loaded** for the last 8 syncs. To navigate quickly to the related sync history, hover over the graph and select the sync you're interested in viewing.

### Resolving connection errors

If the most recent sync failed, you see the error message that helps to diagnose next steps. If a sync starts to fail, Airbyte automatically disables it after multiple consecutive failures or consecutive days of failure.

#### Rate-limited syncs

If a source is being rate-limited by Airbyte trying to extract data, Airbyte displays an informational message. This can occur more frequently when Airbyte is attempting to pull a large amount of data. If available from the source, Airbyte also shows a countdown to when it intends to re-attempt syncing.

![Rate Limited Status](./assets/rate_limited.png)

Airbyte doesn't continue attempting to sync until the rate limit is over. The Active Streams section indicates which specific streams have been rate limited. Airbyte automatically starts attempting to sync again once the rate limit has lifted.

#### Configuration errors

Airbyte shows configuration errors in red. If the failure is due to a configuration error, Airbyte recommends navigating to the related source or destination to re-test and save before attempting another sync.

![Configuration Error](./assets/configuration-error.png)

#### System errors

Airbyte shows sync errors in yellow. These can range from transient errors to warnings from the source, like rate limiting. In most cases, these types of errors resolve themselves without any action required.

![Warning Error](./assets/warning-error.png)

### Major version upgrades (Cloud only)

If Airbyte releases a new major version of the connector in Cloud, you also see a banner on this page indicating the cutoff date for the version upgrade. Airbyte recommends upgrading before the cutoff date to ensure your data continues syncing. If you don't upgrade before the cutoff date, Airbyte automatically disables your connection.

Learn more about version upgrades in the [resolving breaking change documentation](/using-airbyte/schema-change-management.md#resolving-breaking-changes).
