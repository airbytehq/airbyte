# YouTube Analytics

This page contains the setup guide and reference information for the YouTube Analytics source connector.

## Prerequisites

YouTube does not start to generate a report until you create a [reporting job](https://developers.google.com/youtube/reporting/v1/reports#step-3:-create-a-reporting-job) for that report.
Airbyte creates a reporting job for your report or uses current reporting job if it's already exists.
The report will be available within 48 hours of creating the reporting job and will be for the day that the job was scheduled.
For example, if you schedule a job on September 1, 2015, then the report for September 1, 2015, will be ready on September 3, 2015.
The report for September 2, 2015, will be posted on September 4, 2015, and so forth.
Youtube also generates historical data reports covering the 30-day period prior to when you created the job. Airbyte syncs all available historical data too.

## Setup guide

### Step 1: Set up YouTube Analytics

- Go to the [YouTube Reporting API dashboard](https://console.cloud.google.com/apis/api/youtubereporting.googleapis.com/overview) in the project for your service user. Enable the API for your account.
- Use your Google account and authorize over Google's OAuth 2.0 on connection setup. Please make sure to grant the following [authorization scope](https://developers.google.com/youtube/reporting/v1/reports#step-1:-retrieve-authorization-credentials): `https://www.googleapis.com/auth/yt-analytics.readonly`.

## Step 2: Set up the YouTube Analytics connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the YouTube Analytics connector and select **YouTube Analytics** from the Source type dropdown.
4. Select `Authenticate your account`.
5. Log in and Authorize to the Instagram account and click `Set up source`.

### For Airbyte OSS:

2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the YouTube Analytics connector and select **YouTube Analytics** from the Source type dropdown.
4. Select `client_id`
5. Select `client_secret`
6. Select `refresh_token`
7. Click `Set up source`.

## Supported sync modes

The YouTube Analytics source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature               | Supported?  |
| :-------------------- | :---------- |
| Full Refresh Sync     | Yes         |
| Incremental Sync      | Yes         |
| SSL connection        | Yes         |
| Channel Reports       | Yes         |
| Content Owner Reports | Coming soon |
| YouTube Data API      | Coming soon |

## Supported Streams

- [channel_annotations_a1](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#video-annotations)
- [channel_basic_a2](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#video-user-activity)
- [channel_cards_a1](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#video-cards)
- [channel_combined_a2](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#video-combined)
- [channel_demographics_a1](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#video-viewer-demographics)
- [channel_device_os_a2](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#video-device-type-and-operating-system)
- [channel_end_screens_a1](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#video-end-screens)
- [channel_playback_location_a2](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#video-playback-locations)
- [channel_province_a2](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#video-province)
- [channel_sharing_service_a1](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#video-content-sharing)
- [channel_subtitles_a2](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#video-subtitles)
- [channel_traffic_source_a2](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#video-traffic-sources)
- [playlist_basic_a1](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#playlist-user-activity)
- [playlist_combined_a1](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#playlist-combined)
- [playlist_device_os_a1](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#playlist-device-type-and-operating-system)
- [playlist_playback_location_a1](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#playlist-playback-locations)
- [playlist_province_a1](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#playlist-province)
- [playlist_traffic_source_a1](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#playlist-traffic-sources)

## Performance considerations

- Free requests per day: 20,000
- Free requests per 100 seconds: 100
- Free requests per minute: 60

Quota usage is not an issue because data is retrieved once and then filtered, sorted, and queried within the application.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                        |
| :------ | :--------- | :------------------------------------------------------- | :--------------------------------------------- |
| 0.1.4   | 2023-05-22 | [26420](https://github.com/airbytehq/airbyte/pull/26420) | Migrate to advancedAuth                        |
| 0.1.3   | 2022-09-30 | [17454](https://github.com/airbytehq/airbyte/pull/17454) | Added custom backoff logic                     |
| 0.1.2   | 2022-09-29 | [17399](https://github.com/airbytehq/airbyte/pull/17399) | Fixed `403` error while `check connection`     |
| 0.1.1   | 2022-08-18 | [15744](https://github.com/airbytehq/airbyte/pull/15744) | Fix `channel_basic_a2` schema fields data type |
| 0.1.0   | 2021-11-01 | [7407](https://github.com/airbytehq/airbyte/pull/7407)   | Initial Release                                |
