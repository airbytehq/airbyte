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
| 0.0.1 | 2024-11-08 | | Initial release by [@bala-ceg](https://github.com/bala-ceg) via Connector Builder |

</details>
