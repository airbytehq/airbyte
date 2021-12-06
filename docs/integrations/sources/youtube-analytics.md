# YouTube Analytics

YouTube Analytics connector supports [YouTube Analytics Bulk Reports](https://developers.google.com/youtube/reporting/v1/reports). It retrieves bulk reports containing YouTube Analytics data for a [channel](https://developers.google.com/youtube/reporting/v1/reports/channel_reports) or [content owner](https://developers.google.com/youtube/reporting/v1/reports/content_owner_reports).

## Sync overview

YouTube does not start to generate a report until you create a [reporting job](https://developers.google.com/youtube/reporting/v1/reports#step-3:-create-a-reporting-job) for that report. Airbyte creates a reporting job for your report or uses current reporting job if it's already exists. The report will be available within 48 hours of creating the reporting job and will be for the day that the job was scheduled. For example, if you schedule a job on September 1, 2015, then the report for September 1, 2015, will be ready on September 3, 2015. The report for September 2, 2015, will be posted on September 4, 2015, and so forth. Youtube also generates historical data reports covering the 30-day period prior to when you created the job. Airbyte syncs all available historical data too.

## Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| SSL connection | Yes |
| Channel Reports | Yes |
| Content Owner Reports | Coming soon |
| YouTube Data API | Coming soon |

### Supported Reports

This source is capable of syncing the following reports and their data:

* [channel_annotations_a1](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#video-annotations)
* [channel_basic_a2](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#video-user-activity)
* [channel_cards_a1](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#video-cards)
* [channel_combined_a2](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#video-combined)
* [channel_demographics_a1](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#video-viewer-demographics)
* [channel_device_os_a2](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#video-device-type-and-operating-system)
* [channel_end_screens_a1](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#video-end-screens)
* [channel_playback_location_a2](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#video-playback-locations)
* [channel_province_a2](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#video-province)
* [channel_sharing_service_a1](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#video-content-sharing)
* [channel_subtitles_a2](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#video-subtitles)
* [channel_traffic_source_a2](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#video-traffic-sources)
* [playlist_basic_a1](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#playlist-user-activity)
* [playlist_combined_a1](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#playlist-combined)
* [playlist_device_os_a1](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#playlist-device-type-and-operating-system)
* [playlist_playback_location_a1](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#playlist-playback-locations)
* [playlist_province_a1](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#playlist-province)
* [playlist_traffic_source_a1](https://developers.google.com/youtube/reporting/v1/reports/channel_reports#playlist-traffic-sources)

## Getting Started

* Go to the [YouTube Reporting API dashboard](https://console.cloud.google.com/apis/api/youtubereporting.googleapis.com/overview) in the project for your service user. Enable the API for your account.
* Use your Google account and authorize over Google's OAuth 2.0 on connection setup. Please make sure to grant the following [authorization scope](https://developers.google.com/youtube/reporting/v1/reports#step-1:-retrieve-authorization-credentials): `https://www.googleapis.com/auth/yt-analytics.readonly`.

## Rate Limits & Performance Considerations \(Airbyte Open-Source\)

* Free requests per day: 20,000
* Free requests per 100 seconds: 100
* Free requests per minute: 60

Quota usage is not an issue because data is retrieved once and then filtered, sorted, and queried within the application.

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.0 | 2021-11-01 | [7407](https://github.com/airbytehq/airbyte/pull/7407) | Initial Release |
