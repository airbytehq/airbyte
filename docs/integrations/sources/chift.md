# Chift
Chift is a tool that allows for the integration of financial data into SaaS products.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Client Id.  |  |
| `account_id` | `string` | Account Id.  |  |
| `client_secret` | `string` | Client Secret.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| consumers | consumerid | No pagination | ✅ |  ❌  |
| connections | connectionid | No pagination | ✅ |  ❌  |
| syncs |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.2 | 2025-12-16 | [70944](https://github.com/airbytehq/airbyte/pull/70944) | Update dependencies |
| 0.0.1 | 2025-10-13 | | Initial release by [@FVidalCarneiro](https://github.com/FVidalCarneiro) via Connector Builder |

</details>
