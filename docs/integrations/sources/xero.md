# Xero

This page contains the setup guide and reference information for the Xero source connector.

## Prerequisites

- Tenant ID
- Start Date

<!-- env:cloud -->
**For Airbyte Cloud:**

- OAuth 2.0
<!-- /env:cloud -->

<!-- env:oss -->
**For Airbyte Open Source:**

- Client ID
- Client Secret
- Refresh Token
- Access Token
- Token Expiry Date
<!-- /env:oss -->

## Setup guide

### Step 1: Set up Xero

<!-- env:cloud -->
### Step 2: Set up the Xero connector in Airbyte

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **Xero** from the Source type dropdown and enter a name for this connector.
4. Click `Authenticate your Xero account`.
5. Log in and `Allow access`.
6. **Tenant ID** - Enter your Xero Organisation's [Tenant ID](https://developer.xero.com/documentation/guides/oauth2/auth-flow/#xero-tenants)
7. **Start Date** - UTC date and time in the format `YYYY-MM-DDTHH:mm:ssZ` from which you'd like to replicate data.
<!-- /env:cloud -->

<!-- env:oss -->
**For Airbyte Open Source:**

1. Create an application in [Xero development center](https://developer.xero.com/app/manage/).
<!-- /env:oss -->

## Supported sync modes

The Xero source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

* [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
* [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
* [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)

## Supported streams

- [Accounts](https://developer.xero.com/documentation/api/accounting/accounts)
- [BankTransactions](https://developer.xero.com/documentation/api/accounting/banktransactions)
- [BankTransfers](https://developer.xero.com/documentation/api/accounting/banktransfers)
- [BrandingThemes](https://developer.xero.com/documentation/api/accounting/brandingthemes)
- [ContactGroups](https://developer.xero.com/documentation/api/accounting/contactgroups)
- [Contacts](https://developer.xero.com/documentation/api/accounting/contacts)
- [CreditNotes](https://developer.xero.com/documentation/api/accounting/creditnotes)
- [Currencies](https://developer.xero.com/documentation/api/accounting/currencies)
- [Employees](https://developer.xero.com/documentation/api/accounting/employees)
- [Invoices](https://developer.xero.com/documentation/api/accounting/invoices)
- [Items](https://developer.xero.com/documentation/api/accounting/items)
- [ManualJournals](https://developer.xero.com/documentation/api/accounting/manualjournals)
- [Organisation](https://developer.xero.com/documentation/api/accounting/organisation)
- [Overpayments](https://developer.xero.com/documentation/api/accounting/overpayments)
- [Payments](https://developer.xero.com/documentation/api/accounting/payments)
- [Prepayments](https://developer.xero.com/documentation/api/accounting/prepayments)
- [PurchaseOrders](https://developer.xero.com/documentation/api/accounting/purchaseorders)
- [RepeatingInvoices](https://developer.xero.com/documentation/api/accounting/repeatinginvoices)
- [TaxRates](https://developer.xero.com/documentation/api/accounting/taxrates)
- [TrackingCategories](https://developer.xero.com/documentation/api/accounting/trackingcategories)
- [Users](https://developer.xero.com/documentation/api/accounting/users)

### Dates transformation

As Xero uses .NET, some date fields in records could be in [.NET JSON date format](https://developer.xero.com/documentation/api/accounting/requests-and-responses). These dates are transformed into ISO 8601.

### Performance considerations

The connector is restricted by Xero [API rate limits](https://developer.xero.com/documentation/guides/oauth2/limits/#api-rate-limits).

## Changelog

| Version | Date       | Pull Request                                             | Subject                           |
|:--------|:-----------|:---------------------------------------------------------|:----------------------------------|
| 0.2.3   | 2023-06-19 | [27471](https://github.com/airbytehq/airbyte/pull/27471) | Update CDK to 0.40                |
| 0.2.2   | 2023-06-06 | [27007](https://github.com/airbytehq/airbyte/pull/27007) | Update CDK                        |
| 0.2.1   | 2023-03-20 | [24217](https://github.com/airbytehq/airbyte/pull/24217) | Certify to Beta                   |
| 0.2.0   | 2023-03-14 | [24005](https://github.com/airbytehq/airbyte/pull/24005) | Enable in Cloud                   |
| 0.1.0   | 2021-11-11 | [18666](https://github.com/airbytehq/airbyte/pull/18666) | 🎉 New Source - Xero [python cdk] |
