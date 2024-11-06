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
| 0.0.3 | 2024-11-04 | [48247](https://github.com/airbytehq/airbyte/pull/48247) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47498](https://github.com/airbytehq/airbyte/pull/47498) | Update dependencies |
| 0.0.1 | 2024-10-03 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
