# Ebay
The eBay connector  enables seamless data synchronization between eBay&#39;s platform and various data destinations, helping users extract eBay listings, orders, inventory, and marketing data in real time. It supports various eBay APIs, including the Inventory and Marketing APIs, allowing businesses to streamline operations, monitor sales, and analyze product performance efficiently.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `authorization_credentials` | `string` | Authorization credentials.  |  |
| `marketplace_id` | `string` | Marketplace Id.  |  |
| `refresh_token` | `string` | Refresh Token.  |  |
| `evaluation_type` | `string` | Evaluation Type.  |  |
| `evaluation_marketplace` | `string` | Evaluation Marketplaces.  |  |
| `environment` | `string` | Environment.  | `api.sandbox` or `production` |
| `charity_registration_ids` | `string` | Charity Registration Ids.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| inventory_items | sku | DefaultPaginator | ✅ |  ❌  |
| offers |  | DefaultPaginator | ✅ |  ❌  |
| violation_summary |  | DefaultPaginator | ✅ |  ❌  |
| customer_service_metric |  | No pagination | ✅ |  ❌  |
| order_tasks | taskId | DefaultPaginator | ✅ |  ❌  |
| inventory_tasks | taskId | DefaultPaginator | ✅ |  ❌  |
| charity_orgs | charityOrgId | DefaultPaginator | ✅ |  ❌  |
| get_campaigns | campaignId | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-25 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
