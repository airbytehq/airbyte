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
| 0.0.15 | 2025-03-08 | [55401](https://github.com/airbytehq/airbyte/pull/55401) | Update dependencies |
| 0.0.14 | 2025-03-01 | [54900](https://github.com/airbytehq/airbyte/pull/54900) | Update dependencies |
| 0.0.13 | 2025-02-22 | [54264](https://github.com/airbytehq/airbyte/pull/54264) | Update dependencies |
| 0.0.12 | 2025-02-15 | [53919](https://github.com/airbytehq/airbyte/pull/53919) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53383](https://github.com/airbytehq/airbyte/pull/53383) | Update dependencies |
| 0.0.10 | 2025-02-01 | [52951](https://github.com/airbytehq/airbyte/pull/52951) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52187](https://github.com/airbytehq/airbyte/pull/52187) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51778](https://github.com/airbytehq/airbyte/pull/51778) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51258](https://github.com/airbytehq/airbyte/pull/51258) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50465](https://github.com/airbytehq/airbyte/pull/50465) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50161](https://github.com/airbytehq/airbyte/pull/50161) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49573](https://github.com/airbytehq/airbyte/pull/49573) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49006](https://github.com/airbytehq/airbyte/pull/49006) | Update dependencies |
| 0.0.2 | 2024-12-11 | [48938](https://github.com/airbytehq/airbyte/pull/48938) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-10-30 | | Initial release by [@natikgadzhi](https://github.com/natikgadzhi) via Connector Builder |

</details>
