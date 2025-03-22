# Salla API
Salla API connector.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | OAuth Client ID.  |  |
| `client_secret` | `string` | OAuth Client Secret.  |  |
| `client_refresh_token` | `string` | Refresh token.  |  |
| `oauth_access_token` | `string` | Access token. The current access token. This field might be overridden by the connector based on the token refresh endpoint response. |  |
| `oauth_token_expiry_date` | `string` | Token expiry date. The date the current access token expires in. This field might be overridden by the connector based on the token refresh endpoint response. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Orders |  | DefaultPaginator | ✅ |  ❌  |
| Products |  | DefaultPaginator | ✅ |  ❌  |
| Customers |  | DefaultPaginator | ✅ |  ❌  |
| Shipments |  | DefaultPaginator | ✅ |  ❌  |
| Abandoned carts |  | DefaultPaginator | ✅ |  ❌  |
| Branches |  | DefaultPaginator | ✅ |  ❌  |
| Brands |  | DefaultPaginator | ✅ |  ❌  |
| Available Payment Methods |  | DefaultPaginator | ✅ |  ❌  |
| List Banks |  | DefaultPaginator | ✅ |  ❌  |
| Taxes |  | DefaultPaginator | ✅ |  ❌  |
| List Transactions |  | DefaultPaginator | ✅ |  ❌  |
| List Special Offers |  | DefaultPaginator | ✅ |  ❌  |
| List Countries |  | DefaultPaginator | ✅ |  ❌  |
| affiliates |  | DefaultPaginator | ✅ |  ❌  |
| Affiliate Details |  | No pagination | ✅ |  ❌  |
| Transaction details |  | No pagination | ✅ |  ❌  |
| List Reviews |  | DefaultPaginator | ✅ |  ❌  |
| Review details |  | No pagination | ✅ |  ❌  |
| Shipment Details |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-03-20 | | Initial release by [@nafeal3mri](https://github.com/nafeal3mri) via Connector Builder |

</details>
