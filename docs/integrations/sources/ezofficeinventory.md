# EZOfficeInventory
A manifest only source for EZOfficeInventory. https://ezo.io/ezofficeinventory/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your EZOfficeInventory Access Token. API Access is disabled by default. Enable API Access in Settings &gt; Integrations &gt; API Integration and click on Update to generate a new access token |  |
| `subdomain` | `string` | Subdomain. The company name used in signup, also visible in the URL when logged in. |  |
| `start_date` | `string` | Start date. Earliest date you want to sync historical streams (inventory_histories, asset_histories, asset_stock_histories) from |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| inventories | identifier | DefaultPaginator | ✅ |  ❌  |
| assets | identifier | DefaultPaginator | ✅ |  ❌  |
| checked_out_assets | identifier | DefaultPaginator | ✅ |  ❌  |
| asset_stocks | identifier | DefaultPaginator | ✅ |  ❌  |
| members | id | DefaultPaginator | ✅ |  ❌  |
| locations | id | DefaultPaginator | ✅ |  ❌  |
| groups | id | DefaultPaginator | ✅ |  ❌  |
| subgroups | id | DefaultPaginator | ✅ |  ❌  |
| vendors | id | DefaultPaginator | ✅ |  ❌  |
| labels | id | DefaultPaginator | ✅ |  ❌  |
| custom_fields | id | DefaultPaginator | ✅ |  ❌  |
| purchase_orders | id | DefaultPaginator | ✅ |  ❌  |
| bundles |  | DefaultPaginator | ✅ |  ❌  |
| carts |  | DefaultPaginator | ✅ |  ❌  |
| inventory_histories |  | DefaultPaginator | ✅ |  ✅  |
| asset_histories |  | DefaultPaginator | ✅ |  ✅  |
| asset_stock_histories |  | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                   |
|---------|------------|----------------------------------------------------------|-------------------------------------------------------------------------------------------|
| 0.0.12 | 2025-02-01 | [52805](https://github.com/airbytehq/airbyte/pull/52805) | Update dependencies |
| 0.0.11 | 2025-01-25 | [51698](https://github.com/airbytehq/airbyte/pull/51698) | Update dependencies |
| 0.0.10 | 2025-01-11 | [51095](https://github.com/airbytehq/airbyte/pull/51095) | Update dependencies |
| 0.0.9 | 2024-12-28 | [50580](https://github.com/airbytehq/airbyte/pull/50580) | Update dependencies |
| 0.0.8 | 2024-12-21 | [50054](https://github.com/airbytehq/airbyte/pull/50054) | Update dependencies |
| 0.0.7 | 2024-12-14 | [49506](https://github.com/airbytehq/airbyte/pull/49506) | Update dependencies |
| 0.0.6 | 2024-12-12 | [49164](https://github.com/airbytehq/airbyte/pull/49164) | Update dependencies |
| 0.0.5 | 2024-12-11 | [48932](https://github.com/airbytehq/airbyte/pull/48932) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.4 | 2024-11-04 | [48180](https://github.com/airbytehq/airbyte/pull/48180) | Update dependencies |
| 0.0.3 | 2024-10-29 | [47913](https://github.com/airbytehq/airbyte/pull/47913) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47535](https://github.com/airbytehq/airbyte/pull/47535) | Update dependencies |
| 0.0.1 | 2024-09-15 | [45590](https://github.com/airbytehq/airbyte/pull/45590) | Initial release by [@pabloescoder](https://github.com/pabloescoder) via Connector Builder |

</details>
