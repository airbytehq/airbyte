# DBT

DBT Source Connector provides streams with your DBT projects, repositories, users, environments, and runs from DBT Cloud.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key_2` | `string` | DBT API token.  |  |
| `account_id` | `string` | Your DBT account ID.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| `runs` | `id` | DefaultPaginator | ✅ |  ❌  |
| `projects` | `id` | DefaultPaginator | ✅ |  ❌  |
| `repositories` | `id` | DefaultPaginator | ✅ |  ❌  |
| `users` | `id` | DefaultPaginator | ✅ |  ❌  |
| `environments` | `id` | DefaultPaginator | ✅ |  ❌  |


## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.21 | 2025-06-14 | [61190](https://github.com/airbytehq/airbyte/pull/61190) | Update dependencies |
| 0.0.20 | 2025-05-24 | [60364](https://github.com/airbytehq/airbyte/pull/60364) | Update dependencies |
| 0.0.19 | 2025-05-10 | [59951](https://github.com/airbytehq/airbyte/pull/59951) | Update dependencies |
| 0.0.18 | 2025-05-03 | [59432](https://github.com/airbytehq/airbyte/pull/59432) | Update dependencies |
| 0.0.17 | 2025-04-26 | [58848](https://github.com/airbytehq/airbyte/pull/58848) | Update dependencies |
| 0.0.16 | 2025-04-19 | [57768](https://github.com/airbytehq/airbyte/pull/57768) | Update dependencies |
| 0.0.15 | 2025-04-05 | [57224](https://github.com/airbytehq/airbyte/pull/57224) | Update dependencies |
| 0.0.14 | 2025-03-29 | [56540](https://github.com/airbytehq/airbyte/pull/56540) | Update dependencies |
| 0.0.13 | 2025-03-22 | [55990](https://github.com/airbytehq/airbyte/pull/55990) | Update dependencies |
| 0.0.12 | 2025-03-08 | [55323](https://github.com/airbytehq/airbyte/pull/55323) | Update dependencies |
| 0.0.11 | 2025-03-01 | [54959](https://github.com/airbytehq/airbyte/pull/54959) | Update dependencies |
| 0.0.10 | 2025-02-22 | [54390](https://github.com/airbytehq/airbyte/pull/54390) | Update dependencies |
| 0.0.9 | 2025-02-15 | [53775](https://github.com/airbytehq/airbyte/pull/53775) | Update dependencies |
| 0.0.8 | 2025-02-08 | [51624](https://github.com/airbytehq/airbyte/pull/51624) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51086](https://github.com/airbytehq/airbyte/pull/51086) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50556](https://github.com/airbytehq/airbyte/pull/50556) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50035](https://github.com/airbytehq/airbyte/pull/50035) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49499](https://github.com/airbytehq/airbyte/pull/49499) | Update dependencies |
| 0.0.3 | 2024-12-12 | [47748](https://github.com/airbytehq/airbyte/pull/47748) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47460](https://github.com/airbytehq/airbyte/pull/47460) | Update dependencies |
| 0.0.1 | 2024-08-22 | | Initial release by natikgadzhi via Connector Builder |

</details>
