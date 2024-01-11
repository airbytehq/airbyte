---
products: all
---

# Sync Schedules

For each connection, you can select between three options that allow a sync to run. The three options for `Replication Frequency` are:

- Scheduled (e.g. every 24 hours, every 2 hours)
- Cron scheduling
- Manual

## Sync Limitations

* Only one sync per connection can run at a time. 
* If a sync is scheduled to run before the previous sync finishes, the scheduled sync will start after the completion of the previous sync.
* Syncs can run at most every 60 minutes. Reach out to [Sales](https://airbyte.com/company/talk-to-sales) if you require replication more frequently than once per hour. 

## Scheduled syncs
When a scheduled connection is first created, a sync is executed immediately after creation. After that, a sync is run once the time since the last sync \(whether it was triggered manually or due to a schedule\) has exceeded the schedule interval. For example:

- **October 1st, 2pm**, a user sets up a connection to sync data every 24 hours.
- **October 1st, 2:01pm**: sync job runs
- **October 2nd, 2:01pm:** 24 hours have passed since the last sync, so a sync is triggered.
- **October 2nd, 5pm**: The user manually triggers a sync from the UI
- **October 3rd, 2:01pm:** since the last sync was less than 24 hours ago, no sync is run
- **October 3rd, 5:01pm:** It has been more than 24 hours since the last sync, so a sync is run

## Cron Scheduling
If you prefer more flexibility in scheduling your sync, you can also use CRON scheduling to set a precise time of day or month.

Airbyte uses the CRON scheduler from [Quartz](http://www.quartz-scheduler.org/documentation/quartz-2.3.0/tutorials/crontrigger.html). We recommend reading their [documentation](http://www.quartz-scheduler.org/documentation/quartz-2.3.0/tutorials/crontrigger.html) to learn more about how to 

When setting up the cron extpression, you will also be asked to choose a time zone the sync will run in.

:::note
For Scheduled or cron scheduled syncs, Airbyte guarantees syncs will initiate with a schedule accuracy of +/- 30 minutes.
:::

## Manual Syncs
When the connection is set to replicate with `Manual` frequency, the sync will not automatically run. 

It can be triggered by clicking the "Sync Now" button at any time through the UI or be triggered through the UI.