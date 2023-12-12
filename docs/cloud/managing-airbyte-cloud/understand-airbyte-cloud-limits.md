# Understand Airbyte Cloud limits

Understanding the following limitations will help you more effectively manage Airbyte Cloud.

* Max number of workspaces per user: 3*
* Max number of instances of the same source connector: 10*
* Max number of destinations in a workspace: 20*
* Max number of consecutive sync failures before a connection is paused: 100
* Max number of days with consecutive sync failures before a connection is paused: 14 days
* Max number of streams that can be returned by a source in a discover call: 1K
* Max number of streams that can be configured to sync in a single connection: 1K
* Size of a single record: 20MB
* Shortest sync schedule: Every 60 min (Reach out to [Sales](https://airbyte.com/company/talk-to-sales) if you require replication more frequently than once per hour)
* Schedule accuracy: +/- 30 min

*Limits on workspaces, sources, and destinations do not apply to customers of [Powered by Airbyte](https://airbyte.com/solutions/powered-by-airbyte). To learn more [contact us](https://airbyte.com/talk-to-sales)!
