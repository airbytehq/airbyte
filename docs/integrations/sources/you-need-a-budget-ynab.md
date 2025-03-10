# You Need A Budget (YNAB)
Replicates the budgets, accounts, categories, payees, transactions, and category groups from the You Need A Budget (YNAB) API. Requires personal access token from https://api.ynab.com/#personal-access-tokens

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Budgets | id | No pagination | ✅ |  ❌  |
| Accounts | id | No pagination | ✅ |  ❌  |
| Categories |  | No pagination | ✅ |  ❌  |
| Payees |  | No pagination | ✅ |  ❌  |
| Transactions | id | No pagination | ✅ |  ❌  |
| Category Groups |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.16 | 2025-03-08 | [55576](https://github.com/airbytehq/airbyte/pull/55576) | Update dependencies |
| 0.0.15 | 2025-03-01 | [55138](https://github.com/airbytehq/airbyte/pull/55138) | Update dependencies |
| 0.0.14 | 2025-02-22 | [54513](https://github.com/airbytehq/airbyte/pull/54513) | Update dependencies |
| 0.0.13 | 2025-02-15 | [54077](https://github.com/airbytehq/airbyte/pull/54077) | Update dependencies |
| 0.0.12 | 2025-02-08 | [53517](https://github.com/airbytehq/airbyte/pull/53517) | Update dependencies |
| 0.0.11 | 2025-02-01 | [53077](https://github.com/airbytehq/airbyte/pull/53077) | Update dependencies |
| 0.0.10 | 2025-01-25 | [52434](https://github.com/airbytehq/airbyte/pull/52434) | Update dependencies |
| 0.0.9 | 2025-01-18 | [51953](https://github.com/airbytehq/airbyte/pull/51953) | Update dependencies |
| 0.0.8 | 2025-01-11 | [51418](https://github.com/airbytehq/airbyte/pull/51418) | Update dependencies |
| 0.0.7 | 2024-12-28 | [50377](https://github.com/airbytehq/airbyte/pull/50377) | Update dependencies |
| 0.0.6 | 2024-12-14 | [49736](https://github.com/airbytehq/airbyte/pull/49736) | Update dependencies |
| 0.0.5 | 2024-12-12 | [49376](https://github.com/airbytehq/airbyte/pull/49376) | Update dependencies |
| 0.0.4 | 2024-12-11 | [49130](https://github.com/airbytehq/airbyte/pull/49130) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.3 | 2024-11-04 | [48213](https://github.com/airbytehq/airbyte/pull/48213) | Update dependencies |
| 0.0.2 | 2024-10-29 | [47760](https://github.com/airbytehq/airbyte/pull/47760) | Update dependencies |
| 0.0.1 | 2024-09-25 | | Initial release by [@bnmry](https://github.com/bnmry) via Connector Builder |

</details>
