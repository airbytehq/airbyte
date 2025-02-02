# Flexmail
The Airbyte connector for [Flexmail](https://flexmail.be/) enables seamless data integration from Flexmail, a comprehensive email marketing platform, into various data warehouses and analytics tools. With this connector, users can efficiently synchronize Flexmail data—such as campaign details, subscriber information, and engagement metrics—allowing for unified insights and advanced reporting across platforms. Perfect for businesses aiming to centralize their marketing data for enhanced visibility and decision-making.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `account_id` | `string` | Account ID. Your Flexmail account ID. You can find it in your Flexmail account settings. |  |
| `personal_access_token` | `string` | Personal Access Token. A personal access token for API authentication. Manage your tokens in Flexmail under Settings &gt; API &gt; Personal access tokens. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| contacts | id | DefaultPaginator | ✅ |  ❌  |
| custom_fields | id | No pagination | ✅ |  ❌  |
| interests | id | No pagination | ✅ |  ❌  |
| segments | id | No pagination | ✅ |  ❌  |
| sources | id | DefaultPaginator | ✅ |  ❌  |
| webhook_events |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.8 | 2025-02-01 | [52859](https://github.com/airbytehq/airbyte/pull/52859) | Update dependencies |
| 0.0.7 | 2025-01-25 | [51702](https://github.com/airbytehq/airbyte/pull/51702) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51093](https://github.com/airbytehq/airbyte/pull/51093) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50534](https://github.com/airbytehq/airbyte/pull/50534) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50059](https://github.com/airbytehq/airbyte/pull/50059) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49492](https://github.com/airbytehq/airbyte/pull/49492) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49199](https://github.com/airbytehq/airbyte/pull/49199) | Update dependencies |
| 0.0.1 | 2024-11-08 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
