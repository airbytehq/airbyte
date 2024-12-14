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
| 0.0.6 | 2024-12-14 | [49650](https://github.com/airbytehq/airbyte/pull/49650) | Update dependencies |
| 0.0.5 | 2024-12-12 | [49266](https://github.com/airbytehq/airbyte/pull/49266) | Update dependencies |
| 0.0.4 | 2024-12-11 | [48987](https://github.com/airbytehq/airbyte/pull/48987) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.3 | 2024-10-29 | [47734](https://github.com/airbytehq/airbyte/pull/47734) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47534](https://github.com/airbytehq/airbyte/pull/47534) | Update dependencies |
| 0.0.1 | 2024-10-21 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
