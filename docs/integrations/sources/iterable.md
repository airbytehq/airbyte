# Iterable

This page contains the setup guide and reference information for the Iterable source connector.

## Prerequisites

* Iterable Account
* Iterable API Key with `standard` permissions. See [API Keys docs](https://support.iterable.com/hc/en-us/articles/360043464871-API-Keys-) for more details.

## Setup guide
### Step 1: Set up Iterable

Please read [How to find your API key](https://support.iterable.com/hc/en-us/articles/360043464871-API-Keys-#creating-api-keys).

## Step 2: Set up the Iterable connector in Airbyte
### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Iterable connector and select **Iterable** from the Source type dropdown. 
4. Enter your `api_key`
5. Enter the `start_date` you want your sync to start from
6. Click **Set up source**

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard
2. Set the name for your source 
3. Enter your `api_key`
4. Enter the `start_date` you want your sync to start from
5. Click **Set up source**

## Supported sync modes

The Iterable source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | Yes        |
| SSL connection    | Yes        |

## Supported Streams

* [Campaigns](https://api.iterable.com/api/docs#campaigns_campaigns)
* [Campaign Metrics](https://api.iterable.com/api/docs#campaigns_metrics)
* [Channels](https://api.iterable.com/api/docs#channels_channels)
* [Email Bounce](https://api.iterable.com/api/docs#export_exportDataJson)
* [Email Click](https://api.iterable.com/api/docs#export_exportDataJson)
* [Email Complaint](https://api.iterable.com/api/docs#export_exportDataJson)
* [Email Open](https://api.iterable.com/api/docs#export_exportDataJson)
* [Email Send](https://api.iterable.com/api/docs#export_exportDataJson)
* [Email Send Skip](https://api.iterable.com/api/docs#export_exportDataJson)
* [Email Subscribe](https://api.iterable.com/api/docs#export_exportDataJson)
* [Email Unsubscribe](https://api.iterable.com/api/docs#export_exportDataJson)
* [Events](https://api.iterable.com/api/docs#events_User_events)
* [Lists](https://api.iterable.com/api/docs#lists_getLists)
* [List Users](https://api.iterable.com/api/docs#lists_getLists_0)
* [Message Types](https://api.iterable.com/api/docs#messageTypes_messageTypes)
* [Metadata](https://api.iterable.com/api/docs#metadata_list_tables)
* [Templates](https://api.iterable.com/api/docs#templates_getTemplates)
* [Users](https://api.iterable.com/api/docs#export_exportDataJson)

## Changelog

| Version | Date       | Pull Request | Subject                                                                    |
|:--------|:-----------| :-----       |:---------------------------------------------------------------------------|
| 0.1.16  | 2022-08-15 | [15670](https://github.com/airbytehq/airbyte/pull/15670) | Api key is passed via header                                             |
| 0.1.15  | 2021-12-06 | [8524](https://github.com/airbytehq/airbyte/pull/8524) | Update connector fields title/description                                  |
| 0.1.14  | 2021-12-01 | [8380](https://github.com/airbytehq/airbyte/pull/8380) | Update `Events` stream to use `export/userEvents` endpoint                 |
| 0.1.13  | 2021-11-22 | [8091](https://github.com/airbytehq/airbyte/pull/8091) | Adjust slice ranges for email streams                                      |
| 0.1.12  | 2021-11-09 | [7780](https://github.com/airbytehq/airbyte/pull/7780) | Split EmailSend stream into slices to fix premature connection close error |
| 0.1.11  | 2021-11-03 | [7619](https://github.com/airbytehq/airbyte/pull/7619) | Bugfix type error while incrementally loading the `Templates` stream       |
| 0.1.10  | 2021-11-03 | [7591](https://github.com/airbytehq/airbyte/pull/7591) | Optimize export streams memory consumption for large requests              |
| 0.1.9   | 2021-10-06 | [5915](https://github.com/airbytehq/airbyte/pull/5915) | Enable campaign_metrics stream                                             |
| 0.1.8   | 2021-09-20 | [5915](https://github.com/airbytehq/airbyte/pull/5915) | Add new streams: campaign_metrics, events                                  |
| 0.1.7   | 2021-09-20 | [6242](https://github.com/airbytehq/airbyte/pull/6242) | Updated schema for: campaigns, lists, templates, metadata                  |

