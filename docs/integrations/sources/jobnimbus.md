# JobNimbus
The JobNimbus Airbyte connector enables seamless integration between JobNimbus, a popular CRM and project management tool, and your data pipeline. This connector allows you to automatically sync data from JobNimbus, including contacts records, task information, and more, into your preferred destination. It simplifies data extraction and helps you streamline workflows, enabling efficient analysis and reporting for enhanced business insights.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use. Find it by logging into your JobNimbus account, navigating to settings, and creating a new API key under the API section. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| jobs | jnid | DefaultPaginator | ✅ |  ❌  |
| contacts | jnid | DefaultPaginator | ✅ |  ❌  |
| tasks | jnid | DefaultPaginator | ✅ |  ❌  |
| activities | jnid | DefaultPaginator | ✅ |  ❌  |
| files | jnid | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-29 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
