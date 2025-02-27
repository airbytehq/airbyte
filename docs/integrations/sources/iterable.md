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

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Supported Streams

- [Campaigns](https://api.iterable.com/api/docs#campaigns_campaigns)
- [Campaign Metrics](https://api.iterable.com/api/docs#campaigns_metrics)
- [Channels](https://api.iterable.com/api/docs#channels_channels)
- [Email Bounce](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
- [Email Click](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
- [Email Complaint](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
- [Email Open](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
- [Email Send](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
- [Email Send Skip](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
- [Email Subscribe](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
- [Email Unsubscribe](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
- [Events](https://api.iterable.com/api/docs#events_User_events)
- [Lists](https://api.iterable.com/api/docs#lists_getLists)
- [List Users](https://api.iterable.com/api/docs#lists_getLists_0)
- [Message Types](https://api.iterable.com/api/docs#messageTypes_messageTypes)
- [Metadata](https://api.iterable.com/api/docs#metadata_list_tables)
- [Templates](https://api.iterable.com/api/docs#templates_getTemplates) \(Incremental\)
- [Users](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
- [PushSend](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
- [PushSendSkip](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
- [PushOpen](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
- [PushUninstall](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
- [PushBounce](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
- [WebPushSend](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
- [WebPushClick](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
- [WebPushSendSkip](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
- [InAppSend](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
- [InAppOpen](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
- [InAppClick](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
- [InAppClose](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
- [InAppDelete](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
- [InAppDelivery](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
- [InAppSendSkip](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
- [InboxSession](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
- [InboxMessageImpression](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
- [SmsSend](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
- [SmsBounce](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
- [SmsClick](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
- [SmsReceived](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
- [SmsSendSkip](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
- [SmsUsageInfo](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
- [Purchase](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
- [CustomEvent](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)
- [HostedUnsubscribeClick](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental\)

## Additional notes

[List Users](https://api.iterable.com/api/docs#lists_getLists_0) Stream when meet `500 - Generic Error` will skip a broken slice and keep going with the next one. This is related to unexpected failures when trying to get users list for specific list ids. See #[24968](https://github.com/airbytehq/airbyte/issues/24968) issue for more details.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                                                                    |
|:--------|:-----------|:---------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0.6.28 | 2025-02-22 | [54287](https://github.com/airbytehq/airbyte/pull/54287) | Update dependencies |
| 0.6.27 | 2025-02-15 | [53814](https://github.com/airbytehq/airbyte/pull/53814) | Update dependencies |
| 0.6.26 | 2025-02-01 | [52726](https://github.com/airbytehq/airbyte/pull/52726) | Update dependencies |
| 0.6.25 | 2025-01-25 | [52277](https://github.com/airbytehq/airbyte/pull/52277) | Update dependencies |
| 0.6.24 | 2025-01-11 | [51163](https://github.com/airbytehq/airbyte/pull/51163) | Update dependencies |
| 0.6.23 | 2025-01-04 | [50889](https://github.com/airbytehq/airbyte/pull/50889) | Update dependencies |
| 0.6.22 | 2024-12-28 | [50608](https://github.com/airbytehq/airbyte/pull/50608) | Update dependencies |
| 0.6.21 | 2024-12-21 | [50101](https://github.com/airbytehq/airbyte/pull/50101) | Update dependencies |
| 0.6.20 | 2024-12-14 | [49211](https://github.com/airbytehq/airbyte/pull/49211) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.6.19 | 2024-12-12 | [48993](https://github.com/airbytehq/airbyte/pull/48993) | Update dependencies |
| 0.6.18 | 2024-11-04 | [48294](https://github.com/airbytehq/airbyte/pull/48294) | Update dependencies |
| 0.6.17 | 2024-10-29 | [47803](https://github.com/airbytehq/airbyte/pull/47803) | Update dependencies |
| 0.6.16 | 2024-10-28 | [47487](https://github.com/airbytehq/airbyte/pull/47487) | Update dependencies |
| 0.6.15 | 2024-10-23 | [47057](https://github.com/airbytehq/airbyte/pull/47057) | Update dependencies |
| 0.6.14 | 2024-10-12 | [46814](https://github.com/airbytehq/airbyte/pull/46814) | Update dependencies |
| 0.6.13 | 2024-10-05 | [46399](https://github.com/airbytehq/airbyte/pull/46399) | Update dependencies |
| 0.6.12 | 2024-09-28 | [46155](https://github.com/airbytehq/airbyte/pull/46155) | Update dependencies |
| 0.6.11 | 2024-09-21 | [45828](https://github.com/airbytehq/airbyte/pull/45828) | Update dependencies |
| 0.6.10 | 2024-09-14 | [45518](https://github.com/airbytehq/airbyte/pull/45518) | Update dependencies |
| 0.6.9 | 2024-09-07 | [45221](https://github.com/airbytehq/airbyte/pull/45221) | Update dependencies |
| 0.6.8 | 2024-08-31 | [45029](https://github.com/airbytehq/airbyte/pull/45029) | Update dependencies |
| 0.6.7 | 2024-08-24 | [44636](https://github.com/airbytehq/airbyte/pull/44636) | Update dependencies |
| 0.6.6 | 2024-08-17 | [44260](https://github.com/airbytehq/airbyte/pull/44260) | Update dependencies |
| 0.6.5 | 2024-08-12 | [43899](https://github.com/airbytehq/airbyte/pull/43899) | Update dependencies |
| 0.6.4 | 2024-08-10 | [43527](https://github.com/airbytehq/airbyte/pull/43527) | Update dependencies |
| 0.6.3 | 2024-08-03 | [43142](https://github.com/airbytehq/airbyte/pull/43142) | Update dependencies |
| 0.6.2 | 2024-07-27 | [42653](https://github.com/airbytehq/airbyte/pull/42653) | Update dependencies |
| 0.6.1 | 2024-07-23 | [42449](https://github.com/airbytehq/airbyte/pull/42449) | Fix OOM errors; bum CDK version |
| 0.6.0 | 2024-07-22 | [41983](https://github.com/airbytehq/airbyte/pull/41983) | Fix OOM errors; update CDK to v3 |
| 0.5.11 | 2024-07-20 | [42228](https://github.com/airbytehq/airbyte/pull/42228) | Update dependencies |
| 0.5.10 | 2024-07-13 | [41684](https://github.com/airbytehq/airbyte/pull/41684) | Update dependencies |
| 0.5.9 | 2024-07-10 | [41401](https://github.com/airbytehq/airbyte/pull/41401) | Update dependencies |
| 0.5.8 | 2024-07-09 | [41293](https://github.com/airbytehq/airbyte/pull/41293) | Update dependencies |
| 0.5.7 | 2024-07-06 | [40811](https://github.com/airbytehq/airbyte/pull/40811) | Update dependencies |
| 0.5.6 | 2024-06-25 | [40362](https://github.com/airbytehq/airbyte/pull/40362) | Update dependencies |
| 0.5.5 | 2024-06-22 | [40080](https://github.com/airbytehq/airbyte/pull/40080) | Update dependencies |
| 0.5.4 | 2024-06-17 | [39382](https://github.com/airbytehq/airbyte/pull/39382) | Refactor state handling for Python incremental streams |
| 0.5.3 | 2024-06-05 | [39142](https://github.com/airbytehq/airbyte/pull/39142) | Updated the `CDK` version to `0.89.0` to fix OOM |
| 0.5.2 | 2024-06-04 | [39077](https://github.com/airbytehq/airbyte/pull/39077) | [autopull] Upgrade base image to v1.2.1 |
| 0.5.1 | 2024-04-24 | [36645](https://github.com/airbytehq/airbyte/pull/36645) | Schema descriptions and CDK 0.80.0 |
| 0.5.0 | 2024-03-18 | [36231](https://github.com/airbytehq/airbyte/pull/36231) | Migrate connector to low-code |
| 0.4.0 | 2024-03-19 | [36267](https://github.com/airbytehq/airbyte/pull/36267) | Pin airbyte-cdk version to `^0` |
| 0.3.0 | 2024-02-20 | [35465](https://github.com/airbytehq/airbyte/pull/35465) | Per-error reporting and continue sync on stream failures |
| 0.2.2 | 2024-02-12 | [35150](https://github.com/airbytehq/airbyte/pull/35150) | Manage dependencies with Poetry. |
| 0.2.1 | 2024-01-12 | [1234](https://github.com/airbytehq/airbyte/pull/1234) | prepare for airbyte-lib |
| 0.2.0   | 2023-09-29 | [28457](https://github.com/airbytehq/airbyte/pull/30931) | Added `userId` to `email_bounce`, `email_click`, `email_complaint`, `email_open`, `email_send` `email_send_skip`, `email_subscribe`, `email_unsubscribe`, `events` streams |
| 0.1.31  | 2023-12-06 | [33106](https://github.com/airbytehq/airbyte/pull/33106) | Base image migration: remove Dockerfile and use the python-connector-base image                                                                                            |
| 0.1.30  | 2023-07-19 | [28457](https://github.com/airbytehq/airbyte/pull/28457) | Fixed TypeError for StreamSlice in debug mode                                                                                                                              |
| 0.1.29  | 2023-05-24 | [26459](https://github.com/airbytehq/airbyte/pull/26459) | Added requests reading timeout 300 seconds                                                                                                                                 |
| 0.1.28  | 2023-05-12 | [26014](https://github.com/airbytehq/airbyte/pull/26014) | Improve 500 handling for Events stream                                                                                                                                     |
| 0.1.27  | 2023-04-06 | [24962](https://github.com/airbytehq/airbyte/pull/24962) | `UserList` stream when meet `500 - Generic Error` will skip a broken slice and keep going with the next one                                                                |
| 0.1.26  | 2023-03-10 | [23938](https://github.com/airbytehq/airbyte/pull/23938) | Improve retry for `500 - Generic Error`                                                                                                                                    |
| 0.1.25  | 2023-03-07 | [23821](https://github.com/airbytehq/airbyte/pull/23821) | Added retry for `500 - Generic Error`, increased max attempts number to `6` to handle `ChunkedEncodingError`                                                               |
| 0.1.24  | 2023-02-14 | [22979](https://github.com/airbytehq/airbyte/pull/22979) | Specified date formatting in specification                                                                                                                                 |
| 0.1.23  | 2023-01-27 | [22011](https://github.com/airbytehq/airbyte/pull/22011) | Set `AvailabilityStrategy` for streams explicitly to `None`                                                                                                                |
| 0.1.22  | 2022-11-30 | [19913](https://github.com/airbytehq/airbyte/pull/19913) | Replace pendulum.parse -> dateutil.parser.parse to avoid memory leak                                                                                                       |
| 0.1.21  | 2022-10-27 | [18537](https://github.com/airbytehq/airbyte/pull/18537) | Improve streams discovery                                                                                                                                                  |
| 0.1.20  | 2022-10-21 | [18292](https://github.com/airbytehq/airbyte/pull/18292) | Better processing of 401 and 429 errors                                                                                                                                    |
| 0.1.19  | 2022-10-05 | [17602](https://github.com/airbytehq/airbyte/pull/17602) | Add check for stream permissions                                                                                                                                           |
| 0.1.18  | 2022-10-04 | [17573](https://github.com/airbytehq/airbyte/pull/17573) | Limit time range for SATs                                                                                                                                                  |
| 0.1.17  | 2022-09-02 | [16067](https://github.com/airbytehq/airbyte/pull/16067) | added new events streams                                                                                                                                                   |
| 0.1.16  | 2022-08-15 | [15670](https://github.com/airbytehq/airbyte/pull/15670) | Api key is passed via header                                                                                                                                               |
| 0.1.15  | 2021-12-06 | [8524](https://github.com/airbytehq/airbyte/pull/8524)   | Update connector fields title/description                                                                                                                                  |
| 0.1.14  | 2021-12-01 | [8380](https://github.com/airbytehq/airbyte/pull/8380)   | Update `Events` stream to use `export/userEvents` endpoint                                                                                                                 |
| 0.1.13  | 2021-11-22 | [8091](https://github.com/airbytehq/airbyte/pull/8091)   | Adjust slice ranges for email streams                                                                                                                                      |
| 0.1.12  | 2021-11-09 | [7780](https://github.com/airbytehq/airbyte/pull/7780)   | Split EmailSend stream into slices to fix premature connection close error                                                                                                 |
| 0.1.11  | 2021-11-03 | [7619](https://github.com/airbytehq/airbyte/pull/7619)   | Bugfix type error while incrementally loading the `Templates` stream                                                                                                       |
| 0.1.10  | 2021-11-03 | [7591](https://github.com/airbytehq/airbyte/pull/7591)   | Optimize export streams memory consumption for large requests                                                                                                              |
| 0.1.9   | 2021-10-06 | [5915](https://github.com/airbytehq/airbyte/pull/5915)   | Enable campaign_metrics stream                                                                                                                                             |
| 0.1.8   | 2021-09-20 | [5915](https://github.com/airbytehq/airbyte/pull/5915)   | Add new streams: campaign_metrics, events                                                                                                                                  |
| 0.1.7   | 2021-09-20 | [6242](https://github.com/airbytehq/airbyte/pull/6242)   | Updated schema for: campaigns, lists, templates, metadata                                                                                                                  |

</details>
