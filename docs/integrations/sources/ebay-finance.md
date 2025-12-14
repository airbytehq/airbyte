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
| 0.0.24 | 2025-12-09 | [70601](https://github.com/airbytehq/airbyte/pull/70601) | Update dependencies |
| 0.0.23 | 2025-11-25 | [70161](https://github.com/airbytehq/airbyte/pull/70161) | Update dependencies |
| 0.0.22 | 2025-11-18 | [69395](https://github.com/airbytehq/airbyte/pull/69395) | Update dependencies |
| 0.0.21 | 2025-10-29 | [68709](https://github.com/airbytehq/airbyte/pull/68709) | Update dependencies |
| 0.0.20 | 2025-10-21 | [68573](https://github.com/airbytehq/airbyte/pull/68573) | Update dependencies |
| 0.0.19 | 2025-10-14 | [67779](https://github.com/airbytehq/airbyte/pull/67779) | Update dependencies |
| 0.0.18 | 2025-10-07 | [67272](https://github.com/airbytehq/airbyte/pull/67272) | Update dependencies |
| 0.0.17 | 2025-09-30 | [65873](https://github.com/airbytehq/airbyte/pull/65873) | Update dependencies |
| 0.0.16 | 2025-08-23 | [65278](https://github.com/airbytehq/airbyte/pull/65278) | Update dependencies |
| 0.0.15 | 2025-08-09 | [64795](https://github.com/airbytehq/airbyte/pull/64795) | Update dependencies |
| 0.0.14 | 2025-08-02 | [64349](https://github.com/airbytehq/airbyte/pull/64349) | Update dependencies |
| 0.0.13 | 2025-07-26 | [63962](https://github.com/airbytehq/airbyte/pull/63962) | Update dependencies |
| 0.0.12 | 2025-07-19 | [63546](https://github.com/airbytehq/airbyte/pull/63546) | Update dependencies |
| 0.0.11 | 2025-07-12 | [63000](https://github.com/airbytehq/airbyte/pull/63000) | Update dependencies |
| 0.0.10 | 2025-07-05 | [62804](https://github.com/airbytehq/airbyte/pull/62804) | Update dependencies |
| 0.0.9 | 2025-06-28 | [62429](https://github.com/airbytehq/airbyte/pull/62429) | Update dependencies |
| 0.0.8 | 2025-06-22 | [62000](https://github.com/airbytehq/airbyte/pull/62000) | Update dependencies |
| 0.0.7 | 2025-06-14 | [60371](https://github.com/airbytehq/airbyte/pull/60371) | Update dependencies |
| 0.0.6 | 2025-05-10 | [59927](https://github.com/airbytehq/airbyte/pull/59927) | Update dependencies |
| 0.0.5 | 2025-05-03 | [58900](https://github.com/airbytehq/airbyte/pull/58900) | Update dependencies |
| 0.0.4 | 2025-04-19 | [58371](https://github.com/airbytehq/airbyte/pull/58371) | Update dependencies |
| 0.0.3 | 2025-04-12 | [57824](https://github.com/airbytehq/airbyte/pull/57824) | Update dependencies |
| 0.0.2 | 2025-04-05 | [57248](https://github.com/airbytehq/airbyte/pull/57248) | Update dependencies |
| 0.0.1 | 2025-04-01 | | Initial release by [@adityamohta](https://github.com/adityamohta) via Connector Builder |

</details>
