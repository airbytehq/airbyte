# Data Loading

## **Why don’t I see any data in my destination yet?**

It can take a while for Airbyte to load data into your destination. Some sources have restrictive API limits which constrain how much data we can sync in a given time. Large amounts of data in your source can also make the initial sync take longer. You can check your sync status in your connection detail page that you can access through the destination detail page or the source one.

## **What happens if a sync fails?**

You won't loose data when a sync fails, however, no data will be added or updated in your destination.

Airbyte will automatically attempt to replicate data 3 times. You can see and export the logs for those attempts in the connection detail page. You can access this page through the Source or Destination detail page.

In the future, you will be able to configure a notification \(email, Slack...\) when a sync fails, with an option to create a GitHub issue with the logs. We’re still working on it, and the purpose would be to help the community and the Airbyte team fix the issue as soon as possible, especially if it is a connector issue.

Until we have this system in place, here is what you can do:

* File a GitHub issue: go [here](https://github.com/airbytehq/airbyte/issues/new?assignees=&labels=type%2Fbug&template=bug-report.md&title=) and file an issue with the detailed logs copied in the issue’s description. The team will be notified about your issue and will update it for any progress or comment on it.  
* Fix the issue yourself: Airbyte is open source so you don’t need to wait for anybody to fix your issue if it is important to you. To do so, just fork the [GitHub project](http://github.com/airbytehq/airbyte) and fix the piece of code that need fixing. If you’re okay with contributing your fix to the community, you can submit a pull request. We will review it ASAP.
* Ask on Slack: don’t hesitate to ping the team on [Slack](https://slack.airbyte.io).

Once all this is done, Airbyte resumes your sync from where it left off.

We truly appreciate any contribution you make to help the community. Airbyte will become the open-source standard only if everybody participates.

## **What happens to data in the pipeline if the destination gets disconnected? Could I lose data, or wind up with duplicate data when the pipeline is reconnected?**

Airbyte is architected to prevent data loss or duplication. We will display a failure for the sync, and re-attempt it at the next syncing, according to the frequency you set.

## **How frequently can Airbyte sync data?**

You can adjust the load time to run as frequent as every five minutes and as infrequent as every 24 hours.

## **Why wouldn’t I choose to load all of my data every five minutes?**

While frequent data loads will give you more up-to-date data, there are a few reasons you wouldn’t want to load your data every five minutes, including:

* Higher API usage may cause you to hit a limit that could impact other systems that rely on that API.
* Higher cost of loading data into your warehouse.
* More frequent delays, resulting in increased delay notification emails. For instance, if the data source generally takes several hours to update but you choose five-minute increments, you may receive a delay notification every sync.

We generally recommend setting the incremental loads to every hour to help limit API calls.

## **Is there a way to know the estimated time to completion for the first historic sync?**

Unfortunately not yet.

## **I see you support a lot of connectors – what about connectors Airbyte doesn’t support yet?**

You can either:

* Submit a [connector request](https://github.com/airbytehq/airbyte/issues/new?assignees=&labels=area%2Fintegration%2C+new-integration&template=new-integration-request.md&title=) on our Github project, and be notified once we or the community build a connector for it. 
* Build a connector yourself by forking our [GitHub project](https://github.com/airbytehq/airbyte) and submitting a pull request. Here are the [instructions how to build a connector](../contributing-to-airbyte/building-new-connector/).
* Ask on Slack: don’t hesitate to ping the team on [Slack](https://slack.airbyte.io).

## **What kind of notifications do I get?**

For the moment, the UI will only display one kind of notification: when a sync fails, we will display the failure at the source/destination level in the list of sources/destinations, and in the connection detail page along with the logs.

However, there are other types of notifications we’re thinking about:

* When a connector that you use is no longer up to date
* When your connections fails
* When core isn't up to date

