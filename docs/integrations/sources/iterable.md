# Iterable

This page contains the setup guide and reference information for the Iterable source connector.

## Prerequisites

To set up the Iterable source connector, you'll need the Iterable [`Server-side` API Key with `standard` permissions](https://support.iterable.com/hc/en-us/articles/360043464871-API-Keys-).

## Set up the Iterable connector in Airbyte

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account or navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Iterable** from the Source type dropdown.
4. Enter the name for the Iterable connector.
5. For **API Key**, enter the [Iterable API key](https://support.iterable.com/hc/en-us/articles/360043464871-API-Keys-).
6. For **Start Date**, enter the date in YYYY-MM-DDTHH:mm:ssZ format. The data added on and after this date will be replicated.
7. Click **Set up source**.

## Supported sync modes

The Iterable source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

* [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
* [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
* [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
* [Incremental - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history)

## Supported Streams

* [Campaigns](https://api.iterable.com/api/docs#campaigns_campaigns)
* [Campaign Metrics](https://api.iterable.com/api/docs#campaigns_metrics)
* [Channels](https://api.iterable.com/api/docs#channels_channels)
* [Email Bounce](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
* [Email Click](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
* [Email Complaint](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
* [Email Open](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
* [Email Send](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
* [Email Send Skip](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
* [Email Subscribe](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
* [Email Unsubscribe](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
* [Events](https://api.iterable.com/api/docs#events_User_events)
* [Lists](https://api.iterable.com/api/docs#lists_getLists)
* [List Users](https://api.iterable.com/api/docs#lists_getLists_0)
* [Message Types](https://api.iterable.com/api/docs#messageTypes_messageTypes)
* [Metadata](https://api.iterable.com/api/docs#metadata_list_tables)
* [Templates](https://api.iterable.com/api/docs#templates_getTemplates) \(Incremental\)
* [Users](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
* [PushSend](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
* [PushSendSkip](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
* [PushOpen](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
* [PushUninstall](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
* [PushBounce](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
* [WebPushSend](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
* [WebPushClick](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
* [WebPushSendSkip](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
* [InAppSend](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
* [InAppOpen](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
* [InAppClick](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
* [InAppClose](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
* [InAppDelete](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
* [InAppDelivery](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
* [InAppSendSkip](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
* [InboxSession](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
* [InboxMessageImpression](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
* [SmsSend](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
* [SmsBounce](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
* [SmsClick](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
* [SmsReceived](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
* [SmsSendSkip](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
* [SmsUsageInfo](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
* [Purchase](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
* [CustomEvent](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
* [HostedUnsubscribeClick](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)

## Additional notes

[List Users](https://api.iterable.com/api/docs#lists_getLists_0) Stream when meet `500 - Generic Error` will skip a broken slice and keep going with the next one. This is related to unexpected failures when trying to get users list for specific list ids. See #[24968](https://github.com/airbytehq/airbyte/issues/24968) issue for more details.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                    |
|:--------|:-----------|:---------------------------------------------------------|:---------------------------------------------------------------------------|
| 0.1.28  | 2023-05-12 | [26014](https://github.com/airbytehq/airbyte/pull/26014) | Improve 500 handling for Events stream                                     |
| 0.1.27  | 2023-04-06 | [24962](https://github.com/airbytehq/airbyte/pull/24962) | `UserList` stream when meet `500 - Generic Error` will skip a broken slice and keep going with the next one |
| 0.1.26  | 2023-03-10 | [23938](https://github.com/airbytehq/airbyte/pull/23938) | Improve retry for `500 - Generic Error` |
| 0.1.25  | 2023-03-07 | [23821](https://github.com/airbytehq/airbyte/pull/23821) | Added retry for `500 - Generic Error`, increased max attempts number to `6` to handle `ChunkedEncodingError` |
| 0.1.24  | 2023-02-14 | [22979](https://github.com/airbytehq/airbyte/pull/22979) | Specified date formatting in specification  |
| 0.1.23  | 2023-01-27 | [22011](https://github.com/airbytehq/airbyte/pull/22011) | Set `AvailabilityStrategy` for streams explicitly to `None`                                                     |
| 0.1.22  | 2022-11-30 | [19913](https://github.com/airbytehq/airbyte/pull/19913) | Replace pendulum.parse -> dateutil.parser.parse to avoid memory leak       |
| 0.1.21  | 2022-10-27 | [18537](https://github.com/airbytehq/airbyte/pull/18537) | Improve streams discovery                                                  |
| 0.1.20  | 2022-10-21 | [18292](https://github.com/airbytehq/airbyte/pull/18292) | Better processing of 401 and 429 errors                                    |
| 0.1.19  | 2022-10-05 | [17602](https://github.com/airbytehq/airbyte/pull/17602) | Add check for stream permissions                                           |
| 0.1.18  | 2022-10-04 | [17573](https://github.com/airbytehq/airbyte/pull/17573) | Limit time range for SATs                                                  |
| 0.1.17  | 2022-09-02 | [16067](https://github.com/airbytehq/airbyte/pull/16067) | added new events streams                                                   |
| 0.1.16  | 2022-08-15 | [15670](https://github.com/airbytehq/airbyte/pull/15670) | Api key is passed via header                                               |
| 0.1.15  | 2021-12-06 | [8524](https://github.com/airbytehq/airbyte/pull/8524)   | Update connector fields title/description                                  |
| 0.1.14  | 2021-12-01 | [8380](https://github.com/airbytehq/airbyte/pull/8380)   | Update `Events` stream to use `export/userEvents` endpoint                 |
| 0.1.13  | 2021-11-22 | [8091](https://github.com/airbytehq/airbyte/pull/8091)   | Adjust slice ranges for email streams                                      |
| 0.1.12  | 2021-11-09 | [7780](https://github.com/airbytehq/airbyte/pull/7780)   | Split EmailSend stream into slices to fix premature connection close error |
| 0.1.11  | 2021-11-03 | [7619](https://github.com/airbytehq/airbyte/pull/7619)   | Bugfix type error while incrementally loading the `Templates` stream       |
| 0.1.10  | 2021-11-03 | [7591](https://github.com/airbytehq/airbyte/pull/7591)   | Optimize export streams memory consumption for large requests              |
| 0.1.9   | 2021-10-06 | [5915](https://github.com/airbytehq/airbyte/pull/5915)   | Enable campaign_metrics stream                                             |
| 0.1.8   | 2021-09-20 | [5915](https://github.com/airbytehq/airbyte/pull/5915)   | Add new streams: campaign_metrics, events                                  |
| 0.1.7   | 2021-09-20 | [6242](https://github.com/airbytehq/airbyte/pull/6242)   | Updated schema for: campaigns, lists, templates, metadata                  |

