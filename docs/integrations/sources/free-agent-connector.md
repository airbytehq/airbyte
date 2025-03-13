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
| 0.0.15 | 2025-03-01 | [54967](https://github.com/airbytehq/airbyte/pull/54967) | Update dependencies |
| 0.0.14 | 2025-02-22 | [54376](https://github.com/airbytehq/airbyte/pull/54376) | Update dependencies |
| 0.0.13 | 2025-02-15 | [53738](https://github.com/airbytehq/airbyte/pull/53738) | Update dependencies |
| 0.0.12 | 2025-02-08 | [53309](https://github.com/airbytehq/airbyte/pull/53309) | Update dependencies |
| 0.0.11 | 2025-02-01 | [52815](https://github.com/airbytehq/airbyte/pull/52815) | Update dependencies |
| 0.0.10 | 2025-01-25 | [52312](https://github.com/airbytehq/airbyte/pull/52312) | Update dependencies |
| 0.0.9 | 2025-01-18 | [51628](https://github.com/airbytehq/airbyte/pull/51628) | Update dependencies |
| 0.0.8 | 2025-01-11 | [51068](https://github.com/airbytehq/airbyte/pull/51068) | Update dependencies |
| 0.0.7 | 2024-12-28 | [50557](https://github.com/airbytehq/airbyte/pull/50557) | Update dependencies |
| 0.0.6 | 2024-12-21 | [50043](https://github.com/airbytehq/airbyte/pull/50043) | Update dependencies |
| 0.0.5 | 2024-12-14 | [49537](https://github.com/airbytehq/airbyte/pull/49537) | Update dependencies |
| 0.0.4 | 2024-12-12 | [49183](https://github.com/airbytehq/airbyte/pull/49183) | Update dependencies |
| 0.0.3 | 2024-11-04 | [48277](https://github.com/airbytehq/airbyte/pull/48277) | Update dependencies |
| 0.0.2 | 2024-10-29 | [47874](https://github.com/airbytehq/airbyte/pull/47874) | Update dependencies |
| 0.0.1 | 2024-09-24 | | Initial release by [@craigbloodworth](https://github.com/craigbloodworth) via Connector Builder |

</details>
