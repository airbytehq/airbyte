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
  <summary>
    The Linkrunner Airbyte Source Connector extracts campaign data and attributed user analytics from Linkrunner’s Data API, enabling end-to-end mobile attribution analysis from first click to user attribution events.
    It supports:
    Campaign-level filtering by status (ALL, ACTIVE, INACTIVE)
    Filtering by advertising channels (Google, Meta, TikTok)
    Attributed user data linked to campaigns via parent–child streams
    Time-based attribution windows with timezone support
    Automatic pagination for large datasets
    Reliable full-refresh syncs using Airbyte’s Declarative (low-code) framework
    This connector is ideal for building comprehensive mobile marketing and attribution analytics pipelines in Airbyte.
  </summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.4 | 2026-03-31 | [75709](https://github.com/airbytehq/airbyte/pull/75709) | Update dependencies |
| 0.0.3 | 2026-03-17 | [74997](https://github.com/airbytehq/airbyte/pull/74997) | Update dependencies |
| 0.0.2 | 2026-03-10 | [74423](https://github.com/airbytehq/airbyte/pull/74423) | Update dependencies |
| 0.0.1 | 2026-02-06 | | Initial release by [@ChetanBhosale](https://github.com/ChetanBhosale) via Connector Builder |

</details>
