# Phyllo
Website: https://dashboard.getphyllo.com/
API Reference: https://docs.getphyllo.com/docs/api-reference/introduction/introduction

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Client ID. Your Client ID for the Phyllo API. You can find this in the Phyllo Developer Dashboard under API credentials. |  |
| `environment` | `string` | Environment. The environment for the API (e.g., &#39;api.sandbox&#39;, &#39;api.staging&#39;, &#39;api&#39;) | api |
| `client_secret` | `string` | Client Secret. Your Client Secret for the Phyllo API. You can find this in the Phyllo Developer Dashboard under API credentials. |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| work-platforms | id | DefaultPaginator | ✅ |  ✅  |
| users | id | DefaultPaginator | ✅ |  ✅  |
| accounts | id | DefaultPaginator | ✅ |  ✅  |
| profiles | id | DefaultPaginator | ✅ |  ✅  |
| content_items | id | DefaultPaginator | ✅ |  ✅  |
| social_income_transactions | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-04-04 | [57012](https://github.com/airbytehq/airbyte/pull/57012) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
