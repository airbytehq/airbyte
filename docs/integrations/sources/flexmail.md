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
| 0.0.1 | 2024-11-08 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
