# Ebay Fulfillment
Website: https://www.ebay.com/
Documentation: https://developer.ebay.com/api-docs/sell/fulfillment/overview.html

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `refresh_token_endpoint` | `string` | Refresh Token Endpoint.  | https://api.ebay.com/identity/v1/oauth2/token |
| `api_host` | `string` | API Host.  | https://api.ebay.com |
| `username` | `string` | Username.  |  |
| `password` | `string` | Password.  |  |
| `redirect_uri` | `string` | Redirect URI.  |  |
| `refresh_token` | `string` | Refresh Token.  |  |
| `start_date` | `string` | Start Date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| orders | orderId | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.6 | 2025-07-12 | [62999](https://github.com/airbytehq/airbyte/pull/62999) | Update dependencies |
| 0.0.5 | 2025-07-05 | [62792](https://github.com/airbytehq/airbyte/pull/62792) | Update dependencies |
| 0.0.4 | 2025-06-28 | [62324](https://github.com/airbytehq/airbyte/pull/62324) | Update dependencies |
| 0.0.3 | 2025-06-21 | [61940](https://github.com/airbytehq/airbyte/pull/61940) | Update dependencies |
| 0.0.2 | 2025-06-14 | [61250](https://github.com/airbytehq/airbyte/pull/61250) | Update dependencies |
| 0.0.1 | 2025-05-14 | | Initial release by [@adityamohta](https://github.com/adityamohta) via Connector Builder |

</details>
