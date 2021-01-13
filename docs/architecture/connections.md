# Connections

A connection is a configuration for syncing data between a source and a destination. To setup a connection, a user must configure things such such as:

* A catalog selection: which [streams and fields](catalog.md) to replicate from the source
* Sync mode: Whether streams should be replicated using [Full Refresh](full-refresh.md) or [Incremental](incremental.md) syncs
* Sync schedule: when to trigger a sync of the data

For information about catalog selections and sync modes, see [AirbyteCatalog & ConfiguredAirbyteCatalog](catalog.md) and [Full Refresh](full-refresh.md) and [Incremental](incremental.md). Sync schedules are explained below.

## Sync schedules

Syncs will be triggered by either:

* A manual request \(i.e: clicking the "Sync Now" button in the UI\)
* A schedule

When a scheduled connection is first created, a sync is executed as soon as possible. After that, a sync is run once the time since the last sync \(whether it was triggered manually or due to a schedule\) has exceeded the schedule interval. For example, consider the following illustrative scenario:

* **October 1st, 2pm**, a user sets up a connection to sync data every 24 hours. 
* **October 1st, 2:01pm**: sync job runs 
* **October 2nd, 2:01pm:** 24 hours have passed since the last sync, so a sync is triggered. 
* **October 2nd, 5pm**: The user manually triggers a sync from the UI
* **October 3rd, 2:01pm:** since the last sync was less than 24 hours ago, no sync is run
* **October 3rd, 5:01pm:** It has been more than 24 hours since the last sync, so a sync is run

