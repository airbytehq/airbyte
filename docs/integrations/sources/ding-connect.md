# Ding Connect
Website: https://www.dingconnect.com/
API Reference: https://www.dingconnect.com/Api/Description

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your API key for authenticating with the DingConnect API. You can generate this key by navigating to the Developer tab in the Account Settings section of your DingConnect account. |  |
| `X-Correlation-Id` | `string` | X-Correlation-Id. Optional header to correlate HTTP requests between a client and server. |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name                 | Primary Key | Pagination        | Supports Full Sync | Supports Incremental |
|-----------------------------|-------------|-------------------|---------------------|----------------------|
| countries                   | uuid        | DefaultPaginator  | ✅                  | ❌                  |
| currencies                  | uuid        | DefaultPaginator  | ✅                  | ❌                  |
| error_code_descriptions     | uuid        | DefaultPaginator  | ✅                  | ❌                  |
| product_descriptions        | uuid        | DefaultPaginator  | ✅                  | ❌                  |
| products                    | uuid        | DefaultPaginator  | ✅                  | ❌                  |
| promotions                  | uuid        | DefaultPaginator  | ✅                  | ✅                  |
| providers                   | uuid        | DefaultPaginator  | ✅                  | ❌                  |
| regions                     | uuid        | DefaultPaginator  | ✅                  | ❌                  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.3 | 2025-04-12 | [57842](https://github.com/airbytehq/airbyte/pull/57842) | Update dependencies |
| 0.0.2 | 2025-04-05 | [57191](https://github.com/airbytehq/airbyte/pull/57191) | Update dependencies |
| 0.0.1 | 2025-04-03 | [56995](https://github.com/airbytehq/airbyte/pull/56995) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
