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
| 0.0.4 | 2024-12-14 | [49756](https://github.com/airbytehq/airbyte/pull/49756) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49403](https://github.com/airbytehq/airbyte/pull/49403) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49125](https://github.com/airbytehq/airbyte/pull/49125) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-11-08 | | Initial release by [@bala-ceg](https://github.com/bala-ceg) via Connector Builder |

</details>
