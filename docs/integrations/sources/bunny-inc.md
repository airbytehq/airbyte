# Bunny RevOps

Bunny provides a single platform for subscription management, billing, quoting, revenue recognition, and SaaS metrics.
[API Docs](https://docs.bunny.com/developer)

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `apikey` | `string` | API Key.  |  |
| `subdomain` | `string` | Subdomain. The subdomain specific to your Bunny account or service. |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| accounts | id | DefaultPaginator | ✅ |  ❌  |
| accountBalances | id | DefaultPaginator | ✅ |  ❌  |
| contacts | id | DefaultPaginator | ✅ |  ❌  |
| entities | id | DefaultPaginator | ✅ |  ❌  |
| invoices | id | DefaultPaginator | ✅ |  ❌  |
| invoiceItems | id | DefaultPaginator | ✅ |  ❌  |
| payments | id | DefaultPaginator | ✅ |  ❌  |
| products | id | DefaultPaginator | ✅ |  ❌  |
| plans | id | DefaultPaginator | ✅ |  ❌  |
| quotes | id | DefaultPaginator | ✅ |  ❌  |
| quote_charges | id | DefaultPaginator | ✅ |  ❌  |
| subscriptions | id | DefaultPaginator | ✅ |  ❌  |
| subscriptionCharges | id | DefaultPaginator | ✅ |  ❌  |
| transactions | id | DefaultPaginator | ✅ |  ❌  |
| tenants | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.24 | 2025-06-15 | [61624](https://github.com/airbytehq/airbyte/pull/61624) | Update dependencies |
| 0.0.23 | 2025-05-17 | [60646](https://github.com/airbytehq/airbyte/pull/60646) | Update dependencies |
| 0.0.22 | 2025-05-10 | [59789](https://github.com/airbytehq/airbyte/pull/59789) | Update dependencies |
| 0.0.21 | 2025-05-03 | [59363](https://github.com/airbytehq/airbyte/pull/59363) | Update dependencies |
| 0.0.20 | 2025-04-26 | [58687](https://github.com/airbytehq/airbyte/pull/58687) | Update dependencies |
| 0.0.19 | 2025-04-19 | [58285](https://github.com/airbytehq/airbyte/pull/58285) | Update dependencies |
| 0.0.18 | 2025-04-12 | [57638](https://github.com/airbytehq/airbyte/pull/57638) | Update dependencies |
| 0.0.17 | 2025-04-05 | [57147](https://github.com/airbytehq/airbyte/pull/57147) | Update dependencies |
| 0.0.16 | 2025-03-29 | [56582](https://github.com/airbytehq/airbyte/pull/56582) | Update dependencies |
| 0.0.15 | 2025-03-22 | [56088](https://github.com/airbytehq/airbyte/pull/56088) | Update dependencies |
| 0.0.14 | 2025-03-08 | [55420](https://github.com/airbytehq/airbyte/pull/55420) | Update dependencies |
| 0.0.13 | 2025-03-01 | [54840](https://github.com/airbytehq/airbyte/pull/54840) | Update dependencies |
| 0.0.12 | 2025-02-22 | [54260](https://github.com/airbytehq/airbyte/pull/54260) | Update dependencies |
| 0.0.11 | 2025-02-15 | [53915](https://github.com/airbytehq/airbyte/pull/53915) | Update dependencies |
| 0.0.10 | 2025-02-08 | [53442](https://github.com/airbytehq/airbyte/pull/53442) | Update dependencies |
| 0.0.9 | 2025-02-01 | [52912](https://github.com/airbytehq/airbyte/pull/52912) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52154](https://github.com/airbytehq/airbyte/pull/52154) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51720](https://github.com/airbytehq/airbyte/pull/51720) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51283](https://github.com/airbytehq/airbyte/pull/51283) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50470](https://github.com/airbytehq/airbyte/pull/50470) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50190](https://github.com/airbytehq/airbyte/pull/50190) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49555](https://github.com/airbytehq/airbyte/pull/49555) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49007](https://github.com/airbytehq/airbyte/pull/49007) | Update dependencies |
| 0.0.1 | 2024-10-29 | | Initial release by [@tbpeders](https://github.com/tbpeders) via Connector Builder |

</details>
