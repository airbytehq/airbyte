# Linear

An Airbyte connector for Linear.app.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| teams | id | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| cycles | id | DefaultPaginator | ✅ |  ❌  |
| issues | id | DefaultPaginator | ✅ |  ❌  |
| comments | id | DefaultPaginator | ✅ |  ❌  |
| projects | id | DefaultPaginator | ✅ |  ❌  |
| customers | id | DefaultPaginator | ✅ |  ❌  |
| attachments | id | DefaultPaginator | ✅ |  ❌  |
| issue_labels | id | DefaultPaginator | ✅ |  ❌  |
| customer_needs | id | DefaultPaginator | ✅ |  ❌  |
| customer_tiers | id | DefaultPaginator | ✅ |  ❌  |
| issue_relations | id | DefaultPaginator | ✅ |  ❌  |
| workflow_states | id | DefaultPaginator | ✅ |  ❌  |
| project_statuses | id | DefaultPaginator | ✅ |  ❌  |
| customer_statuses | id | DefaultPaginator | ✅ |  ❌  |
| project_milestones | id | DefaultPaginator | ✅ |  ❌  |


## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.28 | 2025-12-09 | [70775](https://github.com/airbytehq/airbyte/pull/70775) | Update dependencies |
| 0.0.27 | 2025-11-25 | [70007](https://github.com/airbytehq/airbyte/pull/70007) | Update dependencies |
| 0.0.26 | 2025-11-18 | [69442](https://github.com/airbytehq/airbyte/pull/69442) | Update dependencies |
| 0.0.25 | 2025-10-29 | [68966](https://github.com/airbytehq/airbyte/pull/68966) | Update dependencies |
| 0.0.24 | 2025-10-21 | [68296](https://github.com/airbytehq/airbyte/pull/68296) | Update dependencies |
| 0.0.23 | 2025-10-14 | [68027](https://github.com/airbytehq/airbyte/pull/68027) | Update dependencies |
| 0.0.22 | 2025-10-07 | [67519](https://github.com/airbytehq/airbyte/pull/67519) | Update dependencies |
| 0.0.21 | 2025-09-30 | [66807](https://github.com/airbytehq/airbyte/pull/66807) | Update dependencies |
| 0.0.20 | 2025-09-24 | [66655](https://github.com/airbytehq/airbyte/pull/66655) | Update dependencies |
| 0.0.19 | 2025-09-09 | [65897](https://github.com/airbytehq/airbyte/pull/65897) | Update dependencies |
| 0.0.18 | 2025-08-23 | [65391](https://github.com/airbytehq/airbyte/pull/65391) | Update dependencies |
| 0.0.17 | 2025-08-09 | [64629](https://github.com/airbytehq/airbyte/pull/64629) | Update dependencies |
| 0.0.16 | 2025-08-02 | [64275](https://github.com/airbytehq/airbyte/pull/64275) | Update dependencies |
| 0.0.15 | 2025-07-26 | [63892](https://github.com/airbytehq/airbyte/pull/63892) | Update dependencies |
| 0.0.14 | 2025-07-19 | [63518](https://github.com/airbytehq/airbyte/pull/63518) | Update dependencies |
| 0.0.13 | 2025-07-12 | [63095](https://github.com/airbytehq/airbyte/pull/63095) | Update dependencies |
| 0.0.12 | 2025-07-05 | [62601](https://github.com/airbytehq/airbyte/pull/62601) | Update dependencies |
| 0.0.11 | 2025-06-28 | [62178](https://github.com/airbytehq/airbyte/pull/62178) | Update dependencies |
| 0.0.10 | 2025-06-26 | [61417](https://github.com/airbytehq/airbyte/pull/61417) | source-linear contribution from zckymc |
| 0.0.9 | 2025-06-21 | [61843](https://github.com/airbytehq/airbyte/pull/61843) | Update dependencies |
| 0.0.8 | 2025-06-14 | [61117](https://github.com/airbytehq/airbyte/pull/61117) | Update dependencies |
| 0.0.7 | 2025-05-24 | [60728](https://github.com/airbytehq/airbyte/pull/60728) | Update dependencies |
| 0.0.6 | 2025-05-10 | [59893](https://github.com/airbytehq/airbyte/pull/59893) | Update dependencies |
| 0.0.5 | 2025-05-03 | [59299](https://github.com/airbytehq/airbyte/pull/59299) | Update dependencies |
| 0.0.4 | 2025-04-26 | [58781](https://github.com/airbytehq/airbyte/pull/58781) | Update dependencies |
| 0.0.3 | 2025-04-19 | [58215](https://github.com/airbytehq/airbyte/pull/58215) | Update dependencies |
| 0.0.2 | 2025-04-12 | [57669](https://github.com/airbytehq/airbyte/pull/57669) | Update dependencies |
| 0.0.1 | 2025-04-11 | [#57586](https://github.com/airbytehq/airbyte/pull/57586) | Initial release by [@natikgadzhi](https://github.com/natikgadzhi) |

</details>
