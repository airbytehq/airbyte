# Eventzilla
The Airbyte connector for Eventzilla enables seamless integration between Eventzilla and various data destinations. It automates the extraction of event management data, such as attendee details, ticket sales, and event performance metrics, and syncs it with your preferred data warehouses or analytics tools. This connector helps organizations centralize and analyze their Eventzilla data for reporting, monitoring, and strategic insights.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `x-api-key` | `string` | API Key. API key to use. Generate it by creating a new application within your Eventzilla account settings under Settings &gt; App Management. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| events | id | DefaultPaginator | ✅ |  ❌  |
| attendees | id | DefaultPaginator | ✅ |  ❌  |
| categories |  | DefaultPaginator | ✅ |  ❌  |
| tickets | id | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| transactions | refno | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.9 | 2025-02-01 | [52840](https://github.com/airbytehq/airbyte/pull/52840) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52334](https://github.com/airbytehq/airbyte/pull/52334) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51675](https://github.com/airbytehq/airbyte/pull/51675) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51083](https://github.com/airbytehq/airbyte/pull/51083) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50549](https://github.com/airbytehq/airbyte/pull/50549) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50047](https://github.com/airbytehq/airbyte/pull/50047) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49488](https://github.com/airbytehq/airbyte/pull/49488) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49198](https://github.com/airbytehq/airbyte/pull/49198) | Update dependencies |
| 0.0.1 | 2024-10-23 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
