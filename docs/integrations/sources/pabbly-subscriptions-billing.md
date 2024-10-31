# Pabbly Subscriptions Billing
 Airbyte connector for[Pabbly Subscriptions Billing](https://www.pabbly.com/subscriptions/) enables seamless data synchronization between Pabbly&#39;s subscription management platform and your preferred data warehouse or analytics environment. With this connector, users can automate the extraction of key subscription data—such as customer details, payment transactions, and subscription statuses—allowing for efficient reporting, analysis, and decision-making without manual intervention.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | Username.  |  |
| `password` | `string` | Password.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| customers | id | No pagination | ✅ |  ❌  |
| subscriptions | id | No pagination | ✅ |  ❌  |
| products | id | No pagination | ✅ |  ❌  |
| coupons | id | No pagination | ✅ |  ❌  |
| invoices | id | No pagination | ✅ |  ❌  |
| payment_methods | id | No pagination | ✅ |  ❌  |
| transactions | id | No pagination | ✅ |  ❌  |
| addons | id | No pagination | ✅ |  ❌  |
| addon_list_category | id | No pagination | ✅ |  ❌  |
| licenses | id | No pagination | ✅ |  ❌  |
| multiplans | id | No pagination | ✅ |  ❌  |
| payment_gateways | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-31 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
