# Jibble
Jibble connector  enables seamless integration between Jibble&#39;s time-tracking data and various data warehouses or tools. It automates data syncs, allowing businesses to analyze employee attendance, productivity, and timesheets efficiently in their preferred analytics platforms.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | OAuth Client ID.  |  |
| `client_secret` | `string` | OAuth Client Secret.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| members | id | DefaultPaginator | ✅ |  ❌  |
| organizations |  | No pagination | ✅ |  ❌  |
| activities |  | No pagination | ✅ |  ❌  |
| schedules |  | No pagination | ✅ |  ❌  |
| groups |  | No pagination | ✅ |  ❌  |
| locations | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-11-08 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
