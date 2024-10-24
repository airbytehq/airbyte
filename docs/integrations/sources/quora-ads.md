# Quora Ads
Quora Ads API Connector allows you to sync advertising data between Quora Ads and external platforms, such as analytics tools, CRMs, or marketing dashboards. Quora Ads is a platform that enables businesses to reach relevant audiences through targeted advertising on Quora, helping drive brand awareness, engagement, and conversions. This connector streamlines the process of retrieving key ad performance data, making it easier to monitor campaigns and optimize marketing strategies.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `campaign_id` | `string` | Campaign Id.  |  |
| `ad_sets` | `string` | adsets.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| current_user |  | DefaultPaginator | ✅ |  ❌  |
| accounts | accountId | DefaultPaginator | ✅ |  ❌  |
| leadgenforms |  | DefaultPaginator | ✅ |  ❌  |
| campagins |  | DefaultPaginator | ✅ |  ❌  |
| adsets |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-22 | | Initial release by [@bala-ceg](https://github.com/bala-ceg) via Connector Builder |

</details>
