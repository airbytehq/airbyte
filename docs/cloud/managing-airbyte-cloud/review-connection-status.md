# Review the connection status:
The connection status displays information about the connection and of each stream being synced. Reviewing this summary allows you to assess the connection's current status.
 
To review the connection status:
1. On the [Airbyte Cloud](http://cloud.airbyte.com/) dashboard, click **Connections**.   

2. Click a connection in the list to view its status.

    The status for a connection is one of the following: 

    - **On time**: The connection is operating within the expected timeframe expectations set by the replication frequency
    - **On track**: The connection is slightly delayed but is expected to catch up before the next sync. 
    - **Delayed**:  The connection has not loaded data within the scheduled replication frequency. For example, if the replication frequency is 1 hour, the connection has not loaded data for more than 1 hour
    - **Error**: The connection has not loaded data in more than two times the scheduled replication frequency. For example, if the replication frequency is 1 hour, the connection has not loaded data for more than 2 hours
    - **Action Required**: A breaking change related to the source or destination requires attention to resolve
    - **Pending**: The connection has not been run yet, so no status exists
    - **Disabled**: The connection has been disabled and is not scheduled to run
    - **In Progress**: the connection is currently extracting or loading data

3. To trigger a sync of all streams, click "Sync now"

4. To trigger a reset of all streams, click "Reset your data"
 
## Review the stream status
The stream status allows you to monitor each stream's latest status. The stream will be highlighted with a grey pending bar to indicate the sync is actively extracting or loading data.

1. The status for a stream is one of the following:

    - **On time**: The stream is operating within the expected timeframe expectations set by the replication frequency
    - **Error**: The most recent sync for this stream failed
    - **Pending**: The stream has not been synced yet, so not status exists

2. Each stream shows the last record loaded to the destination. Toggle the header to display the exact datetime the last record was loaded.

3. To reset a single stream, click the three grey dots next to any stream. Select "Reset this stream" to drop the entire stream. It is recommended to start a new sync after a reset.

4. To see the stream in the connection configuration, click the three grey dots next to any stream. Select "Show in replication table" to redirect to the specific stream in the connection configuration.

5. To see the details of the stream (primary key, cursor field, columns selected), click the three grey dots next to any stream. Select "Open details" to redirect to the stream configuration