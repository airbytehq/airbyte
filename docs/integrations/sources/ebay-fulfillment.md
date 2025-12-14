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
| 0.0.20 | 2025-12-09 | [70581](https://github.com/airbytehq/airbyte/pull/70581) | Update dependencies |
| 0.0.19 | 2025-11-25 | [70173](https://github.com/airbytehq/airbyte/pull/70173) | Update dependencies |
| 0.0.18 | 2025-11-18 | [69422](https://github.com/airbytehq/airbyte/pull/69422) | Update dependencies |
| 0.0.17 | 2025-10-29 | [68728](https://github.com/airbytehq/airbyte/pull/68728) | Update dependencies |
| 0.0.16 | 2025-10-21 | [68559](https://github.com/airbytehq/airbyte/pull/68559) | Update dependencies |
| 0.0.15 | 2025-10-14 | [67770](https://github.com/airbytehq/airbyte/pull/67770) | Update dependencies |
| 0.0.14 | 2025-10-07 | [67287](https://github.com/airbytehq/airbyte/pull/67287) | Update dependencies |
| 0.0.13 | 2025-09-30 | [66286](https://github.com/airbytehq/airbyte/pull/66286) | Update dependencies |
| 0.0.12 | 2025-09-09 | [65799](https://github.com/airbytehq/airbyte/pull/65799) | Update dependencies |
| 0.0.11 | 2025-08-23 | [65266](https://github.com/airbytehq/airbyte/pull/65266) | Update dependencies |
| 0.0.10 | 2025-08-09 | [64791](https://github.com/airbytehq/airbyte/pull/64791) | Update dependencies |
| 0.0.9 | 2025-08-02 | [64329](https://github.com/airbytehq/airbyte/pull/64329) | Update dependencies |
| 0.0.8 | 2025-07-26 | [63952](https://github.com/airbytehq/airbyte/pull/63952) | Update dependencies |
| 0.0.7 | 2025-07-19 | [63550](https://github.com/airbytehq/airbyte/pull/63550) | Update dependencies |
| 0.0.6 | 2025-07-12 | [62999](https://github.com/airbytehq/airbyte/pull/62999) | Update dependencies |
| 0.0.5 | 2025-07-05 | [62792](https://github.com/airbytehq/airbyte/pull/62792) | Update dependencies |
| 0.0.4 | 2025-06-28 | [62324](https://github.com/airbytehq/airbyte/pull/62324) | Update dependencies |
| 0.0.3 | 2025-06-21 | [61940](https://github.com/airbytehq/airbyte/pull/61940) | Update dependencies |
| 0.0.2 | 2025-06-14 | [61250](https://github.com/airbytehq/airbyte/pull/61250) | Update dependencies |
| 0.0.1 | 2025-05-14 | | Initial release by [@adityamohta](https://github.com/adityamohta) via Connector Builder |

</details>
