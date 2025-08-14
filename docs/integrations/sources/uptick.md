# Uptick
Extract data from Uptick - The new standard in
fire inspection software.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `base_url` | `string` | Base Url. Ex: https://demo-fire.onuptick.com/ |  |
| `client_id` | `string` | Client ID.  |  |
| `client_secret` | `string` | Client secret.  |  |
| `client_refresh_token` | `string` | Refresh token.  |  |
| `oauth_access_token` | `string` | Access token. The current access token. This field might be overridden by the connector based on the token refresh endpoint response. |  |
| `oauth_token_expiry_date` | `string` | Token expiry date. The date the current access token expires in. This field might be overridden by the connector based on the token refresh endpoint response. |  |
| `start_date` | `string` | Start Date. Fetch data starting from this date (by default 2025-01-01) | 2025-01-01 |
| `end_date` | `string` | End Date. Fetch data up until this date |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| tasks | id | DefaultPaginator | ✅ |  ❌  |
| taskcategories | id | DefaultPaginator | ✅ |  ❌  |
| clients | id | DefaultPaginator | ✅ |  ❌  |
| clientgroups | id | DefaultPaginator | ✅ |  ❌  |
| properties | id | DefaultPaginator | ✅ |  ❌  |
| taskprofitability | id | No pagination | ✅ |  ❌  |
| invoices | id | DefaultPaginator | ✅ |  ❌  |
| projects | id | DefaultPaginator | ✅ |  ❌  |
| servicequotes | id | DefaultPaginator | ✅ |  ❌  |
| defectquotes | id | DefaultPaginator | ✅ |  ❌  |
| suppliers | id | DefaultPaginator | ✅ |  ❌  |
| purchaseorders | id | DefaultPaginator | ✅ |  ❌  |
| assets | id | DefaultPaginator | ✅ |  ❌  |
| routines | id | DefaultPaginator | ✅ |  ❌  |
| billingcard | id | DefaultPaginator | ✅ |  ❌  |
| purchaseorderbills | id | DefaultPaginator | ✅ |  ❌  |
| purchaseorderdockets | id | DefaultPaginator | ✅ |  ❌  |
| invoicelineitems |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.10 | 2025-08-14 | [64942](https://github.com/airbytehq/airbyte/pull/64942) | Fix docker image entrypoint for platform syncs |
| 0.0.9 | 2025-08-13 | [64170](https://github.com/airbytehq/airbyte/pull/64170) | adds cursor pagination, incremental sync and rate limiting |
| 0.0.8 | 2025-08-09 | [64845](https://github.com/airbytehq/airbyte/pull/64845) | Update dependencies |
| 0.0.7 | 2025-08-02 | [64403](https://github.com/airbytehq/airbyte/pull/64403) | Update dependencies |
| 0.0.6 | 2025-07-26 | [64055](https://github.com/airbytehq/airbyte/pull/64055) | Update dependencies |
| 0.0.5 | 2025-07-20 | [63685](https://github.com/airbytehq/airbyte/pull/63685) | Update dependencies |
| 0.0.4 | 2025-07-12 | [63165](https://github.com/airbytehq/airbyte/pull/63165) | Update dependencies |
| 0.0.3 | 2025-07-05 | [62739](https://github.com/airbytehq/airbyte/pull/62739) | Update dependencies |
| 0.0.2 | 2025-06-28 | [62220](https://github.com/airbytehq/airbyte/pull/62220) | Update dependencies |
| 0.0.1 | 2025-06-10 | | Initial release by [@sajarin](https://github.com/sajarin) via Connector Builder |

</details>
