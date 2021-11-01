# YouTube Analytics

## Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| Replicate Incremental Deletes | No |
| SSL connection | Yes |
| Channel Reports | Yes |
| Content Owner Reports | No |
| YouTube Data API | No |

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


## Rate Limits & Performance Considerations \(Airbyte Open-Source\)

* Free requests per day: 20,000
* Free requests per 100 seconds: 100
* Free requests per minute: 60

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.0 | 2021-11-01 | [7407](https://github.com/airbytehq/airbyte/pull/7407) | Initial Release |
