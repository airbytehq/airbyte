# Ebay Finance
Ebay Finances API Connector

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
| 0.0.1 | 2025-04-01 | | Initial release by [@adityamohta](https://github.com/adityamohta) via Connector Builder |

</details>
