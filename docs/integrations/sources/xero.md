# Xero

This is a setup guide for the Xero source connector which ingests data from the Accounting API.

## Prerequisites

First of all you should create an application in [Xero development center](https://developer.xero.com/app/manage/). The only supported integration type is to use [Xero Custom Connections](https://developer.xero.com/documentation/guides/oauth2/custom-connections/developer) so you should choose it on creating your Xero App.
After creating an application, on configuration screen, authorize user for your Xero Organisation. Also, issue new Client Secret and remember it - it will be required for setting up Xero connector in your Airbyte instance.

## Supported streams

[Accounts](https://developer.xero.com/documentation/api/accounting/accounts)
[BankTransactions](https://developer.xero.com/documentation/api/accounting/banktransactions)
[BankTransfers](https://developer.xero.com/documentation/api/accounting/banktransfers)
[BrandingThemes](https://developer.xero.com/documentation/api/accounting/brandingthemes)
[ContactGroups](https://developer.xero.com/documentation/api/accounting/contactgroups)
[Contacts](https://developer.xero.com/documentation/api/accounting/contacts)
[CreditNotes](https://developer.xero.com/documentation/api/accounting/creditnotes)
[Currencies](https://developer.xero.com/documentation/api/accounting/currencies)
[Employees](https://developer.xero.com/documentation/api/accounting/employees)
[Invoices](https://developer.xero.com/documentation/api/accounting/invoices)
[Items](https://developer.xero.com/documentation/api/accounting/items)
[ManualJournals](https://developer.xero.com/documentation/api/accounting/manualjournals)
[Organisation](https://developer.xero.com/documentation/api/accounting/organisation)
[Overpayments](https://developer.xero.com/documentation/api/accounting/overpayments)
[Payments](https://developer.xero.com/documentation/api/accounting/payments)
[Prepayments](https://developer.xero.com/documentation/api/accounting/prepayments)
[PurchaseOrders](https://developer.xero.com/documentation/api/accounting/purchaseorders)
[RepeatingInvoices](https://developer.xero.com/documentation/api/accounting/repeatinginvoices)
[TaxRates](https://developer.xero.com/documentation/api/accounting/taxrates)
[TrackingCategories](https://developer.xero.com/documentation/api/accounting/trackingcategories)
[Users](https://developer.xero.com/documentation/api/accounting/users)

### Dates transformation

As Xero uses .NET, some date fields in records could be in [.NET JSON date format](https://developer.xero.com/documentation/api/accounting/requests-and-responses). These dates are transformed into ISO 8601.

## Set up the Xero source connector

1. Click **Sources** and then click **+ New source**.
2. On the Set up the source page, select **Xerp** from the Source type dropdown.
3. Enter a name for your new source.
4. For **Client ID**, enter Client ID of your Xero App.
5. For **Client Secret**, enter a Client Secret created on "Configuration" screen of your Xero App
6. For **Tenant ID** field, enter your Xero Organisation's [Tenant ID](https://developer.xero.com/documentation/guides/oauth2/auth-flow/#xero-tenants)
7. For **Scopes** field enter scopes you used for user's authorization on "Configuration" screen of your Xero App
8. Choose **Custom Connections Authentication** as **Authentication** option
9. For **Start date** enter UTC date and time in the format `YYYY-MM-DDTHH:mm:ssZ` as the start date and time of ingestion.
10. Click **Set up source**.

## Supported sync modes

The source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh
- Incremental

## Changelog

| Version | Date       | Pull Request                                             | Subject                           |
| :------ | :--------- | :------------------------------------------------------- | :-------------------------------- |
| 0.1.0   | 2021-11-11 | [18666](https://github.com/airbytehq/airbyte/pull/18666) | 🎉 New Source - Xero [python cdk] |
