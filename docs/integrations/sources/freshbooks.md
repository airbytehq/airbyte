# FreshBooks
FreshBooks connector  seamlessly syncs invoicing, expenses, and client data from FreshBooks into data warehouses or analytics platforms. 

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Client ID.  |  |
| `client_secret` | `string` | Client secret.  |  |
| `redirect_uri` | `string` | Redirect Uri.  |  |
| `account_id` | `string` | Account Id.  |  |
| `client_refresh_token` | `string` | Refresh token.  |  |
| `oauth_access_token` | `string` | Access token. The current access token. This field might be overridden by the connector based on the token refresh endpoint response. |  |
| `oauth_token_expiry_date` | `string` | Token expiry date. The date the current access token expires in. This field might be overridden by the connector based on the token refresh endpoint response. |  |
| `business_uuid` | `string` | Business uuid.  |  |

Read [this](https://documenter.getpostman.com/view/3322108/S1ERwwza#intro) section carefully to get your Account Id and Business UUID.

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| user |  | DefaultPaginator | ✅ |  ❌  |
| clients |  | DefaultPaginator | ✅ |  ❌  |
| invoices | id.invoiceid | DefaultPaginator | ✅ |  ❌  |
| expenses | id.expenseid | DefaultPaginator | ✅ |  ❌  |
| expense_summaries |  | DefaultPaginator | ✅ |  ❌  |
| expense_categories | id | DefaultPaginator | ✅ |  ❌  |
| invoice_details | invoiceid | DefaultPaginator | ✅ |  ❌  |
| expense_details | expenseid | DefaultPaginator | ✅ |  ❌  |
| accounts |  | DefaultPaginator | ✅ |  ❌  |
| taxes | taxid | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.7 | 2025-01-11 | [51087](https://github.com/airbytehq/airbyte/pull/51087) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50525](https://github.com/airbytehq/airbyte/pull/50525) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50000](https://github.com/airbytehq/airbyte/pull/50000) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49498](https://github.com/airbytehq/airbyte/pull/49498) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49209](https://github.com/airbytehq/airbyte/pull/49209) | Update dependencies |
| 0.0.2 | 2024-12-11 | [48942](https://github.com/airbytehq/airbyte/pull/48942) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-10-27 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
