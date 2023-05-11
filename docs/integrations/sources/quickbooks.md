# QuickBooks

This page contains the setup guide and reference information for the QuickBooks Source connector.

## Prerequisites

- [Intuit QuickBooks account](https://quickbooks.intuit.com/global/)
- [Intuit Developer account](https://developer.intuit.com/app/developer/qbo/docs/get-started)
- OAuth2.0 credentials (see [OAuth 2.0 playground](https://developer.intuit.com/app/developer/qbo/docs/develop/authentication-and-authorization/oauth-2.0-playground))
- Realm ID

## Setup guide

### Step 1: Set up QuickBooks

1. Create an [Intuit Developer account](https://developer.intuit.com/app/developer/qbo/docs/get-started)
2. Create an application
3. Obtain credentials. The easiest way to get these credentials is by using Quickbook's [OAuth 2.0 playground](https://developer.intuit.com/app/developer/qbo/docs/develop/authentication-and-authorization/oauth-2.0-playground)

### Step 2: Set up the QuickBooks connector in Airbyte

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **QuickBooks** from the Source type dropdown and enter a name for this connector.
4. **Client ID** - The OAuth2.0 application ID
5. **Client Secret** - The OAuth2.0 application secret
6. **Refresh Token** - Refresh token used to get new access token every time the current one is expired
7. **Access Token** - Access token to perform authenticated API calls with
8. **Token Expiry Date** - DateTime when the access token becomes invalid
9. **Realm ID** - The Labeled [Company ID](https://developer.intuit.com/app/developer/qbo/docs/learn/learn-basic-field-definitions#realm-id) you'd like to replicate data for streams.
10. **Start date** - The date starting from which you'd like to replicate data.
11. **Sandbox** - Turn on if you're going to replicate the data from the sandbox environment.
12. Click **Set up source**.

<!-- /env:cloud -->

<!-- env:oss -->
**For Airbyte Open Source:**

1. **Client ID** - The OAuth2.0 application ID
2. **Client Secret** - The OAuth2.0 application secret
3. **Refresh Token** - Refresh token used to get new access token every time the current one is expired
4. **Access Token** - Access token to perform authenticated API calls with
5. **Token Expiry Date** - DateTime when the access token becomes invalid
6. **Realm ID** - The Labeled [Company ID](https://developer.intuit.com/app/developer/qbo/docs/learn/learn-basic-field-definitions#realm-id) you'd like to replicate data for streams.
7. **Start date** - The date starting from which you'd like to replicate data.
8. **Sandbox** - Turn on if you're going to replicate the data from the sandbox environment.
<!-- /env:oss -->

## Supported sync modes

The Quickbooks Source connector supports the following [ sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

* [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
* [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
* [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
* [Incremental - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history)

## Supported Streams

This Source is capable of syncing the following [Streams](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/most-commonly-used/account):

- [Accounts](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/account)
- [BillPayments](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/billpayment)
- [Budgets](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/budget)
- [Bills](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/bill)
- [Classes](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/class)
- [CreditMemos](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/creditmemo)
- [Customers](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/customer)
- [Departments](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/department)
- [Deposits](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/deposit)
- [Employees](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/employee)
- [Estimates](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/estimate)
- [Invoices](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/invoice)
- [Items](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/item)
- [JournalEntries](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/journalentry)
- [Payments](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/payment)
- [PaymentMethods](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/paymentmethod)
- [Purchases](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/purchase)
- [PurchaseOrders](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/purchaseorder)
- [RefundReceipts](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/refundreceipt)
- [SalesReceipts](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/salesreceipt)
- [TaxAgencies](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/taxagency)
- [TaxCodes](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/taxcode)
- [TaxRates](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/taxrate)
- [Terms](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/term)
- [TimeActivities](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/timeactivity)
- [Transfers](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/transfer)
- [VendorCredits](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/vendorcredit)
- [Vendors](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/vendor)

## Data type map

| Integration Type | Airbyte Type | Notes |
|:-----------------|:-------------|:------|
| `string`         | `string`     |       |
| `number`         | `number`     |       |
| `array`          | `array`      |       |
| `object`         | `object`     |       |

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                  |
|:--------|:-----------|:---------------------------------------------------------|:---------------------------------------------------------|
| `2.0.0` | 2023-04-11 | [25045](https://github.com/airbytehq/airbyte/pull/25045) | Fix datetime format, disable OAuth button in cloud       |
| `1.0.0` | 2023-03-20 | [24324](https://github.com/airbytehq/airbyte/pull/24324) | Migrate to Low-Code                                      |
| `0.1.5` | 2022-02-17 | [10346](https://github.com/airbytehq/airbyte/pull/10346) | Update label `Quickbooks` -> `QuickBooks`                |
| `0.1.4` | 2021-12-20 | [8960](https://github.com/airbytehq/airbyte/pull/8960)   | Update connector fields title/description                |
| `0.1.3` | 2021-08-10 | [4986](https://github.com/airbytehq/airbyte/pull/4986)   | Using number data type for decimal fields instead string |
| `0.1.2` | 2021-07-06 | [4539](https://github.com/airbytehq/airbyte/pull/4539)   | Add `AIRBYTE_ENTRYPOINT` for Kubernetes support          |
