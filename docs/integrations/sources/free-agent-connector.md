# FreeAgent Connector
Download all your data from FreeAgent, a friendly and easy to use cloud based accounting service

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Client ID.  |  |
| `client_secret` | `string` | Client secret.  |  |
| `client_refresh_token_2` | `string` | Refresh token.  |  |
| `updated_since` | `string` | Updated Since.  |  |
| `payroll_year` | `number` | Payroll Year.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Users | url | DefaultPaginator | ✅ |  ❌  |
| Admin Expenses Categories | url | DefaultPaginator | ✅ |  ❌  |
| Cost of Sales Categories | url | DefaultPaginator | ✅ |  ❌  |
| Income Categories | url | DefaultPaginator | ✅ |  ❌  |
| General Categories | url | DefaultPaginator | ✅ |  ❌  |
| Balance Sheet |  | No pagination | ✅ |  ❌  |
| Bank Accounts | url | No pagination | ✅ |  ❌  |
| Bank Transaction Explanations | url | DefaultPaginator | ✅ |  ✅  |
| Bank Transactions | url | DefaultPaginator | ✅ |  ✅  |
| Bills | url | DefaultPaginator | ✅ |  ✅  |
| Company Tax Timeline |  | No pagination | ✅ |  ❌  |
| Contacts | url | DefaultPaginator | ✅ |  ❌  |
| Corporation Tax Returns | url | DefaultPaginator | ✅ |  ❌  |
| Credit Note Reconciliations |  | DefaultPaginator | ✅ |  ✅  |
| Credit Notes |  | DefaultPaginator | ✅ |  ✅  |
| Estimates | url | DefaultPaginator | ✅ |  ✅  |
| Expenses | url | DefaultPaginator | ✅ |  ✅  |
| Final Accounts Reports | url | DefaultPaginator | ✅ |  ❌  |
| Hire Purchases | url | DefaultPaginator | ✅ |  ❌  |
| Invoices | url | DefaultPaginator | ✅ |  ✅  |
| Journal Sets | url | DefaultPaginator | ✅ |  ❌  |
| Contact Notes |  | DefaultPaginator | ✅ |  ❌  |
| Payroll Periods | url | No pagination | ✅ |  ❌  |
| Company | url | No pagination | ✅ |  ❌  |
| Annual Accounting Periods |  | No pagination | ✅ |  ❌  |
| Payslips |  | DefaultPaginator | ✅ |  ❌  |
| Price List Items | url | DefaultPaginator | ✅ |  ❌  |
| Profit &amp; Loss Summary |  | No pagination | ✅ |  ❌  |
| Projects | url | DefaultPaginator | ✅ |  ✅  |
| Tasks | url | DefaultPaginator | ✅ |  ✅  |
| Timeslips | url | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.1 | 2024-09-24 | | Initial release by [@craigbloodworth](https://github.com/craigbloodworth) via Connector Builder |

</details>