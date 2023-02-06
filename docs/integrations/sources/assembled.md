# Assembled

This page guides you through the process of setting up the [Assembled](https://www.assembled.com/) source connector.

## Set up the Insightly connector

1. Log into your [Airbyte Cloud](https://cloud.airbyte.io/workspaces) or Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Assembled** from the Source type dropdown.
4. Enter a name for your source.
5. For **API token**, enter the API token for your Assembled account.
6. For **Start date**, enter the date in YYYY-MM-DDTHH:mm:ssZ format. The data added on and after this date will be replicated.
7. (Optional) Configure **History Days**. This connector will backfill incremental streams from the configured start date. After the initial backfill, the connector will sync x days of data every day to keep the changing report data up to date. Every subsequent sync for a specific day will only sync the latest data for that day. This configuration configures how many days of data to sync per day. The default is 30 days. If you always want to latest data only, it is advised to do a full resync for incremental streams.
8. (Optional) Configure **Report Channels**. Configure what channels to sync reports for. The default are "email" and "phone".
9. (Optional) Configure **Forecast Channels**. Configure what channels to sync forecasts for. The default are "email" and "phone".
10. Click **Set up source**.

## Supported sync modes

The Assembled source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

 - Full Refresh
 - Incremental

## Supported Streams

The Assembled source connector supports the following streams:

* [Activity Types](https://docs.assembled.com/#get-v0-activity_types) \(Full table\)
* [Filters - Queues](https://docs.assembled.com/#get-v0-queues) \(Full table\)
* [Filters - Sites](https://docs.assembled.com/#get-v0-sites) \(Full table\)
* [Filters - Skills](https://docs.assembled.com/#get-v0-skills) \(Full table\)
* [Filters - Teams](https://docs.assembled.com/#get-v0-teams) \(Full table\)
* [People](https://docs.assembled.com/#get-v0-people) \(Full table\)
* [Requirement Types](https://docs.assembled.com/#get-v0-requirement_types) \(Full table\)
* [Activities](https://docs.assembled.com/#get-v0-activities) \(Incremental\)
* [Agent States](https://docs.assembled.com/#get-v0-agents-state) \(Incremental\)
* [Event Changes](https://docs.assembled.com/#get-v0-event_changes) \(Incremental\)
* [Forecasts](https://docs.assembled.com/#get-v0-forecasts) \(Incremental\)
* [Requirements](https://docs.assembled.com/#get-v0-requirements) \(Incremental\)
* [Reports - Adherence](https://docs.assembled.com/#adherence) \(Incremental\)
* [Reports - Agent Ticket Stats](https://docs.assembled.com/#agent-ticket-stats) \(Incremental\)

## Performance considerations

The connector is restricted by Assembled [requests limitation](https://docs.assembled.com/#rate-limiting).


## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                           |
| :------ | :--------- | :------------------------------------------------------- | :-------------------------------------------------------------------------------- |
| 0.1.0   | 2023-02-01 |                                                          | Release Assembled CDK Connector                                                   |
