# Heartbeats

During a data synchronization, many things can go wrong and sometimes the fix is just to restart the synchronization.
Airbyte aims to make this restart as automated as possible and uses heartbeating mechanism in order to do that.
This performed on 2 differents component: the source and the destination. They have different logics which will be
explain bellow.

## Source

### Heartbeatign logic

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