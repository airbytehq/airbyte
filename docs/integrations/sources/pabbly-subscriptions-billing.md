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
| 0.0.40 | 2025-12-09 | [70495](https://github.com/airbytehq/airbyte/pull/70495) | Update dependencies |
| 0.0.39 | 2025-11-25 | [70122](https://github.com/airbytehq/airbyte/pull/70122) | Update dependencies |
| 0.0.38 | 2025-11-18 | [69670](https://github.com/airbytehq/airbyte/pull/69670) | Update dependencies |
| 0.0.37 | 2025-10-29 | [69024](https://github.com/airbytehq/airbyte/pull/69024) | Update dependencies |
| 0.0.36 | 2025-10-21 | [68308](https://github.com/airbytehq/airbyte/pull/68308) | Update dependencies |
| 0.0.35 | 2025-10-14 | [67741](https://github.com/airbytehq/airbyte/pull/67741) | Update dependencies |
| 0.0.34 | 2025-10-07 | [67350](https://github.com/airbytehq/airbyte/pull/67350) | Update dependencies |
| 0.0.33 | 2025-09-30 | [66381](https://github.com/airbytehq/airbyte/pull/66381) | Update dependencies |
| 0.0.32 | 2025-09-09 | [65773](https://github.com/airbytehq/airbyte/pull/65773) | Update dependencies |
| 0.0.31 | 2025-08-23 | [65201](https://github.com/airbytehq/airbyte/pull/65201) | Update dependencies |
| 0.0.30 | 2025-08-09 | [64758](https://github.com/airbytehq/airbyte/pull/64758) | Update dependencies |
| 0.0.29 | 2025-08-02 | [64297](https://github.com/airbytehq/airbyte/pull/64297) | Update dependencies |
| 0.0.28 | 2025-07-26 | [63920](https://github.com/airbytehq/airbyte/pull/63920) | Update dependencies |
| 0.0.27 | 2025-07-19 | [63448](https://github.com/airbytehq/airbyte/pull/63448) | Update dependencies |
| 0.0.26 | 2025-07-12 | [63248](https://github.com/airbytehq/airbyte/pull/63248) | Update dependencies |
| 0.0.25 | 2025-07-05 | [62575](https://github.com/airbytehq/airbyte/pull/62575) | Update dependencies |
| 0.0.24 | 2025-06-28 | [62378](https://github.com/airbytehq/airbyte/pull/62378) | Update dependencies |
| 0.0.23 | 2025-06-21 | [61911](https://github.com/airbytehq/airbyte/pull/61911) | Update dependencies |
| 0.0.22 | 2025-06-14 | [60549](https://github.com/airbytehq/airbyte/pull/60549) | Update dependencies |
| 0.0.21 | 2025-05-10 | [60157](https://github.com/airbytehq/airbyte/pull/60157) | Update dependencies |
| 0.0.20 | 2025-05-03 | [59482](https://github.com/airbytehq/airbyte/pull/59482) | Update dependencies |
| 0.0.19 | 2025-04-27 | [59052](https://github.com/airbytehq/airbyte/pull/59052) | Update dependencies |
| 0.0.18 | 2025-04-19 | [58466](https://github.com/airbytehq/airbyte/pull/58466) | Update dependencies |
| 0.0.17 | 2025-04-12 | [57911](https://github.com/airbytehq/airbyte/pull/57911) | Update dependencies |
| 0.0.16 | 2025-04-05 | [57290](https://github.com/airbytehq/airbyte/pull/57290) | Update dependencies |
| 0.0.15 | 2025-03-29 | [56798](https://github.com/airbytehq/airbyte/pull/56798) | Update dependencies |
| 0.0.14 | 2025-03-22 | [56203](https://github.com/airbytehq/airbyte/pull/56203) | Update dependencies |
| 0.0.13 | 2025-03-08 | [55049](https://github.com/airbytehq/airbyte/pull/55049) | Update dependencies |
| 0.0.12 | 2025-02-23 | [54556](https://github.com/airbytehq/airbyte/pull/54556) | Update dependencies |
| 0.0.11 | 2025-02-15 | [54011](https://github.com/airbytehq/airbyte/pull/54011) | Update dependencies |
| 0.0.10 | 2025-02-08 | [53512](https://github.com/airbytehq/airbyte/pull/53512) | Update dependencies |
| 0.0.9 | 2025-02-01 | [52974](https://github.com/airbytehq/airbyte/pull/52974) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52521](https://github.com/airbytehq/airbyte/pull/52521) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51317](https://github.com/airbytehq/airbyte/pull/51317) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50725](https://github.com/airbytehq/airbyte/pull/50725) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50249](https://github.com/airbytehq/airbyte/pull/50249) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49681](https://github.com/airbytehq/airbyte/pull/49681) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49320](https://github.com/airbytehq/airbyte/pull/49320) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49056](https://github.com/airbytehq/airbyte/pull/49056) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-11-08 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
