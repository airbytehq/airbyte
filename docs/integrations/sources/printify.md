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
| 0.0.26 | 2025-12-09 | [70591](https://github.com/airbytehq/airbyte/pull/70591) | Update dependencies |
| 0.0.25 | 2025-11-25 | [70026](https://github.com/airbytehq/airbyte/pull/70026) | Update dependencies |
| 0.0.24 | 2025-11-18 | [69597](https://github.com/airbytehq/airbyte/pull/69597) | Update dependencies |
| 0.0.23 | 2025-10-29 | [68978](https://github.com/airbytehq/airbyte/pull/68978) | Update dependencies |
| 0.0.22 | 2025-10-21 | [68380](https://github.com/airbytehq/airbyte/pull/68380) | Update dependencies |
| 0.0.21 | 2025-10-14 | [67823](https://github.com/airbytehq/airbyte/pull/67823) | Update dependencies |
| 0.0.20 | 2025-10-07 | [67495](https://github.com/airbytehq/airbyte/pull/67495) | Update dependencies |
| 0.0.19 | 2025-09-30 | [66417](https://github.com/airbytehq/airbyte/pull/66417) | Update dependencies |
| 0.0.18 | 2025-09-09 | [65829](https://github.com/airbytehq/airbyte/pull/65829) | Update dependencies |
| 0.0.17 | 2025-08-23 | [65187](https://github.com/airbytehq/airbyte/pull/65187) | Update dependencies |
| 0.0.16 | 2025-08-16 | [64969](https://github.com/airbytehq/airbyte/pull/64969) | Update dependencies |
| 0.0.15 | 2025-08-02 | [64199](https://github.com/airbytehq/airbyte/pull/64199) | Update dependencies |
| 0.0.14 | 2025-07-26 | [63923](https://github.com/airbytehq/airbyte/pull/63923) | Update dependencies |
| 0.0.13 | 2025-07-19 | [63391](https://github.com/airbytehq/airbyte/pull/63391) | Update dependencies |
| 0.0.12 | 2025-07-12 | [63244](https://github.com/airbytehq/airbyte/pull/63244) | Update dependencies |
| 0.0.11 | 2025-07-05 | [62560](https://github.com/airbytehq/airbyte/pull/62560) | Update dependencies |
| 0.0.10 | 2025-06-28 | [62357](https://github.com/airbytehq/airbyte/pull/62357) | Update dependencies |
| 0.0.9 | 2025-06-21 | [61908](https://github.com/airbytehq/airbyte/pull/61908) | Update dependencies |
| 0.0.8 | 2025-06-14 | [61029](https://github.com/airbytehq/airbyte/pull/61029) | Update dependencies |
| 0.0.7 | 2025-05-24 | [60496](https://github.com/airbytehq/airbyte/pull/60496) | Update dependencies |
| 0.0.6 | 2025-05-10 | [60141](https://github.com/airbytehq/airbyte/pull/60141) | Update dependencies |
| 0.0.5 | 2025-05-03 | [59497](https://github.com/airbytehq/airbyte/pull/59497) | Update dependencies |
| 0.0.4 | 2025-04-27 | [59042](https://github.com/airbytehq/airbyte/pull/59042) | Update dependencies |
| 0.0.3 | 2025-04-19 | [58484](https://github.com/airbytehq/airbyte/pull/58484) | Update dependencies |
| 0.0.2 | 2025-04-12 | [57892](https://github.com/airbytehq/airbyte/pull/57892) | Update dependencies |
| 0.0.1 | 2025-04-09 | [57546](https://github.com/airbytehq/airbyte/pull/57546) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
