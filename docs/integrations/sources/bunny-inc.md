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
