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
| 0.0.1 | 2025-04-09 | | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
