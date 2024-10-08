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
| 0.0.1 | 2024-08-27 | | Initial release by [@johnwasserman](https://github.com/johnwasserman) via Connector Builder |

</details>