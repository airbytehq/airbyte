# e-conomic
The Airbyte connector for e-conomic enables seamless integration with the e-conomic accounting platform. It allows users to efficiently extract financial data such as invoices, accounts, customers, and transactions from e-conomic and sync it to your preferred data warehouse or analytics tool. This connector simplifies data flow management, facilitating automated data extraction for comprehensive financial reporting and analysis.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `app_secret_token` | `string` | App Secret Token. Your private token that identifies your app. Find it in your e-conomic account settings. |  |
| `agreement_grant_token` | `string` | Agreement Grant Token. Token that identifies the grant issued by an agreement, allowing your app to access data. Obtain it from your e-conomic account settings. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| accounts | accountNumber | DefaultPaginator | ✅ |  ❌  |
| accounting_years | year | DefaultPaginator | ✅ |  ❌  |
| app_roles | roleNumber | DefaultPaginator | ✅ |  ❌  |
| currencies | code | DefaultPaginator | ✅ |  ❌  |
| customer_groups | customerGroupNumber | DefaultPaginator | ✅ |  ❌  |
| customers | customerNumber | DefaultPaginator | ✅ |  ❌  |
| departmental_distributions | departmentalDistributionNumber | DefaultPaginator | ✅ |  ❌  |
| departments | departmentNumber | DefaultPaginator | ✅ |  ❌  |
| employees | employeeNumber | DefaultPaginator | ✅ |  ❌  |
| journals | journalNumber | DefaultPaginator | ✅ |  ❌  |
| payment_terms | paymentTermsNumber | DefaultPaginator | ✅ |  ❌  |
| payment_types | paymentTypeNumber | DefaultPaginator | ✅ |  ❌  |
| product_groups | productGroupNumber | DefaultPaginator | ✅ |  ❌  |
| products | productNumber | DefaultPaginator | ✅ |  ❌  |
| draft_quotes | quoteNumber | DefaultPaginator | ✅ |  ❌  |
| suppliers | supplierNumber | DefaultPaginator | ✅ |  ❌  |
| units | unitNumber | DefaultPaginator | ✅ |  ❌  |
| vat_accounts | vatCode | DefaultPaginator | ✅ |  ❌  |
| vat_types | vatTypeNumber | DefaultPaginator | ✅ |  ❌  |
| vat_zones | vatZoneNumber | DefaultPaginator | ✅ |  ❌  |
| sent_quotes | quoteNumber | DefaultPaginator | ✅ |  ❌  |
| archived_quotes | quoteNumber | DefaultPaginator | ✅ |  ❌  |
| draft_invoices | draftInvoiceNumber | DefaultPaginator | ✅ |  ❌  |
| booked_invoices | bookedInvoiceNumber | DefaultPaginator | ✅ |  ❌  |
| paid_invoices | bookedInvoiceNumber | DefaultPaginator | ✅ |  ❌  |
| overdue_invoices | bookedInvoiceNumber | DefaultPaginator | ✅ |  ❌  |
| unpaid_invoices | bookedInvoiceNumber | DefaultPaginator | ✅ |  ❌  |
| not_due_invoices | bookedInvoiceNumber | DefaultPaginator | ✅ |  ❌  |
| total_invoices |  | DefaultPaginator | ✅ |  ❌  |
| sent_invoices | id | DefaultPaginator | ✅ |  ❌  |
| draft_orders | orderNumber | DefaultPaginator | ✅ |  ❌  |
| sent_orders | orderNumber | DefaultPaginator | ✅ |  ❌  |
| archived_orders | orderNumber | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.24 | 2025-06-14 | [61217](https://github.com/airbytehq/airbyte/pull/61217) | Update dependencies |
| 0.0.23 | 2025-05-24 | [60403](https://github.com/airbytehq/airbyte/pull/60403) | Update dependencies |
| 0.0.22 | 2025-05-10 | [60005](https://github.com/airbytehq/airbyte/pull/60005) | Update dependencies |
| 0.0.21 | 2025-05-03 | [59437](https://github.com/airbytehq/airbyte/pull/59437) | Update dependencies |
| 0.0.20 | 2025-04-26 | [58838](https://github.com/airbytehq/airbyte/pull/58838) | Update dependencies |
| 0.0.19 | 2025-04-19 | [58340](https://github.com/airbytehq/airbyte/pull/58340) | Update dependencies |
| 0.0.18 | 2025-04-12 | [57786](https://github.com/airbytehq/airbyte/pull/57786) | Update dependencies |
| 0.0.17 | 2025-04-05 | [57227](https://github.com/airbytehq/airbyte/pull/57227) | Update dependencies |
| 0.0.16 | 2025-03-29 | [56508](https://github.com/airbytehq/airbyte/pull/56508) | Update dependencies |
| 0.0.15 | 2025-03-22 | [55982](https://github.com/airbytehq/airbyte/pull/55982) | Update dependencies |
| 0.0.14 | 2025-03-08 | [55306](https://github.com/airbytehq/airbyte/pull/55306) | Update dependencies |
| 0.0.13 | 2025-03-01 | [54982](https://github.com/airbytehq/airbyte/pull/54982) | Update dependencies |
| 0.0.12 | 2025-02-22 | [54440](https://github.com/airbytehq/airbyte/pull/54440) | Update dependencies |
| 0.0.11 | 2025-02-15 | [53766](https://github.com/airbytehq/airbyte/pull/53766) | Update dependencies |
| 0.0.10 | 2025-02-08 | [53362](https://github.com/airbytehq/airbyte/pull/53362) | Update dependencies |
| 0.0.9 | 2025-02-01 | [52858](https://github.com/airbytehq/airbyte/pull/52858) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52336](https://github.com/airbytehq/airbyte/pull/52336) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51645](https://github.com/airbytehq/airbyte/pull/51645) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51139](https://github.com/airbytehq/airbyte/pull/51139) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50551](https://github.com/airbytehq/airbyte/pull/50551) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50016](https://github.com/airbytehq/airbyte/pull/50016) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49523](https://github.com/airbytehq/airbyte/pull/49523) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49165](https://github.com/airbytehq/airbyte/pull/49165) | Update dependencies |
| 0.0.1 | 2024-10-28 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
