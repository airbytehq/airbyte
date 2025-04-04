# Dwolla
Website: https://dashboard.dwolla.com/
API Reference: https://developers.dwolla.com/docs

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Client ID.  |  |
| `client_secret` | `string` | Client secret.  |  |
| `environment` | `string` | Environment. The environment for the Dwolla API, either &#39;api-sandbox&#39; or &#39;api&#39;. | api |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| customers | id | DefaultPaginator | ✅ |  ✅  |
| funding_sources | id | DefaultPaginator | ✅ |  ✅  |
| events | id | DefaultPaginator | ✅ |  ✅  |
| exchange_partners | id | DefaultPaginator | ✅ |  ✅  |
| business-classifications | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-04-04 | [57004](https://github.com/airbytehq/airbyte/pull/57004) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
