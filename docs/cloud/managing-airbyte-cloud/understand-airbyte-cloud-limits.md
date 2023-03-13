# Understand Airbyte Cloud limits

Understanding the following limitations will help you more effectively manage Airbyte Cloud:

* Max number of workspaces per user: 100
* Max number of sources in a workspace: 100
* Max number of destinations in a workspace: 100
* Max number of connections in a workspace: 100
* Max number of consecutive sync failures before a connection is paused: 100
* Max number of days with consecutive sync failures before a connection is paused: 14 days
* Max number of streams that can be returned by a source in a discover call: 1K
* Max number of streams that can be configured to sync in a single connection: 1K
* Size of a single record: 100MB
* Shortest sync schedule: Every 60 min
* Schedule accuracy: +/- 30 min
