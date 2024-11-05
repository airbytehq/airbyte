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
| 0.0.3 | 2024-11-04 | [48213](https://github.com/airbytehq/airbyte/pull/48213) | Update dependencies |
| 0.0.2 | 2024-10-29 | [47760](https://github.com/airbytehq/airbyte/pull/47760) | Update dependencies |
| 0.0.1 | 2024-09-25 | | Initial release by [@bnmry](https://github.com/bnmry) via Connector Builder |

</details>
