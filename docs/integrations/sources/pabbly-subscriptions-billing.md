# Pabbly Subscriptions Billing
Airbyte connector for [Pabbly Subscriptions Billing](https://www.pabbly.com/subscriptions/) enables seamless data synchronization between Pabbly&#39;s subscription management platform and your preferred data warehouse or analytics environment. With this connector, users can automate the extraction of key subscription data—such as customer details, payment transactions, and subscription statuses—allowing for efficient reporting, analysis, and decision-making without manual intervention

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `password` | `string` | Password.  |  |
| `username` | `string` | Username.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| customers | id | DefaultPaginator | ✅ |  ❌  |
| subscriptions | id | DefaultPaginator | ✅ |  ❌  |
| products | id | DefaultPaginator | ✅ |  ❌  |
| coupons | id | DefaultPaginator | ✅ |  ❌  |
| invoices | id | DefaultPaginator | ✅ |  ❌  |
| payment_methods | id | DefaultPaginator | ✅ |  ❌  |
| transactions | id | DefaultPaginator | ✅ |  ❌  |
| refunds | id | DefaultPaginator | ✅ |  ❌  |
| addons | id | DefaultPaginator | ✅ |  ❌  |
| addon_list_category | id | DefaultPaginator | ✅ |  ❌  |
| licenses | id | DefaultPaginator | ✅ |  ❌  |
| multiplans | id | DefaultPaginator | ✅ |  ❌  |
| payment_gateways | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.8 | 2025-01-25 | [52521](https://github.com/airbytehq/airbyte/pull/52521) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51317](https://github.com/airbytehq/airbyte/pull/51317) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50725](https://github.com/airbytehq/airbyte/pull/50725) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50249](https://github.com/airbytehq/airbyte/pull/50249) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49681](https://github.com/airbytehq/airbyte/pull/49681) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49320](https://github.com/airbytehq/airbyte/pull/49320) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49056](https://github.com/airbytehq/airbyte/pull/49056) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-11-08 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
