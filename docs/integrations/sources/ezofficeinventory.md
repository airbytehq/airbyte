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
| 0.0.1   | 2024-09-15 | [45590](https://github.com/airbytehq/airbyte/pull/45590) | Initial release by [@pabloescoder](https://github.com/pabloescoder) via Connector Builder |

</details>