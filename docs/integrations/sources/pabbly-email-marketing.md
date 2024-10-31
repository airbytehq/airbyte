# Pabbly Email Marketing
An Airbyte connector for Pabbly Email Marketing would allow users to sync and transfer email data seamlessly between Pabbly and other platforms, such as data warehouses or BI tools. This connector would enable real-time data extraction for subscriber lists making it easy to automate reporting and integrate Pabbly insights into a broader data ecosystem.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key_2` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| subscriber_list |  | No pagination | ✅ |  ❌  |
| personalization_tags | tag_value | No pagination | ✅ |  ❌  |
| delivery_servers |  | No pagination | ✅ |  ❌  |
| email_templates | template_id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-31 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
