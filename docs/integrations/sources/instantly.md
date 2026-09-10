# Instantly
instantly.ai Campaigns Data API

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | start_date. Start Date |  |
| `end_date` | `string` | end_date. End Date |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| campaign(s) analytics | campaign_id | No pagination | ✅ |  ❌  |
| Campaigns Analytics Daily |  | No pagination | ✅ |  ❌  |
| Campaigns |  | DefaultPaginator | ✅ |  ❌  |
| Accounts |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-06-04 | | Initial release by [@mhassaanmughal](https://github.com/mhassaanmughal) via Connector Builder |

</details>
