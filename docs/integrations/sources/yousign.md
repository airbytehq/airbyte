# YouSign
Website: https://yousign.app/
API Reference: https://developers.yousign.com/reference/oas-specification

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key or access token |  |
| `subdomain` | `string` | Subdomain. The subdomain for the Yousign API environment, such as &#39;sandbox&#39; or &#39;api&#39;. | api |
| `limit` | `string` | Limit. Limit for each response objects | 10 |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| signature_requests | id | DefaultPaginator | ✅ |  ✅  |
| signature_requests_followers | email | DefaultPaginator | ✅ |  ❌  |
| contacts | id | DefaultPaginator | ✅ |  ✅  |
| users | id | DefaultPaginator | ✅ |  ✅  |
| workspaces | id | DefaultPaginator | ✅ |  ✅  |
| electronic_seal_images | id | DefaultPaginator | ✅ |  ✅  |
| templates | id | DefaultPaginator | ✅ |  ✅  |
| labels | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.4 | 2025-04-19 | [58569](https://github.com/airbytehq/airbyte/pull/58569) | Update dependencies |
| 0.0.3 | 2025-04-13 | [58043](https://github.com/airbytehq/airbyte/pull/58043) | Update dependencies |
| 0.0.2 | 2025-04-05 | [57376](https://github.com/airbytehq/airbyte/pull/57376) | Update dependencies |
| 0.0.1 | 2025-04-01 | [56951](https://github.com/airbytehq/airbyte/pull/56951) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
