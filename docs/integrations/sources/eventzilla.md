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
| 0.0.1 | 2024-10-23 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
