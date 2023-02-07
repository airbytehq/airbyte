# QuickBooks

## Overview

The QuickBooks source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This source wraps the [Singer QuickBooks Tap](https://github.com/singer-io/tap-quickbooks).

### Output schema

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

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--------------- | :----------- | :---- |
| `string`         | `string`     |       |
| `number`         | `number`     |       |
| `array`          | `array`      |       |
| `object`         | `object`     |       |

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | Yes                  |       |
| SSL connection    | Yes                  |       |
| Namespaces        | No                   |       |

## Getting started

1. Create an [Intuit Developer account](https://developer.intuit.com/app/developer/qbo/docs/get-started)
2. Create an app
3. Obtain credentials

### Requirements

- Client ID
- Client Secret
- Realm ID
- Refresh token

The easiest way to get these credentials is by using Quickbook's [OAuth 2.0 playground](https://developer.intuit.com/app/developer/qbo/docs/develop/authentication-and-authorization/oauth-2.0-playground)

**Important note:** The refresh token expires every 100 days. You will need to manually revisit the Oauth playground to obtain a refresh token every 100 days, or your syncs will expire. We plan on offering full Oauth support soon so you don't need to redo this process manually.

## CHANGELOG

| Version | Date       | Pull Request                                             | Subject                                                  |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------- |
| `0.1.5` | 2022-02-17 | [10346](https://github.com/airbytehq/airbyte/pull/10346) | Update label `Quickbooks` -> `QuickBooks`                |
| `0.1.4` | 2021-12-20 | [8960](https://github.com/airbytehq/airbyte/pull/8960)   | Update connector fields title/description                |
| `0.1.3` | 2021-08-10 | [4986](https://github.com/airbytehq/airbyte/pull/4986)   | Using number data type for decimal fields instead string |
| `0.1.2` | 2021-07-06 | [4539](https://github.com/airbytehq/airbyte/pull/4539)   | Add `AIRBYTE_ENTRYPOINT` for Kubernetes support          |
