# SimpleCast
Say hello to the modern end-to-end podcasting platform. Simplecast remains the easiest way to get audio out to the world—with one-click publishing to Apple Podcasts Apple Podcasts , Spotify Spotify, or wherever your audience listens—and the best way for podcasters to cash in on their content.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_token` | `string` | API Token. API token to use. Find it at your Private Apps page on the Simplecast dashboard. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| podcasts | id | DefaultPaginator | ✅ |  ❌  |
| episodes | id | DefaultPaginator | ✅ |  ❌  |
| analytics |  | DefaultPaginator | ✅ |  ❌  |
| analytics_downloads | id | No pagination | ✅ |  ❌  |
| analytics_podcasts_listeners | id | No pagination | ✅ |  ❌  |
| categories |  | DefaultPaginator | ✅ |  ❌  |
| distribution_channels |  | DefaultPaginator | ✅ |  ❌  |
| timezones | value | No pagination | ✅ |  ❌  |
| analytics_episodes | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-03 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
