# Shopware
Shopware source connector

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Client ID.  |  |
| `client_secret` | `string` | Client secret.  |  |
| `base_url` | `string` | Base Url.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Customer List |  | DefaultPaginator | ✅ |  ❌  |
| Customer Address List |  | DefaultPaginator | ✅ |  ❌  |
| Customer Group List |  | DefaultPaginator | ✅ |  ❌  |
| Customer WishList  |  | DefaultPaginator | ✅ |  ❌  |
| Customer Wishlist Product |  | DefaultPaginator | ✅ |  ❌  |
| Delivery Time Resources |  | DefaultPaginator | ✅ |  ❌  |
| Document Resources |  | DefaultPaginator | ✅ |  ❌  |
| Order List |  | DefaultPaginator | ✅ |  ❌  |
| Order Addreses |  | DefaultPaginator | ✅ |  ❌  |
| Order Customer List |  | DefaultPaginator | ✅ |  ❌  |
| Order Delivery List |  | DefaultPaginator | ✅ |  ❌  |
| Order Delivery Positions |  | DefaultPaginator | ✅ |  ❌  |
| Order Line Items |  | DefaultPaginator | ✅ |  ❌  |
| Order Transactions |  | DefaultPaginator | ✅ |  ❌  |
| Products |  | DefaultPaginator | ✅ |  ❌  |
| Product Reviews |  | DefaultPaginator | ✅ |  ❌  |
| Countries |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-21 | | Initial release by [@Harmaton](https://github.com/Harmaton) via Connector Builder |

</details>
