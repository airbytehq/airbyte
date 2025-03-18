# Airbyte

This source allows you to sync up data about your Airbyte Cloud workspaces. [Take a look at this guide](https://docs.airbyte.com/using-airbyte/configuring-api-access) to setup API access tokens.
## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | client_id.  |  |
| `start_date` | `string` | Start date.  |  |
| `client_secret` | `string` | client_secret.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Jobs | jobId | DefaultPaginator | ✅ |  ✅  |
| Connections | connectionId | DefaultPaginator | ✅ |  ❌  |
| Workspaces | workspaceId | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.6 | 2025-03-08 | [55365](https://github.com/airbytehq/airbyte/pull/55365) | Update dependencies |
| 0.0.5 | 2025-03-01 | [54841](https://github.com/airbytehq/airbyte/pull/54841) | Update dependencies |
| 0.0.4 | 2025-02-22 | [54269](https://github.com/airbytehq/airbyte/pull/54269) | Update dependencies |
| 0.0.3 | 2025-02-15 | [48905](https://github.com/airbytehq/airbyte/pull/48905) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47572](https://github.com/airbytehq/airbyte/pull/47572) | Update dependencies |
| 0.0.1 | 2024-08-27 | | Initial release by [@johnwasserman](https://github.com/johnwasserman) via Connector Builder |

</details>
