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
| 0.0.13 | 2026-04-28 | [77164](https://github.com/airbytehq/airbyte/pull/77164) | Update dependencies |
| 0.0.12 | 2026-04-21 | [76551](https://github.com/airbytehq/airbyte/pull/76551) | Update dependencies |
| 0.0.11 | 2026-03-31 | [75769](https://github.com/airbytehq/airbyte/pull/75769) | Update dependencies |
| 0.0.10 | 2026-03-17 | [75077](https://github.com/airbytehq/airbyte/pull/75077) | Update dependencies |
| 0.0.9 | 2026-03-10 | [74454](https://github.com/airbytehq/airbyte/pull/74454) | Update dependencies |
| 0.0.8 | 2026-02-24 | [73822](https://github.com/airbytehq/airbyte/pull/73822) | Update dependencies |
| 0.0.7 | 2026-02-17 | [73447](https://github.com/airbytehq/airbyte/pull/73447) | Update dependencies |
| 0.0.6 | 2026-02-10 | [73000](https://github.com/airbytehq/airbyte/pull/73000) | Update dependencies |
| 0.0.5 | 2026-02-03 | [72704](https://github.com/airbytehq/airbyte/pull/72704) | Update dependencies |
| 0.0.4 | 2026-01-20 | [72112](https://github.com/airbytehq/airbyte/pull/72112) | Update dependencies |
| 0.0.3 | 2026-01-14 | [71711](https://github.com/airbytehq/airbyte/pull/71711) | Update dependencies |
| 0.0.2 | 2025-12-19 | [70944](https://github.com/airbytehq/airbyte/pull/70944) | Update dependencies |
| 0.0.1 | 2025-10-13 | | Initial release by [@FVidalCarneiro](https://github.com/FVidalCarneiro) via Connector Builder |

</details>
