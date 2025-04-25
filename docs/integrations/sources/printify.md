# Printify
Website: https://printify.com/
API Reference: https://developers.printify.com/#catalog

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_token` | `string` | API Token. Your Printify API token. Obtain it from your Printify account settings. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| shops | id | DefaultPaginator | ✅ |  ❌  |
| shop_orders | id | DefaultPaginator | ✅ |  ❌  |
| catalog_blueprints | id | DefaultPaginator | ✅ |  ❌  |
| catalog_print_providers | id | DefaultPaginator | ✅ |  ❌  |
| shop_products | id | DefaultPaginator | ✅ |  ❌  |
| catalog_blueprint_print_providers | uuid | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.3 | 2025-04-19 | [58484](https://github.com/airbytehq/airbyte/pull/58484) | Update dependencies |
| 0.0.2 | 2025-04-12 | [57892](https://github.com/airbytehq/airbyte/pull/57892) | Update dependencies |
| 0.0.1 | 2025-04-09 | [57546](https://github.com/airbytehq/airbyte/pull/57546) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
