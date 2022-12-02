# Data Loading

## **Why don’t I see any data in my destination yet?**

It can take a while for Airbyte to load data into your destination. Some sources have restrictive API limits which constrain how much 
data we can sync in a given time. Large amounts of data in your source can also make the initial sync take longer. You can check your
sync status in your connection detail page that you can access through the destination detail page or the source one.

## **Why my final tables are being recreated everytime?**

Airbyte ingests data into raw tables and applies the process of normalization if you selected it in the connection page.
The normalization runs a full refresh each sync and for some destinations like Snowflake, Redshift, Bigquery this may incur more
resource consumption and more costs. You need to pay attention to the frequency that you're retrieving your data to avoid issues.
For example, if you create a connection to sync every 5 minutes with incremental sync on, it will only retrieve new records into the raw tables but will apply normalization
to *all* the data in every sync! If you have tons of data, this may not be the right sync frequency for you.

There is a [Github issue](https://github.com/airbytehq/airbyte/issues/4286) to implement normalization using incremental, which will reduce
costs and resources in your destination.

## **What happens if a sync fails?**

You won't lose data when a sync fails, however, no data will be added or updated in your destination.

Airbyte will automatically attempt to replicate data 3 times. You can see and export the logs for those attempts in the connection 
detail page. You can access this page through the Source or Destination detail page.

You can configure a Slack webhook to warn you when a sync fails.

In the future you will be able to configure other notification method (email, Sentry) and an option to create a
GitHub issue with the logs. We’re still working on it, and the purpose would be to help the community and the Airbyte team to fix the
issue as soon as possible, especially if it is a connector issue.

Until Airbyte has this system in place, here is what you can do:

* File a GitHub issue: go [here](https://github.com/airbytehq/airbyte/issues/new?assignees=&labels=type%2Fbug&template=bug-report.md&title=) 
  and file an issue with the detailed logs copied in the issue’s description. The team will be notified about your issue and will update
  it for any progress or comment on it.  
* Fix the issue yourself: Airbyte is open source so you don’t need to wait for anybody to fix your issue if it is important to you.
  To do so, just fork the [GitHub project](https://github.com/airbytehq/airbyte) and fix the piece of code that need fixing. If you’re okay
  with contributing your fix to the community, you can submit a pull request. We will review it ASAP.
* Ask on Slack: don’t hesitate to ping the team on [Slack](https://slack.airbyte.io).

Once all this is done, Airbyte resumes your sync from where it left off.

We truly appreciate any contribution you make to help the community. Airbyte will become the open-source standard only if everybody participates.

## **Can Airbyte support 2-way sync i.e. changes from A go to B and changes from B go to A?**

Airbyte actually does not support this right now. There are some details around how we handle schema and tables names that isn't going to 
work for you in the current iteration.
If you attempt to do a circular dependency between source and destination, you'll end up with the following
A.public.table_foo writes to B.public.public_table_foo to A.public.public_public_table_foo. You won't be writing into your original table,
which I think is your intention.


## **What happens to data in the pipeline if the destination gets disconnected? Could I lose data, or wind up with duplicate data when the pipeline is reconnected?**

Airbyte is architected to prevent data loss or duplication. Airbyte will display a failure for the sync, and re-attempt it at the next syncing,
according to the frequency you set.

## **How frequently can Airbyte sync data?**

You can adjust the load time to run as frequent as every hour or as infrequent as once a year using [Cron expressions](https://docs.airbyte.com/cloud/managing-airbyte-cloud#edit-stream-configuration). 

## **Why wouldn’t I choose to load all of my data more frequently?**

While frequent data loads will give you more up-to-date data, there are a few reasons you wouldn’t want to load your too frequently, including:

* Higher API usage may cause you to hit a limit that could impact other systems that rely on that API.
* Higher cost of loading data into your warehouse.
* More frequent delays, resulting in increased delay notification emails. For instance, if the data source generally takes several hours to 
  update but you wanted five-minute increments, you may receive a delay notification every sync.

Generally is recommended setting the incremental loads to every hour to help limit API calls.

## **Is there a way to know the estimated time to completion for the first historic sync?**

Unfortunately not yet.

## **Do you support change data capture \(CDC\) or logical replication for databases?**

Airbyte currently supports [CDC for Postgres and Mysql](../../understanding-airbyte/cdc.md). Airbyte is adding support for a few other 
databases you can check in the roadmap.

## Using incremental sync, is it possible to add more fields when some new columns are added to a source table, or when a new table is added?

For the moment, incremental sync doesn't support schema changes, so you would need to perform a full refresh whenever that happens.
Here’s a related [Github issue](https://github.com/airbytehq/airbyte/issues/1601).

## There is a limit of how many tables one connection can handle?

Yes, for more than 6000 thousand tables could be a problem to load the information on UI.

There are two Github issues about this limitation: [Issue #3942](https://github.com/airbytehq/airbyte/issues/3942) 
and [Issue #3943](https://github.com/airbytehq/airbyte/issues/3943).

## Help, Airbyte is hanging/taking a long time to discover my source's schema!

This usually happens for database sources that contain a lot of tables. This should resolve itself in half an hour or so.

If the source contains more than 6k tables, see the [above question](#there-is-a-limit-of-how-many-tables-one-connection-can-handle).

There is a known issue with [Oracle databases](https://github.com/airbytehq/airbyte/issues/4944).

## **I see you support a lot of connectors – what about connectors Airbyte doesn’t support yet?**

You can either:

* Submit a [connector request](https://github.com/airbytehq/airbyte/issues/new?assignees=&labels=area%2Fintegration%2C+new-integration&template=new-integration-request.md&title=) on our Github project, and be notified once we or the community build a connector for it. 
* Build a connector yourself by forking our [GitHub project](https://github.com/airbytehq/airbyte) and submitting a pull request. Here
  are the [instructions how to build a connector](../../contributing-to-airbyte/README.md).
* Ask on Slack: don’t hesitate to ping the team on [Slack](https://slack.airbyte.io).

## **What kind of notifications do I get?**

For the moment, the UI will only display one kind of notification: when a sync fails, Airbyte will display the failure at the source/destination 
level in the list of sources/destinations, and in the connection detail page along with the logs.

However, there are other types of notifications:

* When a connector that you use is no longer up to date
* When your connections fails
* When core isn't up to date

