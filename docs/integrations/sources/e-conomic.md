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
| 0.0.1 | 2024-10-28 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
