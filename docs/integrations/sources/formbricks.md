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
| 0.0.23 | 2025-06-14 | [61219](https://github.com/airbytehq/airbyte/pull/61219) | Update dependencies |
| 0.0.22 | 2025-05-24 | [60384](https://github.com/airbytehq/airbyte/pull/60384) | Update dependencies |
| 0.0.21 | 2025-05-10 | [59998](https://github.com/airbytehq/airbyte/pull/59998) | Update dependencies |
| 0.0.20 | 2025-05-03 | [59431](https://github.com/airbytehq/airbyte/pull/59431) | Update dependencies |
| 0.0.19 | 2025-04-26 | [58872](https://github.com/airbytehq/airbyte/pull/58872) | Update dependencies |
| 0.0.18 | 2025-04-19 | [57815](https://github.com/airbytehq/airbyte/pull/57815) | Update dependencies |
| 0.0.17 | 2025-04-05 | [57212](https://github.com/airbytehq/airbyte/pull/57212) | Update dependencies |
| 0.0.16 | 2025-03-29 | [56495](https://github.com/airbytehq/airbyte/pull/56495) | Update dependencies |
| 0.0.15 | 2025-03-22 | [55931](https://github.com/airbytehq/airbyte/pull/55931) | Update dependencies |
| 0.0.14 | 2025-03-08 | [55310](https://github.com/airbytehq/airbyte/pull/55310) | Update dependencies |
| 0.0.13 | 2025-03-01 | [54918](https://github.com/airbytehq/airbyte/pull/54918) | Update dependencies |
| 0.0.12 | 2025-02-22 | [54391](https://github.com/airbytehq/airbyte/pull/54391) | Update dependencies |
| 0.0.11 | 2025-02-15 | [53723](https://github.com/airbytehq/airbyte/pull/53723) | Update dependencies |
| 0.0.10 | 2025-02-08 | [53345](https://github.com/airbytehq/airbyte/pull/53345) | Update dependencies |
| 0.0.9 | 2025-02-01 | [52871](https://github.com/airbytehq/airbyte/pull/52871) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52348](https://github.com/airbytehq/airbyte/pull/52348) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51678](https://github.com/airbytehq/airbyte/pull/51678) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51091](https://github.com/airbytehq/airbyte/pull/51091) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50548](https://github.com/airbytehq/airbyte/pull/50548) | Update dependencies |
| 0.0.4 | 2024-12-21 | [49993](https://github.com/airbytehq/airbyte/pull/49993) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49525](https://github.com/airbytehq/airbyte/pull/49525) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49167](https://github.com/airbytehq/airbyte/pull/49167) | Update dependencies |
| 0.0.1 | 2024-11-08 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
