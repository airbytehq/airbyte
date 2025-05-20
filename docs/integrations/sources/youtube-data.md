# Youtube Data API
The YouTube Data API v3 is an API that provides access to YouTube data, such as videos, playlists, channels, comments and simple stats.
This is a simpler version of Youtube connector, if you need more detailed reports from your channel please check
the [Youtube Analytics Connector](https://docs.airbyte.com/integrations/sources/youtube-analytics)


## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `channel_id` | `string` | channel_id.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| videos |  | DefaultPaginator | ✅ |  ❌  |
| video_details |  | DefaultPaginator | ✅ |  ❌  |
| channels | id | DefaultPaginator | ✅ |  ❌  |
| comments |  | DefaultPaginator | ✅ |  ❌  |
| channel_comments | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.21 | 2025-05-10 | [59968](https://github.com/airbytehq/airbyte/pull/59968) | Update dependencies |
| 0.0.20 | 2025-05-04 | [59566](https://github.com/airbytehq/airbyte/pull/59566) | Update dependencies |
| 0.0.19 | 2025-04-26 | [58930](https://github.com/airbytehq/airbyte/pull/58930) | Update dependencies |
| 0.0.18 | 2025-04-19 | [58550](https://github.com/airbytehq/airbyte/pull/58550) | Update dependencies |
| 0.0.17 | 2025-04-13 | [58052](https://github.com/airbytehq/airbyte/pull/58052) | Update dependencies |
| 0.0.16 | 2025-04-05 | [57379](https://github.com/airbytehq/airbyte/pull/57379) | Update dependencies |
| 0.0.15 | 2025-03-29 | [56821](https://github.com/airbytehq/airbyte/pull/56821) | Update dependencies |
| 0.0.14 | 2025-03-22 | [56338](https://github.com/airbytehq/airbyte/pull/56338) | Update dependencies |
| 0.0.13 | 2025-03-09 | [55664](https://github.com/airbytehq/airbyte/pull/55664) | Update dependencies |
| 0.0.12 | 2025-03-01 | [55162](https://github.com/airbytehq/airbyte/pull/55162) | Update dependencies |
| 0.0.11 | 2025-02-23 | [54632](https://github.com/airbytehq/airbyte/pull/54632) | Update dependencies |
| 0.0.10 | 2025-02-15 | [53087](https://github.com/airbytehq/airbyte/pull/53087) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52387](https://github.com/airbytehq/airbyte/pull/52387) | Update dependencies |
| 0.0.8 | 2025-01-18 | [52006](https://github.com/airbytehq/airbyte/pull/52006) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51380](https://github.com/airbytehq/airbyte/pull/51380) | Update dependencies |
| 0.0.6 | 2025-01-04 | [50753](https://github.com/airbytehq/airbyte/pull/50753) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50326](https://github.com/airbytehq/airbyte/pull/50326) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49756](https://github.com/airbytehq/airbyte/pull/49756) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49403](https://github.com/airbytehq/airbyte/pull/49403) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49125](https://github.com/airbytehq/airbyte/pull/49125) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-11-08 | | Initial release by [@bala-ceg](https://github.com/bala-ceg) via Connector Builder |

</details>
