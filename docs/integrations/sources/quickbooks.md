# Quickbooks

## Overview

The Mixpanel source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This source wraps the [Singer Quickbooks Tap](https://github.com/singer-io/tap-quickbooks).

### Output schema

This Source is capable of syncing the following [Streams](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/most-commonly-used/account):

* Accounts
* BillPayments
* Budgets
* Bills
* Classes
* CreditMemos
* Customers
* Departments
* Deposits
* Employees
* Estimates
* Invoices
* Items
* JournalEntries
* Payments
* PaymentMethods
* Purchases
* PurchaseOrders
* RefundReceipts
* SalesReceipts
* TaxAgencies
* TaxCodes
* TaxRates
* Terms
* TimeActivities
* Transfers
* VendorCredits
* Vendors

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| `string` | `string` |  |
| `number` | `number` |  |
| `array` | `array` |  |
| `object` | `object` |  |

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | Yes |  |
| SSL connection | Yes |  |

## Getting started

1. Create an [Intuit Developer account](https://developer.intuit.com/app/developer/qbo/docs/get-started)
2. Create an app
3. Obtain credentials

### Requirements
* Client ID
* Client Secret
* Realm ID
* Refresh token

To simplify obtaining credential process you can use [OAuth 2.0 playground](https://developer.intuit.com/app/developer/qbo/docs/develop/authentication-and-authorization/oauth-2.0-playground)

