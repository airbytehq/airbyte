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
| 0.1.6 | 2025-05-17 | [60611](https://github.com/airbytehq/airbyte/pull/60611) | Update dependencies |
| 0.1.5 | 2025-05-10 | [59852](https://github.com/airbytehq/airbyte/pull/59852) | Update dependencies |
| 0.1.4 | 2025-05-03 | [59370](https://github.com/airbytehq/airbyte/pull/59370) | Update dependencies |
| 0.1.3 | 2025-04-26 | [58721](https://github.com/airbytehq/airbyte/pull/58721) | Update dependencies |
| 0.1.2 | 2025-04-19 | [58276](https://github.com/airbytehq/airbyte/pull/58276) | Update dependencies |
| 0.1.1 | 2025-04-12 | [57637](https://github.com/airbytehq/airbyte/pull/57637) | Update dependencies |
| 0.1.0 | 2025-04-08 | [57518](https://github.com/airbytehq/airbyte/pull/57518) | Fixed jobs incremental syncing by filtering out null updatedAt records |
| 0.0.9 | 2025-04-05 | [57155](https://github.com/airbytehq/airbyte/pull/57155) | Update dependencies |
| 0.0.8 | 2025-03-29 | [56560](https://github.com/airbytehq/airbyte/pull/56560) | Update dependencies |
| 0.0.7 | 2025-03-22 | [56130](https://github.com/airbytehq/airbyte/pull/56130) | Update dependencies |
| 0.0.6 | 2025-03-08 | [55365](https://github.com/airbytehq/airbyte/pull/55365) | Update dependencies |
| 0.0.5 | 2025-03-01 | [54841](https://github.com/airbytehq/airbyte/pull/54841) | Update dependencies |
| 0.0.4 | 2025-02-22 | [54269](https://github.com/airbytehq/airbyte/pull/54269) | Update dependencies |
| 0.0.3 | 2025-02-15 | [48905](https://github.com/airbytehq/airbyte/pull/48905) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47572](https://github.com/airbytehq/airbyte/pull/47572) | Update dependencies |
| 0.0.1 | 2024-08-27 | | Initial release by [@johnwasserman](https://github.com/johnwasserman) via Connector Builder |

</details>
