# YouTube Analytics

This page contains the setup guide and reference information for the YouTube Analytics source connector.

## Prerequisites

The Google account you authorize must own or manage a YouTube channel. An account without an associated channel cannot access YouTube Reporting API data.

For Airbyte Open Source, you need a Google Cloud project with the YouTube Reporting API enabled and an OAuth 2.0 **Client ID**, **Client Secret**, and **Refresh Token** with the `https://www.googleapis.com/auth/yt-analytics.readonly` scope. See [Set up YouTube Analytics](#set-up-youtube-analytics) for instructions. Airbyte Cloud users authenticate with OAuth in the setup flow and do not need to provide these credentials.

YouTube partners may also provide a **Content Owner ID** to retrieve data on behalf of that content owner.

## Setup guide

Follow these steps to prepare YouTube access and then add the source in Airbyte.

## Set up YouTube Analytics

Airbyte Cloud users can authorize their Google account during source setup. For Airbyte Open Source, create OAuth credentials for the Google account that owns or manages your YouTube channel:

1. [Create or select a Google Cloud project](https://console.cloud.google.com/) and [enable the YouTube Reporting API](https://console.cloud.google.com/apis/api/youtubereporting.googleapis.com/overview).
2. [Configure the OAuth consent screen](https://developers.google.com/workspace/guides/configure-oauth-consent) and add the `https://www.googleapis.com/auth/yt-analytics.readonly` scope. If the app's publishing status is **Testing**, add the channel's Google account as a test user. Google documents that refresh tokens for External apps in Testing status expire after 7 days; see [refresh token expiration](https://developers.google.com/identity/protocols/oauth2#expiration).
3. [Create an OAuth client ID](https://support.google.com/cloud/answer/6158849) with the application type **Web application**. Add `https://developers.google.com/oauthplayground` as an authorized redirect URI, then copy the Client ID and Client Secret.
4. Open the [OAuth 2.0 Playground](https://developers.google.com/oauthplayground). Select the gear icon, choose **Use your own OAuth credentials**, and enter the Client ID and Client Secret. In Step 1, enter `https://www.googleapis.com/auth/yt-analytics.readonly` as the scope and select **Authorize APIs**. Sign in with the channel's Google account. In Step 2, select **Exchange authorization code for tokens** and copy the Refresh token.

See Google's [YouTube Reporting API authorization guide](https://developers.google.com/youtube/reporting/guides/authorization) for more information.

## Set up the YouTube Analytics connector in Airbyte

### For Airbyte Cloud:

1. [Log in to Airbyte Cloud](https://cloud.airbyte.com/workspaces).
2. In the left navigation bar, select **Sources**, then select **+ new source**.
3. Enter a name for the source and select **YouTube Analytics** from the source type list.
4. Select **Authenticate your account**, sign in with the Google account that owns or manages the channel, and authorize access.
5. Select **Set up source**.

### For Airbyte Open Source:

1. In the left navigation bar, select **Sources**, then select **+ new source**.
2. Enter a name for the source and select **YouTube Analytics** from the source type list.
3. Enter the **Client ID**, **Client Secret**, and **Refresh Token** you created in [Set up YouTube Analytics](#set-up-youtube-analytics).
4. Optionally, enter a **Content Owner ID**.
5. Select **Set up source**.

## Content Owner ID (optional)

The **Content Owner ID** field is for YouTube partners who participate in the [YouTube Partner Program](https://support.google.com/youtube/answer/72851) and manage multiple channels through a content owner account. This includes Multi-Channel Networks (MCNs) and media companies that manage content across multiple YouTube channels.

- If you are a regular YouTube channel owner, leave this field empty. The connector will retrieve data for the channel associated with your OAuth credentials.
- If you are a YouTube partner with a content owner account, enter your content owner ID to retrieve data for channels managed under that account.
- To find your content owner ID, check the URL when logged in to [YouTube Studio](https://studio.youtube.com/) (look for the `o=` parameter), use the [YouTube Content ID API](https://developers.google.com/youtube/partner/docs/v1/contentOwners/list), or contact your YouTube partner manager.

## Supported sync modes

The YouTube Analytics source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature           | Supported?                                                        |
| :---------------- | :---------------------------------------------------------------- |
| Full Refresh Sync | Yes                                                               |
| Incremental Sync  | Yes — report streams; `report_types` is full refresh only         |

## Supported Streams

- [report_types](https://developers.google.com/youtube/reporting/v1/reference/rest/v1/reportTypes/list) - The report types available to your channel or content owner. Full refresh only. The connection check uses this stream because it returns data with valid credentials alone and requires no reporting job.
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

Each report stream provides one YouTube bulk report. Incremental syncs download only report files YouTube created since the previous sync and also pick up files YouTube re-issues with corrected data. A re-issued file replaces an earlier report for the same days, so use **Incremental | Append + Deduped** for report streams. With **Incremental | Append**, the original rows and the corrected rows are both kept in the destination.

## Report availability

During the first sync, Airbyte creates a reporting job for each selected report if one does not already exist. YouTube begins generating reports after a job is created, and the first report is typically available within 48 hours. That report contains data for the day the job was scheduled. For example, if a job is scheduled on September 1, 2015, the report for September 1 is ready on September 3; the report for September 2 is posted on September 4.

When a new job is scheduled, YouTube also generates historical reports covering the 30-day period before the job was created. Historical reports are typically posted within a couple of days, and Airbyte syncs available historical data. A first sync that creates new jobs may therefore return no records from report streams.

YouTube makes generated reports available for 60 days, except for historical reports, which are available for 30 days. See the [YouTube Reporting API report documentation](https://developers.google.com/youtube/reporting/v1/reports) for details.

## YouTube API Services usage disclosure

This connector uses [YouTube API Services](https://developers.google.com/youtube/analytics) to retrieve data from YouTube. By using this connector, you agree to be bound by the [YouTube Terms of Service](https://www.youtube.com/t/terms).

YouTube API Services are provided by Google. For information about how Google handles data, review the [Google Privacy Policy](https://www.google.com/policies/privacy).

When using OAuth 2.0 authentication, this connector accesses authorized user data. You can revoke the connector's access to your Google account at any time through the [Google security settings page](https://myaccount.google.com/connections?filters=3,4&hl=en). To delete stored data that was previously synced, remove the relevant connection in your Airbyte workspace or delete the data from your configured destination.

## Rate limits and quotas

The connector limits its requests to 60 per minute. YouTube may also return a rate-limit error. The connector retries these requests automatically after about a minute; repeated rate-limit errors fail the sync. If your project's daily YouTube API quota is exhausted, the sync stops with **Daily YouTube API project quota is exhausted.** Try again after quota becomes available.

Airbyte Cloud uses an Airbyte Google Cloud project whose YouTube API quota is shared across Cloud connections. Airbyte Open Source uses the quota of the Google Cloud project configured for the source. Check your [project's quota page in Google Cloud](https://console.cloud.google.com/iam-admin/quotas) for current limits.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Performance considerations

Each selected report stream makes requests to find its reporting job and available reports, then downloads each available report file. Selecting more report streams can therefore use more of your project's quota.

The optional **Number of Concurrent Workers** setting controls how many report files download in parallel. The default is 2 and the maximum is 4. More workers can shorten syncs with many report files, but every worker shares the same request limit and YouTube API quota, so higher values can reach rate limits sooner.

## Limitations & Troubleshooting

- **401: no channel associated with the Google account.** The error starts with `The authorized Google account does not appear to have an associated YouTube channel.` Use an account that owns or manages a YouTube channel. If you are connecting as a content owner, also confirm the Content Owner ID is correct.
- **401: credentials rejected.** The error starts with `Google rejected the YouTube Reporting API credentials:` followed by Google's message. Re-authenticate the source. If the error continues, the Google account likely has no associated YouTube channel.
- **403: access denied.** The error starts with `The YouTube Reporting API denied access:` followed by Google's message. Confirm that the authorized Google account owns or manages the channel and that the OAuth consent screen includes the required scope. If you set a Content Owner ID, confirm that the account can act on behalf of that content owner.
- **Refresh token is invalid or expired.** Google rejected the refresh token, for example because it was revoked or expired. Re-authenticate the source on Airbyte Cloud, or create a new refresh token on Airbyte Open Source.
- **Daily quota exhausted.** If the sync reports **Daily YouTube API project quota is exhausted.**, check your project's quota and try again after quota becomes available.
- **No rows on the first sync.** YouTube may not have generated reports for newly created reporting jobs yet. Reports are typically available within 48 hours.
- **Skipped report files.** If YouTube lists a report file but it can no longer be downloaded (HTTP 404), most likely because it passed its [retention period](#report-availability), the connector skips that file, records a message in the sync logs, and the rest of the sync continues. The rows in that file are not synced.
- **Refresh token expires after 7 days.** This applies to External OAuth apps in Testing status. Add the channel's Google account as a test user, or publish the app according to Google's requirements.
- **Content-owner reports are not available as streams.** The available streams are channel and playlist reports. To retrieve YouTube Data API information, use the separate [YouTube Data connector](/integrations/sources/youtube-data).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| :----------- | :----------- | :--------------------------------------------------------- | :---------------------------------------------------- |
| 1.5.0 | 2026-10-21 | [89629](https://github.com/airbytehq/airbyte/pull/89629) | Emit report metrics as numbers, follow pagination on job and report listings, and give clearer errors for credential, permission and missing-file failures |
| 1.4.7 | 2026-10-27 | [90075](https://github.com/airbytehq/airbyte/pull/90075) | Update dependencies |
| 1.4.6 | 2026-10-20 | [89472](https://github.com/airbytehq/airbyte/pull/89472) | Update dependencies |
| 1.4.5 | 2026-10-13 | [88882](https://github.com/airbytehq/airbyte/pull/88882) | Update dependencies |
| 1.4.4 | 2026-10-06 | [88106](https://github.com/airbytehq/airbyte/pull/88106) | Update dependencies |
| 1.4.3 | 2026-09-29 | [87431](https://github.com/airbytehq/airbyte/pull/87431) | Update dependencies |
| 1.4.2 | 2026-09-22 | [86879](https://github.com/airbytehq/airbyte/pull/86879) | Update dependencies |
| 1.4.1 | 2026-09-15 | [86309](https://github.com/airbytehq/airbyte/pull/86309) | Update dependencies |
| 1.4.0 | 2026-09-09 | [85335](https://github.com/airbytehq/airbyte/pull/85335) | Restore incremental syncs for report streams, including reports that YouTube re-issues with corrected data |
| 1.3.4 | 2026-09-08 | [85727](https://github.com/airbytehq/airbyte/pull/85727) | Update dependencies |
| 1.3.3 | 2026-08-21 | [84945](https://github.com/airbytehq/airbyte/pull/84945) | Fail fast with a clear transient error when the daily YouTube API project quota is exhausted, and correctly classify rate-limited and server-error responses |
| 1.3.2 | 2026-08-18 | [84816](https://github.com/airbytehq/airbyte/pull/84816) | Update dependencies |
| 1.3.1 | 2026-08-11 | [82653](https://github.com/airbytehq/airbyte/pull/82653) | Update dependencies |
| 1.3.0 | 2026-08-03 | [83286](https://github.com/airbytehq/airbyte/pull/83286) | Add new `report_types` stream, fix `check` failures, and explain 401s caused by a Google account with no YouTube channel |
| 1.2.12 | 2026-07-23 | [82712](https://github.com/airbytehq/airbyte/pull/82712) | Fix setup check failure by pointing the connection check at the always-available `channel_basic_a3` report instead of `channel_annotations_a1` |
| 1.2.11 | 2026-07-14 | [82069](https://github.com/airbytehq/airbyte/pull/82069) | Update dependencies |
| 1.2.10 | 2026-06-30 | [81330](https://github.com/airbytehq/airbyte/pull/81330) | Update dependencies |
| 1.2.9 | 2026-06-23 | [80732](https://github.com/airbytehq/airbyte/pull/80732) | Update dependencies |
| 1.2.8 | 2026-06-16 | [80106](https://github.com/airbytehq/airbyte/pull/80106) | Update dependencies |
| 1.2.7 | 2026-06-09 | [79579](https://github.com/airbytehq/airbyte/pull/79579) | Update dependencies |
| 1.2.6 | 2026-06-02 | [79073](https://github.com/airbytehq/airbyte/pull/79073) | Update dependencies |
| 1.2.5 | 2026-04-28 | [77489](https://github.com/airbytehq/airbyte/pull/77489) | Update dependencies |
| 1.2.4 | 2026-04-21 | [74693](https://github.com/airbytehq/airbyte/pull/74693) | Update dependencies |
| 1.2.3 | 2026-02-24 | [73149](https://github.com/airbytehq/airbyte/pull/73149) | Update dependencies |
| 1.2.2 | 2026-02-03 | [72635](https://github.com/airbytehq/airbyte/pull/72635) | Update dependencies |
| 1.2.1 | 2026-01-20 | [72048](https://github.com/airbytehq/airbyte/pull/72048) | Update dependencies |
| 1.2.0 | 2026-01-14 | [71377](https://github.com/airbytehq/airbyte/pull/71377) | Promoting release candidate 1.2.0-rc.2 to a main version. |
| 1.2.0-rc.2 | 2026-01-09 | [71244](https://github.com/airbytehq/airbyte/pull/71244) | Fix incorrect report_id key and remove additional error message |
| 1.2.0-rc.1 | 2026-01-07 | [71169](https://github.com/airbytehq/airbyte/pull/71169) | Add optional content_owner_id config for multi-channel support and improve error handling |
| 1.1.2 | 2025-12-18 | [70715](https://github.com/airbytehq/airbyte/pull/70715) | Update dependencies |
| 1.1.1 | 2025-12-02 | [64964](https://github.com/airbytehq/airbyte/pull/64964) | Update dependencies |
| 1.1.0 | 2025-11-17 | [69352](https://github.com/airbytehq/airbyte/pull/69352) | Promoting release candidate 1.1.0-rc.1 to a main version. |
| 1.1.0-rc.1 | 2025-11-02 | [42838](https://github.com/airbytehq/airbyte/pull/42838) | Migrate to Manifest-only |
| 1.0.0 | 2025-10-30 | [66558](https://github.com/airbytehq/airbyte/pull/66558) | Update deprecated channel and playlist BULK reports |
| 0.2.0 | 2025-02-07 | [53196](https://github.com/airbytehq/airbyte/pull/53196) | Update check connection and empty responses |
| 0.1.7 | 2025-02-26 | [54696](https://github.com/airbytehq/airbyte/pull/54696) | Update requests-mock dependency version |
| 0.1.6 | 2024-06-17 | [39529](https://github.com/airbytehq/airbyte/pull/39529) | Pin CDK version to 0.38.0 |
| 0.1.5 | 2024-05-21 | [38546](https://github.com/airbytehq/airbyte/pull/38546) | [autopull] base image + poetry + up_to_date |
| 0.1.4 | 2023-05-22 | [26420](https://github.com/airbytehq/airbyte/pull/26420) | Migrate to advancedAuth |
| 0.1.3 | 2022-09-30 | [17454](https://github.com/airbytehq/airbyte/pull/17454) | Added custom backoff logic |
| 0.1.2 | 2022-09-29 | [17399](https://github.com/airbytehq/airbyte/pull/17399) | Fixed `403` error while `check connection` |
| 0.1.1 | 2022-08-18 | [15744](https://github.com/airbytehq/airbyte/pull/15744) | Fix `channel_basic_a2` schema fields data type |
| 0.1.0 | 2021-11-01 | [7407](https://github.com/airbytehq/airbyte/pull/7407) | Initial Release |

</details>
