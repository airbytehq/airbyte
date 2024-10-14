# Zoho Inventory
The Zoho Inventory connector  enables seamless data synchronization between Zoho Inventory and your data pipelines. It facilitates the automatic extraction of key inventory data such as items, orders, vendors, and invoices, ensuring up-to-date insights for analytics and reporting. Perfect for streamlining inventory management with minimal manual effort

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `domain` | `string` | Domain. The domain suffix for the Zoho Inventory API based on your data center location (e.g., &#39;com&#39;, &#39;eu&#39;, &#39;in&#39;, etc.) | com |
| `client_id` | `string` | OAuth Client ID.  |  |
| `client_secret` | `string` | OAuth Client Secret.  |  |
| `refresh_token` | `string` | OAuth Refresh Token.  |  |

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
| packages | package_id | DefaultPaginator | ✅ |  ❌  |
| invoices | invoice_id | DefaultPaginator | ✅ |  ❌  |
| purchaseorders | purchaseorder_id | DefaultPaginator | ✅ |  ❌  |
| creditnotes | creditnote_id | DefaultPaginator | ✅ |  ❌  |
| users | user_id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-14 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>