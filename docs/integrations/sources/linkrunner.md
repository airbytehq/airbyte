# Linkrunner
Linkrunner is a Mobile Measurement Partner (MMP) that helps track user journeys from first click to revenue generation. This connector extracts campaign data and attributed user analytics from Linkrunner&#39;s Data API, enabling comprehensive mobile attribution reporting and analysis. Supports filtering by campaign status, advertising channels (Google, Meta, TikTok), and time-based attribution data with automatic pagination and parent-child stream relationships.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `linkrunner-key` | `string` | LinkRunner API Key. Your LinkRunner API key for authentication. Find this in your LinkRunner dashboard. |  |
| `filter` | `string` | Campaign Filter. Filter campaigns by status (ALL, ACTIVE, or INACTIVE) | ALL |
| `channel` | `string` | Channel Filter. Filter campaigns by marketing channel (leave empty for all channels) |  |
| `start_timestamp` | `string` | Start Date. Start date for fetching attributed users in ISO 8601 format (e.g., 2024-01-01T00:00:00Z) |  |
| `end_timestamp` | `string` | End Date. End date for fetching attributed users in ISO 8601 format. Leave empty for current date. |  |
| `timezone` | `string` | Timezone. Timezone for date filtering (default is UTC) | UTC |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| campaigns | display_id | DefaultPaginator | ✅ |  ❌  |
| attributed_users |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-02-06 | | Initial release by [@ChetanBhosale](https://github.com/ChetanBhosale) via Connector Builder |

</details>
