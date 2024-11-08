# Youtube Data
Youtube Data

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `video_id` | `string` | video_id.  |  |
| `channel_id` | `string` | channel_id.  |  |
| `region_code` | `string` | region_code.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| video |  | DefaultPaginator | ✅ |  ❌  |
| channels | id | DefaultPaginator | ✅ |  ❌  |
| comments |  | DefaultPaginator | ✅ |  ❌  |
| popularvideos | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-11-08 | | Initial release by [@bala-ceg](https://github.com/bala-ceg) via Connector Builder |

</details>
