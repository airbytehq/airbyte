# referralhero
airbyte connector developed using airbyte 1.0 UI Connector development

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| lists | uuid | DefaultPaginator | ✅ |  ❌  |
| leaderboard |  | DefaultPaginator | ✅ |  ❌  |
| bonuses |  | DefaultPaginator | ✅ |  ❌  |
| subscribers | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-07 | | Initial release by [@bala-ceg](https://github.com/bala-ceg) via Connector Builder |

</details>
