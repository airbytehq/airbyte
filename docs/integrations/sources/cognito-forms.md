# Cognito Forms
The Airbyte connector for Cognito Forms enables seamless data integration between Cognito Forms and various data destinations. With this connector, users can automatically extract form and form schema from Cognito Forms and sync it to data warehouses, or other tools in real-time. 

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API access token to use. You can create and find it in your Cognito Forms account under Settings &gt; Integrations. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| forms | Id | No pagination | ✅ |  ❌  |
| form_schemas |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-31 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
