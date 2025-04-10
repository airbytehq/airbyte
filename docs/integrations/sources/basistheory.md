# BasisTheory
Website: https://portal.basistheory.com/
API Reference: https://developers.basistheory.com/docs/api/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your API key for authenticating with the Basis Theory API. You can find this key when you create an application in the Basis Theory dashboard. |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| applications | id | DefaultPaginator | ✅ |  ✅  |
| application-templates | id | DefaultPaginator | ✅ |  ❌  |
| logs | id | DefaultPaginator | ✅ |  ✅  |
| reactors | id | DefaultPaginator | ✅ |  ✅  |
| tenants | id | DefaultPaginator | ✅ |  ✅  |
| webhooks | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-04-10 | | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
