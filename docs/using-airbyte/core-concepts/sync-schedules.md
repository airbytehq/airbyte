---
products: all
---

# Sync Schedules

For each connection, you can select between three options that allow a sync to run. The three options for `Schedule Type` are:

| Schedule Setting | Definition |
|--|--| 
| Scheduled | Runs the syncs at the specified time interval (e.g. every 24 hours, every 2 hours) | 
| Cron | Runs the syncs based on the user-defined cron expression | 
| Manual | You are required to run the syncs manually | 

## Scheduled syncs

You can choose between the following scheduled options:

- Every 24 hours (most common)
- Every 12 hours
- Every 8 hours
- Every 6 hours
- Every 3 hours
- Every 2 hours
- Every 1 hour

When a scheduled connection is first created, a sync is executed immediately after creation. After that, a sync is run once the time since the last sync \(whether it was triggered manually or due to a schedule\) has exceeded the schedule interval. For example:

- **October 1st, 2pm**, a user sets up a connection to sync data every 24 hours.
- **October 1st, 2:01pm**: sync job runs
- **October 2nd, 2:01pm:** 24 hours have passed since the last sync, so a sync is triggered.
- **October 2nd, 5pm**: The user manually triggers a sync from the UI
- **October 3rd, 2:01pm:** since the last sync was less than 24 hours ago, no sync is run
- **October 3rd, 5:01pm:** It has been more than 24 hours since the last sync, so a sync is run

## Cron Syncs

If you prefer more precision in scheduling your sync, you can also use CRON scheduling to set a specific time of day or month.

Airbyte uses the CRON scheduler from [Quartz](http://www.quartz-scheduler.org/documentation/quartz-2.3.0/tutorials/crontrigger.html). We recommend reading their [documentation](http://www.quartz-scheduler.org/documentation/quartz-2.3.0/tutorials/crontrigger.html) to understand the required formatting. You can also refer to these examples:

| Cron string          | Sync Timing                                            |
| -------------------- | ------------------------------------------------------ |
| 0 0 \* \* \* ?       | Every hour, at 0 minutes past the hour                 |
| 0 0 15 \* \* ?       | At 15:00 every day                                     |
| 0 0 15 \* \* MON,TUE | At 15:00, only on Monday and Tuesday                   |
| 0 0 0,2,4,6 \* \* ?  | At 12:00 AM, 02:00 AM, 04:00 AM and 06:00 AM every day |
| 0 0 _/15 _ \* ?      | At 0 minutes past the hour, every 15 hours             |

When setting up the cron expression, you will also be asked to choose a time zone the sync will run in.

## Manual Syncs

When the connection is set to replicate with `Manual` frequency, the sync will not automatically run.

It can be triggered by clicking the "Sync Now" button at any time through the UI or be triggered through the API.


## Sync Considerations

- Only one sync per connection can run at a time.
- If a sync is scheduled to run before the previous sync finishes, the scheduled sync will start after the completion of the previous sync.
- Syncs can run at most every 60 minutes in Airbyte Cloud. Reach out to [Sales](https://airbyte.com/company/talk-to-sales) if you require replication more frequently than once per hour.

:::note
For Scheduled or cron scheduled syncs, Airbyte guarantees syncs will initiate with a schedule accuracy of +/- 30 minutes.
:::