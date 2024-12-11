# Brex
Fetches data on users, expenses, transactions, vendors, and budgets from Brex API.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `user_token` | `string` | User Token. User token to authenticate API requests. Generate it from your Brex dashboard under Developer &gt; Settings. |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| transactions | id | DefaultPaginator | ✅ |  ✅  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| departments | id | DefaultPaginator | ✅ |  ❌  |
| vendors | id | DefaultPaginator | ✅ |  ❌  |
| expenses | id | DefaultPaginator | ✅ |  ✅  |
| budgets | budget_id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.2 | 2024-12-11 | [48938](https://github.com/airbytehq/airbyte/pull/48938) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-10-30 | | Initial release by [@natikgadzhi](https://github.com/natikgadzhi) via Connector Builder |

</details>
