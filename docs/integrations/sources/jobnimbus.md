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
| 0.0.15 | 2025-03-08 | [55453](https://github.com/airbytehq/airbyte/pull/55453) | Update dependencies |
| 0.0.14 | 2025-03-01 | [54819](https://github.com/airbytehq/airbyte/pull/54819) | Update dependencies |
| 0.0.13 | 2025-02-22 | [54302](https://github.com/airbytehq/airbyte/pull/54302) | Update dependencies |
| 0.0.12 | 2025-02-15 | [53819](https://github.com/airbytehq/airbyte/pull/53819) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53261](https://github.com/airbytehq/airbyte/pull/53261) | Update dependencies |
| 0.0.10 | 2025-02-01 | [52769](https://github.com/airbytehq/airbyte/pull/52769) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52235](https://github.com/airbytehq/airbyte/pull/52235) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51817](https://github.com/airbytehq/airbyte/pull/51817) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51192](https://github.com/airbytehq/airbyte/pull/51192) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50661](https://github.com/airbytehq/airbyte/pull/50661) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50145](https://github.com/airbytehq/airbyte/pull/50145) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49610](https://github.com/airbytehq/airbyte/pull/49610) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49239](https://github.com/airbytehq/airbyte/pull/49239) | Update dependencies |
| 0.0.2 | 2024-12-11 | [48919](https://github.com/airbytehq/airbyte/pull/48919) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-10-29 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
