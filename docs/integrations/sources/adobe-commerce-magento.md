# Adobe Commerce (Magento)
Integrate Adobe Commerce store data to your destination

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | Integration Access Token.  |  |
| `start_date` | `string` | Start Date.  |  |
| `store_host` | `string` | Store Host. magento.mystore.com |  |
| `api_version` | `string` | API Version. V1 | V1 |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| carts | id | DefaultPaginator | ✅ |  ✅  |
| coupons | coupon_id | DefaultPaginator | ✅ |  ✅  |
| creditmemos | entity_id | DefaultPaginator | ✅ |  ✅  |
| customers | id | DefaultPaginator | ✅ |  ✅  |
| customer_groups | id.code | DefaultPaginator | ✅ |  ❌  |
| directory_countries | id | DefaultPaginator | ✅ |  ❌  |
| directory_currency | base_currency_code | DefaultPaginator | ✅ |  ❌  |
| inventory_stocks | stock_id | DefaultPaginator | ✅ |  ❌  |
| inventory_sources | source_code | DefaultPaginator | ✅ |  ❌  |
| inventory_source_items | sku | DefaultPaginator | ✅ |  ❌  |
| invoices | entity_id | DefaultPaginator | ✅ |  ✅  |
| orders | entity_id | DefaultPaginator | ✅ |  ✅  |
| products | id | DefaultPaginator | ✅ |  ✅  |
| sales_rules | rule_id | DefaultPaginator | ✅ |  ✅  |
| shipments | entity_id | DefaultPaginator | ✅ |  ✅  |
| store_websites | id.code | DefaultPaginator | ✅ |  ❌  |
| store_views | id.code | DefaultPaginator | ✅ |  ❌  |
| store_groups | id.code | DefaultPaginator | ✅ |  ❌  |
| tax_rates | id | DefaultPaginator | ✅ |  ❌  |
| tax_classes | class_id | DefaultPaginator | ✅ |  ❌  |
| transactions | transaction_id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.6 | 2025-12-09 | [70559](https://github.com/airbytehq/airbyte/pull/70559) | Update dependencies |
| 0.0.5 | 2025-11-25 | [69909](https://github.com/airbytehq/airbyte/pull/69909) | Update dependencies |
| 0.0.4 | 2025-10-29 | [69058](https://github.com/airbytehq/airbyte/pull/69058) | Update dependencies |
| 0.0.3 | 2025-09-30 | [65651](https://github.com/airbytehq/airbyte/pull/65651) | Update dependencies |
| 0.0.2 | 2025-08-23 | [65323](https://github.com/airbytehq/airbyte/pull/65323) | Update dependencies |
| 0.0.1 | 2025-07-26 | | Initial release by [@joacoc2020](https://github.com/joacoc2020) via Connector Builder |

</details>
