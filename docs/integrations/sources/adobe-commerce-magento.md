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

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.19 | 2026-07-14 | [81713](https://github.com/airbytehq/airbyte/pull/81713) | Update dependencies |
| 0.0.18 | 2026-06-30 | [80972](https://github.com/airbytehq/airbyte/pull/80972) | Update dependencies |
| 0.0.17 | 2026-06-23 | [80352](https://github.com/airbytehq/airbyte/pull/80352) | Update dependencies |
| 0.0.16 | 2026-06-16 | [79762](https://github.com/airbytehq/airbyte/pull/79762) | Update dependencies |
| 0.0.15 | 2026-06-09 | [79198](https://github.com/airbytehq/airbyte/pull/79198) | Update dependencies |
| 0.0.14 | 2026-06-02 | [78553](https://github.com/airbytehq/airbyte/pull/78553) | Update dependencies |
| 0.0.13 | 2026-04-28 | [77168](https://github.com/airbytehq/airbyte/pull/77168) | Update dependencies |
| 0.0.12 | 2026-04-21 | [76511](https://github.com/airbytehq/airbyte/pull/76511) | Update dependencies |
| 0.0.11 | 2026-03-17 | [74982](https://github.com/airbytehq/airbyte/pull/74982) | Update dependencies |
| 0.0.10 | 2026-03-10 | [74535](https://github.com/airbytehq/airbyte/pull/74535) | Update dependencies |
| 0.0.9 | 2026-02-10 | [73003](https://github.com/airbytehq/airbyte/pull/73003) | Update dependencies |
| 0.0.8 | 2026-01-20 | [71997](https://github.com/airbytehq/airbyte/pull/71997) | Update dependencies |
| 0.0.7 | 2026-01-14 | [71508](https://github.com/airbytehq/airbyte/pull/71508) | Update dependencies |
| 0.0.6 | 2025-12-18 | [70559](https://github.com/airbytehq/airbyte/pull/70559) | Update dependencies |
| 0.0.5 | 2025-11-25 | [69909](https://github.com/airbytehq/airbyte/pull/69909) | Update dependencies |
| 0.0.4 | 2025-10-29 | [69058](https://github.com/airbytehq/airbyte/pull/69058) | Update dependencies |
| 0.0.3 | 2025-09-30 | [65651](https://github.com/airbytehq/airbyte/pull/65651) | Update dependencies |
| 0.0.2 | 2025-08-23 | [65323](https://github.com/airbytehq/airbyte/pull/65323) | Update dependencies |
| 0.0.1 | 2025-07-26 | | Initial release by [@joacoc2020](https://github.com/joacoc2020) via Connector Builder |

</details>
