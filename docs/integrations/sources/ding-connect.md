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
| 0.0.21 | 2025-10-29 | [69007](https://github.com/airbytehq/airbyte/pull/69007) | Update dependencies |
| 0.0.20 | 2025-09-30 | [66948](https://github.com/airbytehq/airbyte/pull/66948) | Update dependencies |
| 0.0.19 | 2025-09-09 | [65838](https://github.com/airbytehq/airbyte/pull/65838) | Update dependencies |
| 0.0.18 | 2025-08-23 | [65298](https://github.com/airbytehq/airbyte/pull/65298) | Update dependencies |
| 0.0.17 | 2025-08-09 | [64763](https://github.com/airbytehq/airbyte/pull/64763) | Update dependencies |
| 0.0.16 | 2025-08-02 | [64382](https://github.com/airbytehq/airbyte/pull/64382) | Update dependencies |
| 0.0.15 | 2025-07-26 | [63954](https://github.com/airbytehq/airbyte/pull/63954) | Update dependencies |
| 0.0.14 | 2025-07-19 | [63585](https://github.com/airbytehq/airbyte/pull/63585) | Update dependencies |
| 0.0.13 | 2025-07-12 | [63013](https://github.com/airbytehq/airbyte/pull/63013) | Update dependencies |
| 0.0.12 | 2025-07-05 | [62789](https://github.com/airbytehq/airbyte/pull/62789) | Update dependencies |
| 0.0.11 | 2025-06-28 | [62315](https://github.com/airbytehq/airbyte/pull/62315) | Update dependencies |
| 0.0.10 | 2025-06-21 | [61983](https://github.com/airbytehq/airbyte/pull/61983) | Update dependencies |
| 0.0.9 | 2025-06-14 | [61173](https://github.com/airbytehq/airbyte/pull/61173) | Update dependencies |
| 0.0.8 | 2025-05-24 | [60411](https://github.com/airbytehq/airbyte/pull/60411) | Update dependencies |
| 0.0.7 | 2025-05-10 | [60028](https://github.com/airbytehq/airbyte/pull/60028) | Update dependencies |
| 0.0.6 | 2025-05-03 | [59380](https://github.com/airbytehq/airbyte/pull/59380) | Update dependencies |
| 0.0.5 | 2025-04-26 | [58874](https://github.com/airbytehq/airbyte/pull/58874) | Update dependencies |
| 0.0.4 | 2025-04-19 | [58321](https://github.com/airbytehq/airbyte/pull/58321) | Update dependencies |
| 0.0.3 | 2025-04-12 | [57842](https://github.com/airbytehq/airbyte/pull/57842) | Update dependencies |
| 0.0.2 | 2025-04-05 | [57191](https://github.com/airbytehq/airbyte/pull/57191) | Update dependencies |
| 0.0.1 | 2025-04-03 | [56995](https://github.com/airbytehq/airbyte/pull/56995) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
