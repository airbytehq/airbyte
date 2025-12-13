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
| 0.0.45 | 2025-12-09 | [70709](https://github.com/airbytehq/airbyte/pull/70709) | Update dependencies |
| 0.0.44 | 2025-11-25 | [70127](https://github.com/airbytehq/airbyte/pull/70127) | Update dependencies |
| 0.0.43 | 2025-11-18 | [69510](https://github.com/airbytehq/airbyte/pull/69510) | Update dependencies |
| 0.0.42 | 2025-10-29 | [68968](https://github.com/airbytehq/airbyte/pull/68968) | Update dependencies |
| 0.0.41 | 2025-10-21 | [68438](https://github.com/airbytehq/airbyte/pull/68438) | Update dependencies |
| 0.0.40 | 2025-10-14 | [67985](https://github.com/airbytehq/airbyte/pull/67985) | Update dependencies |
| 0.0.39 | 2025-10-07 | [67244](https://github.com/airbytehq/airbyte/pull/67244) | Update dependencies |
| 0.0.38 | 2025-09-30 | [66848](https://github.com/airbytehq/airbyte/pull/66848) | Update dependencies |
| 0.0.37 | 2025-09-24 | [66474](https://github.com/airbytehq/airbyte/pull/66474) | Update dependencies |
| 0.0.36 | 2025-09-09 | [65703](https://github.com/airbytehq/airbyte/pull/65703) | Update dependencies |
| 0.0.35 | 2025-08-24 | [65455](https://github.com/airbytehq/airbyte/pull/65455) | Update dependencies |
| 0.0.34 | 2025-08-09 | [64820](https://github.com/airbytehq/airbyte/pull/64820) | Update dependencies |
| 0.0.33 | 2025-08-02 | [64309](https://github.com/airbytehq/airbyte/pull/64309) | Update dependencies |
| 0.0.32 | 2025-07-26 | [64064](https://github.com/airbytehq/airbyte/pull/64064) | Update dependencies |
| 0.0.31 | 2025-07-20 | [63677](https://github.com/airbytehq/airbyte/pull/63677) | Update dependencies |
| 0.0.30 | 2025-07-12 | [63214](https://github.com/airbytehq/airbyte/pull/63214) | Update dependencies |
| 0.0.29 | 2025-07-05 | [62699](https://github.com/airbytehq/airbyte/pull/62699) | Update dependencies |
| 0.0.28 | 2025-06-28 | [62201](https://github.com/airbytehq/airbyte/pull/62201) | Update dependencies |
| 0.0.27 | 2025-06-21 | [61764](https://github.com/airbytehq/airbyte/pull/61764) | Update dependencies |
| 0.0.26 | 2025-06-15 | [61198](https://github.com/airbytehq/airbyte/pull/61198) | Update dependencies |
| 0.0.25 | 2025-05-24 | [60761](https://github.com/airbytehq/airbyte/pull/60761) | Update dependencies |
| 0.0.24 | 2025-05-10 | [59948](https://github.com/airbytehq/airbyte/pull/59948) | Update dependencies |
| 0.0.23 | 2025-05-04 | [59555](https://github.com/airbytehq/airbyte/pull/59555) | Update dependencies |
| 0.0.22 | 2025-04-26 | [58936](https://github.com/airbytehq/airbyte/pull/58936) | Update dependencies |
| 0.0.21 | 2025-04-19 | [58566](https://github.com/airbytehq/airbyte/pull/58566) | Update dependencies |
| 0.0.20 | 2025-04-12 | [58012](https://github.com/airbytehq/airbyte/pull/58012) | Update dependencies |
| 0.0.19 | 2025-04-05 | [57373](https://github.com/airbytehq/airbyte/pull/57373) | Update dependencies |
| 0.0.18 | 2025-03-29 | [56818](https://github.com/airbytehq/airbyte/pull/56818) | Update dependencies |
| 0.0.17 | 2025-03-22 | [56342](https://github.com/airbytehq/airbyte/pull/56342) | Update dependencies |
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
