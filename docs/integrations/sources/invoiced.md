# Invoiced
This Airbyte connector for **Invoiced** enables seamless data integration between Invoiced, a cloud-based billing and invoicing platform, and various data destinations. Using this connector, you can automatically extract and sync data such as invoices, customers, payments, and more from the Invoiced API into your preferred data warehouse or analytics platform. It simplifies the process of managing financial data and helps businesses maintain accurate and up-to-date records, facilitating better reporting and analysis. Ideal for users who need to automate data pipelines from their invoicing system.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use. Find it at https://invoiced.com/account |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| customers | id | DefaultPaginator | ✅ |  ❌  |
| invoices | id | DefaultPaginator | ✅ |  ❌  |
| payments | id | DefaultPaginator | ✅ |  ❌  |
| credit_balance_adjustments | id | DefaultPaginator | ✅ |  ❌  |
| credit_notes | id | DefaultPaginator | ✅ |  ❌  |
| subscriptions |  | DefaultPaginator | ✅ |  ❌  |
| estimates | id | DefaultPaginator | ✅ |  ❌  |
| contacts | id | DefaultPaginator | ✅ |  ❌  |
| items | id | DefaultPaginator | ✅ |  ❌  |
| tax_rates | id | DefaultPaginator | ✅ |  ❌  |
| plans | id | DefaultPaginator | ✅ |  ❌  |
| coupons | id | DefaultPaginator | ✅ |  ❌  |
| events | id | DefaultPaginator | ✅ |  ❌  |
| notes | id | DefaultPaginator | ✅ |  ❌  |
| tasks | id | DefaultPaginator | ✅ |  ❌  |
| metered_billings | id | DefaultPaginator | ✅ |  ❌  |
| payment_sources | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.45 | 2025-12-09 | [70466](https://github.com/airbytehq/airbyte/pull/70466) | Update dependencies |
| 0.0.44 | 2025-11-25 | [70194](https://github.com/airbytehq/airbyte/pull/70194) | Update dependencies |
| 0.0.43 | 2025-11-18 | [69508](https://github.com/airbytehq/airbyte/pull/69508) | Update dependencies |
| 0.0.42 | 2025-10-29 | [68790](https://github.com/airbytehq/airbyte/pull/68790) | Update dependencies |
| 0.0.41 | 2025-10-21 | [68512](https://github.com/airbytehq/airbyte/pull/68512) | Update dependencies |
| 0.0.40 | 2025-10-14 | [67961](https://github.com/airbytehq/airbyte/pull/67961) | Update dependencies |
| 0.0.39 | 2025-10-07 | [67370](https://github.com/airbytehq/airbyte/pull/67370) | Update dependencies |
| 0.0.38 | 2025-09-30 | [66787](https://github.com/airbytehq/airbyte/pull/66787) | Update dependencies |
| 0.0.37 | 2025-09-09 | [66062](https://github.com/airbytehq/airbyte/pull/66062) | Update dependencies |
| 0.0.36 | 2025-08-23 | [65339](https://github.com/airbytehq/airbyte/pull/65339) | Update dependencies |
| 0.0.35 | 2025-08-09 | [64637](https://github.com/airbytehq/airbyte/pull/64637) | Update dependencies |
| 0.0.34 | 2025-08-02 | [64172](https://github.com/airbytehq/airbyte/pull/64172) | Update dependencies |
| 0.0.33 | 2025-07-26 | [63904](https://github.com/airbytehq/airbyte/pull/63904) | Update dependencies |
| 0.0.32 | 2025-07-19 | [63525](https://github.com/airbytehq/airbyte/pull/63525) | Update dependencies |
| 0.0.31 | 2025-07-12 | [63157](https://github.com/airbytehq/airbyte/pull/63157) | Update dependencies |
| 0.0.30 | 2025-07-05 | [62602](https://github.com/airbytehq/airbyte/pull/62602) | Update dependencies |
| 0.0.29 | 2025-06-28 | [62185](https://github.com/airbytehq/airbyte/pull/62185) | Update dependencies |
| 0.0.28 | 2025-06-21 | [61863](https://github.com/airbytehq/airbyte/pull/61863) | Update dependencies |
| 0.0.27 | 2025-06-14 | [61130](https://github.com/airbytehq/airbyte/pull/61130) | Update dependencies |
| 0.0.26 | 2025-05-24 | [60655](https://github.com/airbytehq/airbyte/pull/60655) | Update dependencies |
| 0.0.25 | 2025-05-10 | [59883](https://github.com/airbytehq/airbyte/pull/59883) | Update dependencies |
| 0.0.24 | 2025-05-03 | [59288](https://github.com/airbytehq/airbyte/pull/59288) | Update dependencies |
| 0.0.23 | 2025-04-26 | [58829](https://github.com/airbytehq/airbyte/pull/58829) | Update dependencies |
| 0.0.22 | 2025-04-19 | [58195](https://github.com/airbytehq/airbyte/pull/58195) | Update dependencies |
| 0.0.21 | 2025-04-12 | [57746](https://github.com/airbytehq/airbyte/pull/57746) | Update dependencies |
| 0.0.20 | 2025-04-05 | [57045](https://github.com/airbytehq/airbyte/pull/57045) | Update dependencies |
| 0.0.19 | 2025-03-29 | [56643](https://github.com/airbytehq/airbyte/pull/56643) | Update dependencies |
| 0.0.18 | 2025-03-22 | [56021](https://github.com/airbytehq/airbyte/pull/56021) | Update dependencies |
| 0.0.17 | 2025-03-08 | [55485](https://github.com/airbytehq/airbyte/pull/55485) | Update dependencies |
| 0.0.16 | 2025-03-01 | [54818](https://github.com/airbytehq/airbyte/pull/54818) | Update dependencies |
| 0.0.15 | 2025-02-22 | [54295](https://github.com/airbytehq/airbyte/pull/54295) | Update dependencies |
| 0.0.14 | 2025-02-15 | [53824](https://github.com/airbytehq/airbyte/pull/53824) | Update dependencies |
| 0.0.13 | 2025-02-08 | [53249](https://github.com/airbytehq/airbyte/pull/53249) | Update dependencies |
| 0.0.12 | 2025-02-01 | [52755](https://github.com/airbytehq/airbyte/pull/52755) | Update dependencies |
| 0.0.11 | 2025-01-25 | [52237](https://github.com/airbytehq/airbyte/pull/52237) | Update dependencies |
| 0.0.10 | 2025-01-18 | [51828](https://github.com/airbytehq/airbyte/pull/51828) | Update dependencies |
| 0.0.9 | 2025-01-11 | [51141](https://github.com/airbytehq/airbyte/pull/51141) | Update dependencies |
| 0.0.8 | 2024-12-28 | [50600](https://github.com/airbytehq/airbyte/pull/50600) | Update dependencies |
| 0.0.7 | 2024-12-21 | [50103](https://github.com/airbytehq/airbyte/pull/50103) | Update dependencies |
| 0.0.6 | 2024-12-14 | [49650](https://github.com/airbytehq/airbyte/pull/49650) | Update dependencies |
| 0.0.5 | 2024-12-12 | [49266](https://github.com/airbytehq/airbyte/pull/49266) | Update dependencies |
| 0.0.4 | 2024-12-11 | [48987](https://github.com/airbytehq/airbyte/pull/48987) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.3 | 2024-10-29 | [47734](https://github.com/airbytehq/airbyte/pull/47734) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47534](https://github.com/airbytehq/airbyte/pull/47534) | Update dependencies |
| 0.0.1 | 2024-10-21 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
