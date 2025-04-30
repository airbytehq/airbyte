# GRID Esports
http://grid.gg esports data

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start` | `string` | start.  |  |
| `end` | `string` | end.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| series | id | DefaultPaginator | ✅ |  ❌  |
| seriesState | id | No pagination | ✅ |  ❌  |
| SeriesEvents | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-04-30 | | Initial release by [@clarkieryan](https://github.com/clarkieryan) via Connector Builder |

</details>
