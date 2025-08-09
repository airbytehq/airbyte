# ShopWired
Website: https://admin.myshopwired.uk/
API Reference: https://api.shopwired.co.uk/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your API Key, which acts as the username for Basic Authentication. You can find it in your ShopWired account under API settings. |  |
| `api_secret` | `string` | API Secret. Your API Secret, which acts as the password for Basic Authentication. You can find it in your ShopWired account under API settings. |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| countries | id | No pagination | ✅ |  ❌  |
| pages | id | DefaultPaginator | ✅ |  ✅  |
| products | id | DefaultPaginator | ✅ |  ✅  |
| products_images | id | DefaultPaginator | ✅ |  ❌  |
| choice_sets | id | DefaultPaginator | ✅ |  ❌  |
| products_reviews | id | DefaultPaginator | ✅ |  ✅  |
| product_options | id | DefaultPaginator | ✅ |  ❌  |
| products_variations | id | DefaultPaginator | ✅ |  ❌  |
| customers | id | DefaultPaginator | ✅ |  ✅  |
| orders | id | DefaultPaginator | ✅ |  ✅  |
| shipping_zones | uuid | DefaultPaginator | ✅ |  ❌  |
| events | id | DefaultPaginator | ✅ |  ✅  |
| categories | id | DefaultPaginator | ✅ |  ✅  |
| themes | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.10 | 2025-08-09 | [64843](https://github.com/airbytehq/airbyte/pull/64843) | Update dependencies |
| 0.0.9 | 2025-07-19 | [63639](https://github.com/airbytehq/airbyte/pull/63639) | Update dependencies |
| 0.0.8 | 2025-07-12 | [63053](https://github.com/airbytehq/airbyte/pull/63053) | Update dependencies |
| 0.0.7 | 2025-06-28 | [62295](https://github.com/airbytehq/airbyte/pull/62295) | Update dependencies |
| 0.0.6 | 2025-06-14 | [61618](https://github.com/airbytehq/airbyte/pull/61618) | Update dependencies |
| 0.0.5 | 2025-05-24 | [60107](https://github.com/airbytehq/airbyte/pull/60107) | Update dependencies |
| 0.0.4 | 2025-05-04 | [58966](https://github.com/airbytehq/airbyte/pull/58966) | Update dependencies |
| 0.0.3 | 2025-04-19 | [58419](https://github.com/airbytehq/airbyte/pull/58419) | Update dependencies |
| 0.0.2 | 2025-04-12 | [57937](https://github.com/airbytehq/airbyte/pull/57937) | Update dependencies |
| 0.0.1 | 2025-04-06 | [57493](https://github.com/airbytehq/airbyte/pull/57493) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
