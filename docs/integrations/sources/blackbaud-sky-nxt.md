# Blackbaud SKY NXT
Connector Blackbaud NXT via SKY API

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Client ID. The Application ID from your registered SKY application |  |
| `start_date` | `string` | Start Date. UTC date and time in the format 2020-01-01T00:00:00Z. Data modified after this date will be replicated. |  |
| `client_secret` | `string` | Client Secret. The Application secret from your registered SKY application |  |
| `subscription_key` | `string` | Subscription Key. Your SKY API subscription key (primary or secondary) |  |
| `client_access_token` | `string` | Access Token.  |  |
| `client_refresh_token` | `string` | Refresh Token.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| constituents | id | DefaultPaginator | ✅ |  ✅  |
| actions | id | DefaultPaginator | ✅ |  ✅  |
| addresses | id | DefaultPaginator | ✅ |  ✅  |
| phones | id | DefaultPaginator | ✅ |  ✅  |
| emailaddresses | id | DefaultPaginator | ✅ |  ✅  |
| relationships | id | DefaultPaginator | ✅ |  ✅  |
| notes | id | DefaultPaginator | ✅ |  ✅  |
| customfields | id | DefaultPaginator | ✅ |  ✅  |
| constituentcodes | id | DefaultPaginator | ✅ |  ✅  |
| gifts | id | DefaultPaginator | ✅ |  ✅  |
| giftcustomfields | id | DefaultPaginator | ✅ |  ✅  |
| opportunities | id | DefaultPaginator | ✅ |  ✅  |
| campaigns | id | DefaultPaginator | ✅ |  ✅  |
| funds | id | DefaultPaginator | ✅ |  ✅  |
| appeals | id | DefaultPaginator | ✅ |  ✅  |
| available_codetables | code_tables_id | DefaultPaginator | ✅ |  ❌  |
| codetable_solicitcodes | table_entries_id | DefaultPaginator | ✅ |  ❌  |
| query_incremental | Gift ID | No pagination | ✅ |  ✅  |
| query_generic |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-09-12 | | Initial release by [@allandelmare](https://github.com/allandelmare) via Connector Builder |

</details>
