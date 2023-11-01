# Heartbeats

During a data synchronization, many things can go wrong and sometimes the fix is just to restart the synchronization.
Airbyte aims to make this restart as automated as possible and uses heartbeating mechanism in order to do that.
This performed on 2 differents component: the source and the destination. They have different logics which will be
explained bellow.

## Source

### Heartbeating logic

The platform considers both `RECORD` and `STATE` messages emitted by the source as source heartbeats.
The Airbyte platform has a process which monitors when the last beat was send and if it reaches a threshold,
the synchronization attempt will be failed. It fails with a cause being the source an message saying 
`The source is unresponsive`. Internal the error has a heartbeat timeout type, which is not display in the UI.

### Configuration

The heartbeat can be configured using the file flags.yaml through 2 entries:
* `heartbeat-max-seconds-between-messages`: this configures the maximum time allowed between 2 messages.
The default is 3 hours.
* `heartbeat.failSync`: Setting this to true will make the syncs to fail if a missed heartbeat is detected.
If false no sync will be failed because of a missed heartbeat. The default value is true.

## Destination

### Heartbeating logic

Adding a heartbeat to the destination similar to the one at the source is not straightforward since there isn't a constant stream of messages from the destination to the platform. Instead, we have implemented something that is more akin to a timeout. The platform monitors whether there has been a call to the destination that has taken more than a specified amount of time. If such a delay occurs, the platform considers the destination to have timed out.

### Configuration
The timeout can be configured using the file `flags.yaml` through 2 entries:
* `destination-timeout-max-seconds`: If the platform detects a call to the destination exceeding the duration specified in this entry, it will consider the destination to have timed out. The default timeout value is 24 hours.
* `destination-timeout.failSync`: If enabled (true by default), a detected destination timeout will cause the platform to fail the sync. If not, the platform will log a message and allow the sync to continue. When the platform fails a sync due to a destination timeout, the UI will display the message: `The destination is unresponsive`.
