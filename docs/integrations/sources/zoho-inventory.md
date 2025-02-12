# Zoho Inventory
The Zoho Inventory connector  enables seamless data synchronization between Zoho Inventory and your data pipelines. It facilitates the automatic extraction of key inventory data such as items, orders, vendors, and invoices, ensuring up-to-date insights for analytics and reporting. Perfect for streamlining inventory management with minimal manual effort

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | OAuth Client ID.  |  |
| `client_secret` | `string` | OAuth Client Secret.  |  |
| `refresh_token` | `string` | OAuth Refresh Token.  |  |
| `domain` | `string` | Domain. The domain suffix for the Zoho Inventory API based on your data center location (e.g., `com`, `eu`, `in`, etc.) | com |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| items | item_id | DefaultPaginator | ✅ |  ❌  |
| item_groups | group_id | DefaultPaginator | ✅ |  ❌  |
| organizations | organization_id | DefaultPaginator | ✅ |  ❌  |
| contacts | contact_id | DefaultPaginator | ✅ |  ❌  |
| itemadjustments | inventory_adjustment_id | DefaultPaginator | ✅ |  ❌  |
| warehouses | warehouse_id | DefaultPaginator | ✅ |  ❌  |
| transferorders | transfer_order_id | DefaultPaginator | ✅ |  ❌  |
| salesorders | salesorder_id | DefaultPaginator | ✅ |  ❌  |
| packages | package_id | DefaultPaginator | ✅ |  ✅  |
| invoices | invoice_id | DefaultPaginator | ✅ |  ✅  |
| purchaseorders | purchaseorder_id | DefaultPaginator | ✅ |  ❌  |
| creditnotes | creditnote_id | DefaultPaginator | ✅ |  ❌  |
| users | user_id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.11 | 2025-02-08 | [53602](https://github.com/airbytehq/airbyte/pull/53602) | Update dependencies |
| 0.0.10 | 2025-02-01 | [53120](https://github.com/airbytehq/airbyte/pull/53120) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52555](https://github.com/airbytehq/airbyte/pull/52555) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51934](https://github.com/airbytehq/airbyte/pull/51934) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51466](https://github.com/airbytehq/airbyte/pull/51466) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50834](https://github.com/airbytehq/airbyte/pull/50834) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50389](https://github.com/airbytehq/airbyte/pull/50389) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49448](https://github.com/airbytehq/airbyte/pull/49448) | Update dependencies |
| 0.0.3 | 2024-10-29 | [47862](https://github.com/airbytehq/airbyte/pull/47862) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47605](https://github.com/airbytehq/airbyte/pull/47605) | Update dependencies |
| 0.0.1 | 2024-10-19 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
