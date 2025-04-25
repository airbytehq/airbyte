# Docuseal
Website: https://docuseal.com/
API Reference: https://www.docuseal.com/docs/api

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your API key for authenticating with the DocuSeal API. Obtain it from the DocuSeal API Console at https://console.docuseal.com/api. |  |
| `start_date` | `string` | Start date.  |  |
| `limit` | `string` | Limit. The pagination limit | 5 |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| submissions | id | DefaultPaginator | ✅ |  ✅  |
| templates | id | DefaultPaginator | ✅ |  ✅  |
| submitters | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.4 | 2025-04-19 | [58316](https://github.com/airbytehq/airbyte/pull/58316) | Update dependencies |
| 0.0.3 | 2025-04-12 | [57831](https://github.com/airbytehq/airbyte/pull/57831) | Update dependencies |
| 0.0.2 | 2025-04-05 | [57272](https://github.com/airbytehq/airbyte/pull/57272) | Update dependencies |
| 0.0.1 | 2025-04-01 | | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
