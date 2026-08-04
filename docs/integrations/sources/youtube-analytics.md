# YouTube Analytics

This page contains the setup guide and reference information for the YouTube Analytics source connector.

This connector reads bulk reports from the [YouTube Reporting API](https://developers.google.com/youtube/reporting/v1/reports). It doesn't use the YouTube Analytics targeted-query API, so the data you get matches YouTube's predefined channel and playlist reports rather than an arbitrary set of dimensions and metrics.

## Prerequisites

- A Google account that owns or manages a YouTube channel. All Reporting API data belongs to a channel or a content owner, so an account with no associated channel can't read any data.
- Authorization for the `https://www.googleapis.com/auth/yt-analytics.readonly` [scope](https://developers.google.com/youtube/reporting/v1/reports#step-1:-retrieve-authorization-credentials). The connector doesn't request the monetary scope, so revenue and ad performance reports aren't available.
- For self-managed Airbyte: a Google Cloud project with the [YouTube Reporting API](https://console.cloud.google.com/apis/api/youtubereporting.googleapis.com/overview) enabled, an OAuth client, and a refresh token for that client.

## Setup guide

### Airbyte Cloud

1. In the left navigation bar, click **Sources**. In the top-right corner, click **New source**.
2. Search for and select **YouTube Analytics**, then enter a name for the source.
3. Click **Authenticate your account** and complete Google's consent screen with the account that has access to your channel.
4. Optionally enter a **Content Owner ID**. See [Content Owner ID](#content-owner-id).
5. Click **Set up source**.

### Self-managed Airbyte

Self-managed deployments authenticate with your own Google OAuth client instead of Airbyte's.

1. In your Google Cloud project, enable the [YouTube Reporting API](https://console.cloud.google.com/apis/api/youtubereporting.googleapis.com/overview) and create an OAuth 2.0 client ID of type **Web application** or **Desktop app**.
2. Generate a refresh token for that client, granting the `https://www.googleapis.com/auth/yt-analytics.readonly` scope with the Google account that has access to your channel.
3. In Airbyte, click **Sources** > **New source**, then select **YouTube Analytics**.
4. Enter your **Client ID**, **Client Secret**, and **Refresh Token**.
5. Optionally enter a **Content Owner ID**. See [Content Owner ID](#content-owner-id).
6. Click **Set up source**.

The connection check reads the `report_types` stream, which only requires valid credentials and doesn't create any reporting jobs.

### Content Owner ID

The **Content Owner ID** field is for YouTube partners who participate in the [YouTube Partner Program](https://support.google.com/youtube/answer/72851) and manage multiple channels through a content owner account. This includes Multi-Channel Networks (MCNs) and media companies that manage content across multiple YouTube channels.

- If you are a regular YouTube channel owner, leave this field empty. The connector will retrieve data for the channel associated with your OAuth credentials.
- If you are a YouTube partner with a content owner account, enter your content owner ID to retrieve data for channels managed under that account.
- To find your content owner ID, you can check the URL when logged into the [YouTube Studio](https://studio.youtube.com/) (look for the `o=` parameter), use the [YouTube Content ID API](https://developers.google.com/youtube/partner/docs/v1/contentOwners/list), or contact your YouTube partner manager.

When you set this field, the connector adds the `onBehalfOfContentOwner` parameter to its requests. The streams themselves are still channel and playlist reports; the content owner-specific report types, such as `content_owner_basic_a4`, aren't available in this connector.

## How reporting jobs affect your syncs

YouTube doesn't generate a bulk report until a [reporting job](https://developers.google.com/youtube/reporting/v1/reports#step-3:-create-a-reporting-job) exists for that report type. For each stream you enable, the connector reuses an existing job or creates one named `Airbyte reporting job` during the first sync of that stream. Setting up the source doesn't create any jobs. This has a few consequences worth planning for:

- **The first sync of a new source returns no report records.** It creates the reporting jobs; records begin to arrive on a sync that runs at least 48 hours later.
- **Recent days lag by about 48 hours.** The report for a given day is ready roughly two days later. If a job is created on September 1, the report for September 1 arrives on September 3, and the report for September 2 arrives on September 4.
- **Historical data goes back 30 days.** When YouTube creates a job, it also generates reports covering the 30 days before that date, and the connector syncs them. There's no way to backfill further, so a stream you enable today can't return data from before last month.
- **Reports expire.** YouTube keeps generated reports for 60 days, and historical reports for 30 days. If a connection is disabled or failing for longer than that, the missed days are gone permanently; only newly generated reports are synced when the connection resumes.
- **Each report covers one day** in Pacific time (UTC-8), and the connector stores that day in the `date` field as an integer such as `20260730`. `date` is also the cursor for incremental syncs.
- **Some rows are anonymized.** YouTube replaces dimension values with aggregated or null values when the underlying metrics don't meet its privacy threshold, so expect rows with empty `video_id` or `country_code` values.

## Supported sync modes

The YouTube Analytics source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | Yes        |
| SSL connection    | Yes        |

Because YouTube only exposes each report as complete daily files, incremental syncs resume from the last day already synced rather than from a timestamp within a day.

## Supported streams

Each stream except `report_types` corresponds to one YouTube channel or playlist report. Enable only the reports you need: every enabled report stream creates a reporting job in your account.

- [report_types](https://developers.google.com/youtube/reporting/v1/reference/rest/v1/reportTypes/list) - the report types available to your channel or content owner. Full refresh only, and it doesn't require a reporting job.
- [channel_annotations_a1](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#video-annotations)
- [channel_basic_a3](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#video-user-activity)
- [channel_cards_a1](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#video-cards)
- [channel_combined_a3](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#video-combined)
- [channel_demographics_a1](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#video-viewer-demographics)
- [channel_device_os_a3](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#video-device-type-and-operating-system)
- [channel_end_screens_a1](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#video-end-screens)
- [channel_playback_location_a3](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#video-playback-locations)
- [channel_province_a3](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#video-province)
- [channel_sharing_service_a1](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#video-content-sharing)
- [channel_subtitles_a3](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#video-subtitles)
- [channel_traffic_source_a3](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#video-traffic-sources)
- [playlist_basic_a2](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#playlist-user-activity)
- [playlist_combined_a2](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#playlist-combined)
- [playlist_device_os_a2](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#playlist-device-type-and-operating-system)
- [playlist_playback_location_a2](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#playlist-playback-locations)
- [playlist_province_a2](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#playlist-province)
- [playlist_traffic_source_a2](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#playlist-traffic-sources)

## Troubleshooting

### The connection check fails with "no stream slices were found"

Upgrade to version 1.3.0 or later, which checks the `reportTypes` endpoint instead of a report that may have no reporting job. Versions before 1.2.12 checked the `channel_annotations_a1` report, and versions 1.2.12 through 1.2.x checked `channel_basic_a3`; both can fail this way.

### A stream syncs no records

This is expected in two cases: the reporting job for that report was created less than 48 hours ago, or your channel has no activity for the dimensions in that report. YouTube also generates report files for days with no data, and those files contain only a header row.

### Setup fails with "The authorized Google account does not appear to have an associated YouTube channel"

The account you authorized has no YouTube channel or content owner linked to it, so the Reporting API rejects its requests with a 401. Create a channel for that account, or re-authenticate with an account that already owns or manages one. If you're connecting as a content owner, also confirm the **Content Owner ID** is correct.

### Requests fail with a 403 error

The authorized Google account must have access to the channel's analytics. Re-authenticate with an account that can view the channel in [YouTube Studio](https://studio.youtube.com/), and confirm you granted the `yt-analytics.readonly` scope. If you set a **Content Owner ID**, confirm the account is linked to that content owner.

## YouTube API Services usage disclosure

This connector uses [YouTube API Services](https://developers.google.com/youtube/analytics) to retrieve data from YouTube. By using this connector, you agree to be bound by the [YouTube Terms of Service](https://www.youtube.com/t/terms).

YouTube API Services are provided by Google. For information about how Google handles data, review the [Google Privacy Policy](https://www.google.com/policies/privacy).

When using OAuth 2.0 authentication, this connector accesses authorized user data. You can revoke the connector's access to your Google account at any time through the [Google security settings page](https://myaccount.google.com/connections?filters=3,4&hl=en). To delete stored data that was previously synced, remove the relevant connection in your Airbyte workspace or delete the data from your configured destination.

## Performance considerations

The YouTube Reporting API has the following quota limits:

- Free requests per day: 20,000
- Free requests per 100 seconds: 100
- Free requests per minute: 60

The connector retrieves bulk report data from YouTube's reporting jobs, which minimizes API quota usage compared to making individual queries for each metric.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version    | Date       | Pull Request                                             | Subject                                             |
|:-----------|:-----------|:---------------------------------------------------------|:----------------------------------------------------|
| 1.3.0 | 2026-08-04 | [83286](https://github.com/airbytehq/airbyte/pull/83286) | Add new `report_types` stream, use it for the connection check, and explain 401s caused by a Google account with no YouTube channel |
| 1.2.12 | 2026-07-30 | [82712](https://github.com/airbytehq/airbyte/pull/82712) | Fix setup check failure by pointing the connection check at the always-available `channel_basic_a3` report instead of `channel_annotations_a1` |
| 1.2.11 | 2026-07-14 | [82069](https://github.com/airbytehq/airbyte/pull/82069) | Update dependencies |
| 1.2.10 | 2026-06-30 | [81330](https://github.com/airbytehq/airbyte/pull/81330) | Update dependencies |
| 1.2.9 | 2026-06-23 | [80732](https://github.com/airbytehq/airbyte/pull/80732) | Update dependencies |
| 1.2.8 | 2026-06-16 | [80106](https://github.com/airbytehq/airbyte/pull/80106) | Update dependencies |
| 1.2.7 | 2026-06-09 | [79579](https://github.com/airbytehq/airbyte/pull/79579) | Update dependencies |
| 1.2.6 | 2026-06-02 | [79073](https://github.com/airbytehq/airbyte/pull/79073) | Update dependencies |
| 1.2.5 | 2026-04-28 | [77489](https://github.com/airbytehq/airbyte/pull/77489) | Update dependencies |
| 1.2.4 | 2026-04-21 | [74693](https://github.com/airbytehq/airbyte/pull/74693) | Update dependencies |
| 1.2.3 | 2026-02-24 | [73149](https://github.com/airbytehq/airbyte/pull/73149) | Update dependencies |
| 1.2.2 | 2026-02-06 | [72635](https://github.com/airbytehq/airbyte/pull/72635) | Update dependencies |
| 1.2.1 | 2026-01-20 | [72048](https://github.com/airbytehq/airbyte/pull/72048) | Update dependencies |
| 1.2.0 | 2026-01-14 | [71377](https://github.com/airbytehq/airbyte/pull/71377) | Promoting release candidate 1.2.0-rc.2 to a main version. |
| 1.2.0-rc.2 | 2026-01-09 | [71244](https://github.com/airbytehq/airbyte/pull/71244) | Fix incorrect report_id key and remove additional error message |
| 1.2.0-rc.1 | 2026-01-07 | [71169](https://github.com/airbytehq/airbyte/pull/71169) | Add optional content_owner_id config for multi-channel support and improve error handling |
| 1.1.2 | 2025-12-18 | [70715](https://github.com/airbytehq/airbyte/pull/70715) | Update dependencies |
| 1.1.1 | 2025-12-02 | [64964](https://github.com/airbytehq/airbyte/pull/64964) | Update dependencies |
| 1.1.0 | 2025-11-17 | [69352](https://github.com/airbytehq/airbyte/pull/69352) | Promoting release candidate 1.1.0-rc.1 to a main version. |
| 1.1.0-rc.1 | 2025-11-10 | [42838](https://github.com/airbytehq/airbyte/pull/42838) | Migrate to Manifest-only |
| 1.0.0 | 2025-10-30 | [66558](https://github.com/airbytehq/airbyte/pull/66558) | Update deprecated channel and playlist BULK reports |
| 0.2.0 | 2025-05-29 | [53196](https://github.com/airbytehq/airbyte/pull/53196) | Update check connection and empty responses |
| 0.1.7 | 2025-02-27 | [54696](https://github.com/airbytehq/airbyte/pull/54696) | Update requests-mock dependency version |
| 0.1.6 | 2024-06-17 | [39529](https://github.com/airbytehq/airbyte/pull/39529) | Pin CDK version to 0.38.0 |
| 0.1.5 | 2024-05-21 | [38546](https://github.com/airbytehq/airbyte/pull/38546) | [autopull] base image + poetry + up_to_date |
| 0.1.4 | 2023-05-22 | [26420](https://github.com/airbytehq/airbyte/pull/26420) | Migrate to advancedAuth |
| 0.1.3 | 2022-09-30 | [17454](https://github.com/airbytehq/airbyte/pull/17454) | Added custom backoff logic |
| 0.1.2 | 2022-09-29 | [17399](https://github.com/airbytehq/airbyte/pull/17399) | Fixed `403` error while `check connection` |
| 0.1.1 | 2022-08-18 | [15744](https://github.com/airbytehq/airbyte/pull/15744) | Fix `channel_basic_a2` schema fields data type |
| 0.1.0 | 2021-11-01 | [7407](https://github.com/airbytehq/airbyte/pull/7407) | Initial Release |

</details>
