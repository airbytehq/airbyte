# Formbricks
The Airbyte connector for [Formbricks](https://www.formbricks.com/) enables seamless data integration by pulling customer feedback and form data from Formbricks directly into your data warehouse. This connector allows you to automate data syncing for enhanced analytics, providing valuable insights into user behavior and satisfaction across platforms.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use. You can generate and find it in your Postman account settings. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| surveys | id | No pagination | ✅ |  ❌  |
| action_classes | id | No pagination | ✅ |  ❌  |
| attribute_classes | id | No pagination | ✅ |  ❌  |
| identified_peoples | id | No pagination | ✅ |  ❌  |
| responses | id | DefaultPaginator | ✅ |  ❌  |
| webhooks | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.3 | 2024-12-14 | [49525](https://github.com/airbytehq/airbyte/pull/49525) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49167](https://github.com/airbytehq/airbyte/pull/49167) | Update dependencies |
| 0.0.1 | 2024-11-08 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
