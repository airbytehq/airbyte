# GetGist
An Airbyte connector for [Gist](https://getgist.com/) would enable data syncing between Gist and various data platforms or databases. This connector could pull data from key objects like contacts, tags, segments, campaigns, forms, and subscription types, facilitating integration with other tools in a data pipeline. By automating data extraction from Gist, users can analyze customer interactions and engagement more efficiently in their preferred analytics or storage environment.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use. Find it in the Integration Settings on your Gist dashboard at https://app.getgist.com/projects/_/settings/api-key. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| contacts | id | DefaultPaginator | ✅ |  ❌  |
| collections | id | DefaultPaginator | ✅ |  ❌  |
| tags | id | DefaultPaginator | ✅ |  ❌  |
| segments | id | DefaultPaginator | ✅ |  ❌  |
| forms | id | DefaultPaginator | ✅ |  ❌  |
| campaigns | id | DefaultPaginator | ✅ |  ❌  |
| subscription_types | id | DefaultPaginator | ✅ |  ❌  |
| teams | id | DefaultPaginator | ✅ |  ❌  |
| teammates | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.10 | 2025-02-01 | [52830](https://github.com/airbytehq/airbyte/pull/52830) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52331](https://github.com/airbytehq/airbyte/pull/52331) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51653](https://github.com/airbytehq/airbyte/pull/51653) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51085](https://github.com/airbytehq/airbyte/pull/51085) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50512](https://github.com/airbytehq/airbyte/pull/50512) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50018](https://github.com/airbytehq/airbyte/pull/50018) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49532](https://github.com/airbytehq/airbyte/pull/49532) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49192](https://github.com/airbytehq/airbyte/pull/49192) | Update dependencies |
| 0.0.2 | 2024-12-11 | [48908](https://github.com/airbytehq/airbyte/pull/48908) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-10-31 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
