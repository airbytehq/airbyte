# Heartbeats

Many transient issues can occur when moving data. One class of issues is an unresponsive Source or Destination. In this case, the fix is often a simple restart.

Airbyte aims to make restarts as automated as possible and uses a heartbeating mechanism to do so.

Airbyte monitors for responses from the Sources and Destination, interpreting these as 'heartbeats'. If the Source or Destination does not heartbeat within
a certain time frame, Airbyte triggers a heartbeat error and automatically restarts the job.

Heartbeats are a final catch-all mechanism. Errors are expected to be transient and should automatically resolve. If they do not, it is likely a sign of a more serious issue.
In these cases, Airbyte takes the more conservative approach. Airbyte restarts the job to avoid a seemingly endless job, and highlight to users the existence of a potential issue.

## Known Heartbeat Error Causes

Possible reasons for a heartbeat error:

1. Certain API sources take an unknown amount of time to generate asynchronous responses (e.g., Salesforce, Facebook, Amplitude). No workaround currently exists.
2. Certain API sources can be rate-limited for a time period longer than their configured threshold. Although Airbyte tries its best to handle this on a per-connector basis, rate limits are not always predictable.
3. Database sources can be slow to respond to a query. This can be due to a variety of reasons, including the size of the database, the complexity of the query, and the number of other queries being made to the database at the same time.
   1. The most common reason we see is using an un-indexed column as a cursor column in an incremental sync, or a dramatically under-provisioned database.
4. Destinations can be slow to respond to write requests.
   1. The most common reason we see here is destination resource availability vis-a-vis data volumes.

In general,

- **Database Sources and Destination errors are extremely rare**. Any issues are likely to be indicative of actual issues and need to be investigated.
- **API Sources errors are uncommon but not unexpected**. This is especially true if an API source generates asynchronous responses or has rate limits.

## Airbyte Cloud

Airbyte Cloud has identical heartbeat monitoring and alerting as Airbyte Open Source.

If these issues show up on Airbyte Cloud,

1. Please read [Known Causes](#known-causes). In many cases, the issue is with the source, the destination or the connection set up, and not with Airbyte.
2. Reach out to Airbyte Support for help.

## Technical Details

### Source

#### Heartbeating logic

The platform considers both `RECORD` and `STATE` messages emitted by the source as source heartbeats.
The Airbyte platform has a process which monitors when the last beat was send and if it reaches a threshold,
the synchronization attempt will be failed. It fails with a cause being the source an message saying
`The source is unresponsive`. Internal the error has a heartbeat timeout type, which is not display in the UI.

#### Configuration

The heartbeat can be configured using the file flags.yaml through 2 entries:

- `hseartbeat-max-seconds-between-messages`: this configures the maximum time allowed between 2 messages.
  The default is 3 hours.
- `heartbeat.failSync`: Setting this to true will make the syncs to fail if a missed heartbeat is detected.
  If false no sync will be failed because of a missed heartbeat. The default value is true.

### Destination

#### Heartbeating logic

Adding a heartbeat to the destination similar to the one at the source is not straightforward since there isn't a constant stream of messages from the destination to the platform. Instead, we have implemented something that is more akin to a timeout. The platform monitors whether there has been a call to the destination that has taken more than a specified amount of time. If such a delay occurs, the platform considers the destination to have timed out.

#### Configuration

The timeout can be configured using the file `flags.yaml` through 2 entries:

- `destination-timeout-max-seconds`: If the platform detects a call to the destination exceeding the duration specified in this entry, it will consider the destination to have timed out. The default timeout value is 24 hours.
- `destination-timeout.failSync`: If enabled (true by default), a detected destination timeout will cause the platform to fail the sync. If not, the platform will log a message and allow the sync to continue. When the platform fails a sync due to a destination timeout, the UI will display the message: `The destination is unresponsive`.
