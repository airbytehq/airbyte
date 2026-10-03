# Hyperline
Sync subscription and billing data from Hyperline into your data warehouse.
This source connector syncs customers, quotes, subscriptions, products, invoices, companies, coupons and price configurations.
Configuration requires your Hyperline API key and a start date from which to sync data.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start Date. The earliest date to sync records from. Format: YYYY-MM-DDTHH:MM:SSZ |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| products |  | DefaultPaginator | ✅ |  ❌  |
| companies |  | DefaultPaginator | ✅ |  ❌  |
| coupons |  | DefaultPaginator | ✅ |  ❌  |
| customers | id | DefaultPaginator | ✅ |  ✅  |
| invoices | id | DefaultPaginator | ✅ |  ✅  |
| price_configurations |  | DefaultPaginator | ✅ |  ❌  |
| quotes | id | DefaultPaginator | ✅ |  ✅  |
| subscriptions | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-04-15 | | Initial release by [@tania-gonzalez9](https://github.com/tania-gonzalez9) via Connector Builder |

</details>
