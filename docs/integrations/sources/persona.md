# Persona
Airbyte connector for [Persona](https://withpersona.com) that makes it easy to move and manage your identity verification data between platforms. This connector helps you seamlessly sync your data from Persona, simplifying workflows and ensuring your identity-related tasks are more efficient.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key or access token |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| accounts | id | DefaultPaginator | ✅ |  ❌  |
| cases | id | DefaultPaginator | ✅ |  ❌  |
| api-keys | id | DefaultPaginator | ✅ |  ❌  |
| api-logs | id | DefaultPaginator | ✅ |  ❌  |
| events | id | DefaultPaginator | ✅ |  ❌  |
| inquiries | id | DefaultPaginator | ✅ |  ❌  |
| inquiry-sessions | id | DefaultPaginator | ✅ |  ❌  |
| workflows-run | id | DefaultPaginator | ✅ |  ❌  |
| webhooks | id | DefaultPaginator | ✅ |  ❌  |
| workflow-runs | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.16 | 2025-03-08 | [55529](https://github.com/airbytehq/airbyte/pull/55529) | Update dependencies |
| 0.0.15 | 2025-03-01 | [55021](https://github.com/airbytehq/airbyte/pull/55021) | Update dependencies |
| 0.0.14 | 2025-02-23 | [54566](https://github.com/airbytehq/airbyte/pull/54566) | Update dependencies |
| 0.0.13 | 2025-02-15 | [53945](https://github.com/airbytehq/airbyte/pull/53945) | Update dependencies |
| 0.0.12 | 2025-02-08 | [53503](https://github.com/airbytehq/airbyte/pull/53503) | Update dependencies |
| 0.0.11 | 2025-02-01 | [52983](https://github.com/airbytehq/airbyte/pull/52983) | Update dependencies |
| 0.0.10 | 2025-01-25 | [52471](https://github.com/airbytehq/airbyte/pull/52471) | Update dependencies |
| 0.0.9 | 2025-01-18 | [51917](https://github.com/airbytehq/airbyte/pull/51917) | Update dependencies |
| 0.0.8 | 2025-01-11 | [51331](https://github.com/airbytehq/airbyte/pull/51331) | Update dependencies |
| 0.0.7 | 2024-12-28 | [50696](https://github.com/airbytehq/airbyte/pull/50696) | Update dependencies |
| 0.0.6 | 2024-12-21 | [50257](https://github.com/airbytehq/airbyte/pull/50257) | Update dependencies |
| 0.0.5 | 2024-12-14 | [49663](https://github.com/airbytehq/airbyte/pull/49663) | Update dependencies |
| 0.0.4 | 2024-12-12 | [49069](https://github.com/airbytehq/airbyte/pull/49069) | Update dependencies |
| 0.0.3 | 2024-11-04 | [48247](https://github.com/airbytehq/airbyte/pull/48247) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47498](https://github.com/airbytehq/airbyte/pull/47498) | Update dependencies |
| 0.0.1 | 2024-10-03 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
