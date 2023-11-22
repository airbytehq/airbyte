# QuickBooks

This page contains the setup guide and reference information for QuickBooks.

## Prerequisites

* Intuit Developer account
* OAuth2.0 credentials (Client ID, Client secret, Refresh token, Access token, Token expiry date, Realm id)

## Features

| Feature | Supported? |
| --- | --- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| Namespaces | No |

## Setup guide

### Step 1: Create a QuickBooks Application

1. Create an [Intuit Developer account](https://developer.intuit.com/app/developer/qbo/docs/get-started)

2. Visit your [Intuit Developer Dashboard](https://developer.intuit.com/app/developer/dashboard).

3. Click **Create an application**, give your app a name, and select the scopes of the APIs you would like to access.

### Step 2: Obtain QuickBooks credentials

1. The easiest way to get these credentials is by using [Quickbook's OAuth 2.0 playground](https://developer.intuit.com/app/developer/qbo/docs/develop/authentication-and-authorization/oauth-2.0-playground).

2. From the **Select app** dropdown, select one of your **sandbox** companies. Copy your **Client Id** and **Client Secret**. You will use them when creating the source in Daspire.

3. In the **Scopes** section, select one or more scopes.

4. Click **Get authorization code**. If asked, select Connect to connect your app to the OAuth Playground.

5. Review and copy the auto-generated **Authorization code** and **Realm ID**. The authorization code is based on your app’s scopes.

6. Click **Get tokens**. Copy the **Access Token**, **Refresh Token**, and **Realm ID**.

7. Review the sample request and response.

### Step 3: Set up QuickBooks in Daspire

1. Select **QuickBooks** from the Source list.

2. Enter a **Source Name**.

3. Enter the **Client ID** - The OAuth2.0 application ID you obtained in Step 2.

4. Enter the **Client Secret** - The OAuth2.0 application secret you obtained in Step 2.

5. Enter the **Refresh Token** you obtained in Step 2.

6. Enter the **Access Token** you obtained in Step 2.

7. Enter the **Token Expiry Date** - DateTime when the access token becomes invalid.

8. Enter the **Realm ID** - The Labeled Company ID you'd like to replicate data for streams you obtained in Step 2.

9. Enter the **Start date** - The date starting from which you'd like to replicate data.

10. **Sandbox** - Turn on if you're going to replicate the data from the sandbox environment.

11. Click **Save & Test**.

## Supported streams

This source is capable of syncing the following streams:

* [Accounts](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/account)
* [BillPayments](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/billpayment)
* [Budgets](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/budget)
* [Bills](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/bill)
* [Classes](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/class)
* [CreditMemos](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/creditmemo)
* [Customers](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/customer)
* [Departments](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/department)
* [Deposits](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/deposit)
* [Employees](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/employee)
* [Estimates](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/estimate)
* [Invoices](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/invoice)
* [Items](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/item)
* [JournalEntries](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/journalentry)
* [Payments](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/payment)
* [PaymentMethods](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/paymentmethod)
* [Purchases](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/purchase)
* [PurchaseOrders](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/purchaseorder)
* [RefundReceipts](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/refundreceipt)
* [SalesReceipts](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/salesreceipt)
* [TaxAgencies](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/taxagency)
* [TaxCodes](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/taxcode)
* [TaxRates](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/taxrate)
* [Terms](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/term)
* [TimeActivities](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/timeactivity)
* [Transfers](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/transfer)
* [VendorCredits](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/vendorcredit)
* [Vendors](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/vendor)

## Data type mapping

| Integration Type | Daspire Type |
| --- | --- |
| `string` | `string` |
| `number` | `number` |
| `array` | `array` |
| `object` | `object` |

## Troubleshooting

Max number of tables that can be synced at a time is 6,000. We advise you to adjust your settings if it fails to fetch schema due to max number of tables reached.
