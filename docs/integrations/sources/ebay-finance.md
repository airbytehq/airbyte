# Ebay Finance
Website: https://www.ebay.com/
Documentation: https://developer.ebay.com/api-docs/sell/finances/overview.html

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `token_refresh_endpoint` | `string` | Refresh Token Endpoint.  | https://api.ebay.com/identity/v1/oauth2/token |
| `client_access_token` | `string` | Access token.  |  |
| `username` | `string` | Username. Ebay Developer Client ID |  |
| `password` | `string` | Password. Ebay Client Secret |  |
| `redirect_uri` | `string` | Redirect URI.  |  |
| `refresh_token` | `string` | Refresh Token.  |  |
| `api_host` | `string` | API Host. https://apiz.sandbox.ebay.com for sandbox &amp; https://apiz.ebay.com for production | https://apiz.ebay.com |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| transactions |  | DefaultPaginator | ✅ |  ✅  |
| payouts | payoutId | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.7 | 2025-05-17 | [60371](https://github.com/airbytehq/airbyte/pull/60371) | Update dependencies |
| 0.0.6 | 2025-05-10 | [59927](https://github.com/airbytehq/airbyte/pull/59927) | Update dependencies |
| 0.0.5 | 2025-05-03 | [58900](https://github.com/airbytehq/airbyte/pull/58900) | Update dependencies |
| 0.0.4 | 2025-04-19 | [58371](https://github.com/airbytehq/airbyte/pull/58371) | Update dependencies |
| 0.0.3 | 2025-04-12 | [57824](https://github.com/airbytehq/airbyte/pull/57824) | Update dependencies |
| 0.0.2 | 2025-04-05 | [57248](https://github.com/airbytehq/airbyte/pull/57248) | Update dependencies |
| 0.0.1 | 2025-04-01 | | Initial release by [@adityamohta](https://github.com/adityamohta) via Connector Builder |

</details>
