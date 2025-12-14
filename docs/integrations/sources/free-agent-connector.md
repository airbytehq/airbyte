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
| Project Notes | | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.1.5 | 2025-12-09 | [70538](https://github.com/airbytehq/airbyte/pull/70538) | Update dependencies |
| 0.1.4 | 2025-11-25 | [69969](https://github.com/airbytehq/airbyte/pull/69969) | Update dependencies |
| 0.1.3 | 2025-11-18 | [69467](https://github.com/airbytehq/airbyte/pull/69467) | Update dependencies |
| 0.1.2 | 2025-10-29 | [68832](https://github.com/airbytehq/airbyte/pull/68832) | Update dependencies |
| 0.1.1 | 2025-10-21 | [68451](https://github.com/airbytehq/airbyte/pull/68451) | Update dependencies |
| 0.1.0 | 2025-10-07 | [67023](https://github.com/airbytehq/airbyte/pull/67023) | Added Project Notes stream and reworked Payslips stream to use payroll periods as parent instead of accounting periods. Non-breaking change |
| 0.0.37 | 2025-10-14 | [68060](https://github.com/airbytehq/airbyte/pull/68060) | Update dependencies |
| 0.0.36 | 2025-10-07 | [67306](https://github.com/airbytehq/airbyte/pull/67306) | Update dependencies |
| 0.0.35 | 2025-09-30 | [66763](https://github.com/airbytehq/airbyte/pull/66763) | Update dependencies |
| 0.0.34 | 2025-09-24 | [65887](https://github.com/airbytehq/airbyte/pull/65887) | Update dependencies |
| 0.0.33 | 2025-08-23 | [65265](https://github.com/airbytehq/airbyte/pull/65265) | Update dependencies |
| 0.0.32 | 2025-08-09 | [64775](https://github.com/airbytehq/airbyte/pull/64775) | Update dependencies |
| 0.0.31 | 2025-08-02 | [64373](https://github.com/airbytehq/airbyte/pull/64373) | Update dependencies |
| 0.0.30 | 2025-07-26 | [64041](https://github.com/airbytehq/airbyte/pull/64041) | Update dependencies |
| 0.0.29 | 2025-07-19 | [63553](https://github.com/airbytehq/airbyte/pull/63553) | Update dependencies |
| 0.0.28 | 2025-07-12 | [63010](https://github.com/airbytehq/airbyte/pull/63010) | Update dependencies |
| 0.0.27 | 2025-07-05 | [62801](https://github.com/airbytehq/airbyte/pull/62801) | Update dependencies |
| 0.0.26 | 2025-06-28 | [62334](https://github.com/airbytehq/airbyte/pull/62334) | Update dependencies |
| 0.0.25 | 2025-06-21 | [61979](https://github.com/airbytehq/airbyte/pull/61979) | Update dependencies |
| 0.0.24 | 2025-06-14 | [61257](https://github.com/airbytehq/airbyte/pull/61257) | Update dependencies |
| 0.0.23 | 2025-05-24 | [60351](https://github.com/airbytehq/airbyte/pull/60351) | Update dependencies |
| 0.0.22 | 2025-05-10 | [59418](https://github.com/airbytehq/airbyte/pull/59418) | Update dependencies |
| 0.0.21 | 2025-04-26 | [58845](https://github.com/airbytehq/airbyte/pull/58845) | Update dependencies |
| 0.0.20 | 2025-04-19 | [58357](https://github.com/airbytehq/airbyte/pull/58357) | Update dependencies |
| 0.0.19 | 2025-04-12 | [57826](https://github.com/airbytehq/airbyte/pull/57826) | Update dependencies |
| 0.0.18 | 2025-04-05 | [57259](https://github.com/airbytehq/airbyte/pull/57259) | Update dependencies |
| 0.0.17 | 2025-03-29 | [56515](https://github.com/airbytehq/airbyte/pull/56515) | Update dependencies |
| 0.0.16 | 2025-03-22 | [55342](https://github.com/airbytehq/airbyte/pull/55342) | Update dependencies |
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
