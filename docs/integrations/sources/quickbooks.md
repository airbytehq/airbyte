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

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

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
| :--------------- | :----------- | :---- |
| `string`         | `string`     |       |
| `number`         | `number`     |       |
| `array`          | `array`      |       |
| `object`         | `object`     |       |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version     | Date       | Pull Request                                             | Subject                                                            |
|:------------|:-----------|:---------------------------------------------------------| :----------------------------------------------------------------- |
| 4.0.2 | 2025-02-23 | [54573](https://github.com/airbytehq/airbyte/pull/54573) | Update dependencies |
| 4.0.1 | 2025-02-15 | [46789](https://github.com/airbytehq/airbyte/pull/46789) | Update dependencies |
| 4.0.0 | 2025-01-18 | [51615](https://github.com/airbytehq/airbyte/pull/51615) | Remove nested credentials object from config to enable overwriting of new refresh token in config |
| 3.0.26 | 2024-11-01 | [48089](https://github.com/airbytehq/airbyte/pull/48089) | Promoting release candidate 3.0.26-rc.1 to a main version. |
| 3.0.26-rc.1 | 2024-09-10 | [44560](https://github.com/airbytehq/airbyte/pull/44560) | Replace Custom Components with Airbyte CDK features                |
| 3.0.25      | 2024-10-05 | [46424](https://github.com/airbytehq/airbyte/pull/46424) | Update dependencies                                                |
| 3.0.24      | 2024-09-28 | [46142](https://github.com/airbytehq/airbyte/pull/46142) | Update dependencies                                                |
| 3.0.23      | 2024-09-21 | [45727](https://github.com/airbytehq/airbyte/pull/45727) | Update dependencies                                                |
| 3.0.22      | 2024-09-14 | [45517](https://github.com/airbytehq/airbyte/pull/45517) | Update dependencies                                                |
| 3.0.21      | 2024-09-07 | [45231](https://github.com/airbytehq/airbyte/pull/45231) | Update dependencies                                                |
| 3.0.20      | 2024-08-31 | [44961](https://github.com/airbytehq/airbyte/pull/44961) | Update dependencies                                                |
| 3.0.19      | 2024-08-24 | [44713](https://github.com/airbytehq/airbyte/pull/44713) | Update dependencies                                                |
| 3.0.18      | 2024-08-17 | [44282](https://github.com/airbytehq/airbyte/pull/44282) | Update dependencies                                                |
| 3.0.17      | 2024-08-12 | [43829](https://github.com/airbytehq/airbyte/pull/43829) | Update dependencies                                                |
| 3.0.16      | 2024-08-10 | [43563](https://github.com/airbytehq/airbyte/pull/43563) | Update dependencies                                                |
| 3.0.15      | 2024-08-03 | [43052](https://github.com/airbytehq/airbyte/pull/43052) | Update dependencies                                                |
| 3.0.14      | 2024-07-27 | [42666](https://github.com/airbytehq/airbyte/pull/42666) | Update dependencies                                                |
| 3.0.13      | 2024-07-20 | [42358](https://github.com/airbytehq/airbyte/pull/42358) | Update dependencies                                                |
| 3.0.12      | 2024-07-13 | [41745](https://github.com/airbytehq/airbyte/pull/41745) | Update dependencies                                                |
| 3.0.11      | 2024-07-10 | [41414](https://github.com/airbytehq/airbyte/pull/41414) | Update dependencies                                                |
| 3.0.10      | 2024-07-10 | [41325](https://github.com/airbytehq/airbyte/pull/41325) | Update dependencies                                                |
| 3.0.9       | 2024-07-09 | [40660](https://github.com/airbytehq/airbyte/pull/40660) | Fix configured catalog, inline schemas                             |
| 3.0.8       | 2024-07-06 | [40885](https://github.com/airbytehq/airbyte/pull/40885) | Update dependencies                                                |
| 3.0.7       | 2024-06-25 | [40355](https://github.com/airbytehq/airbyte/pull/40355) | Update dependencies                                                |
| 3.0.6       | 2024-06-22 | [39955](https://github.com/airbytehq/airbyte/pull/39955) | Update dependencies                                                |
| 3.0.5       | 2024-06-06 | [39285](https://github.com/airbytehq/airbyte/pull/39285) | [autopull] Upgrade base image to v1.2.2                            |
| 3.0.4       | 2024-05-21 | [38518](https://github.com/airbytehq/airbyte/pull/38518) | [autopull] base image + poetry + up_to_date                        |
| `3.0.3`     | 2024-03-22 | [36389](https://github.com/airbytehq/airbyte/pull/36389) | Add refresh token updater and add missing properties to streams    |
| `3.0.2`     | 2024-02-20 | [32236](https://github.com/airbytehq/airbyte/pull/32236) | Small typo in spec correction                                      |
| `3.0.1`     | 2023-11-06 | [32236](https://github.com/airbytehq/airbyte/pull/32236) | Upgrade to `airbyte-cdk>=0.52.10` to resolve refresh token issues  |
| `3.0.0`     | 2023-09-26 | [30770](https://github.com/airbytehq/airbyte/pull/30770) | Update schema to use `number` instead of `integer`                 |
| `2.0.5`     | 2023-09-26 | [30766](https://github.com/airbytehq/airbyte/pull/30766) | Fix improperly named keyword argument                              |
| `2.0.4`     | 2023-06-28 | [27803](https://github.com/airbytehq/airbyte/pull/27803) | Update following state breaking changes                            |
| `2.0.3`     | 2023-06-08 | [27148](https://github.com/airbytehq/airbyte/pull/27148) | Update description and example values of a Start Date in spec.json |
| `2.0.2`     | 2023-06-07 | [26722](https://github.com/airbytehq/airbyte/pull/27053) | Update CDK version and adjust authenticator configuration          |
| `2.0.1`     | 2023-05-28 | [26722](https://github.com/airbytehq/airbyte/pull/26722) | Change datatype for undisclosed amount field in payments           |
| `2.0.0`     | 2023-04-11 | [25045](https://github.com/airbytehq/airbyte/pull/25045) | Fix datetime format, disable OAuth button in cloud                 |
| `1.0.0`     | 2023-03-20 | [24324](https://github.com/airbytehq/airbyte/pull/24324) | Migrate to Low-Code                                                |
| `0.1.5`     | 2022-02-17 | [10346](https://github.com/airbytehq/airbyte/pull/10346) | Update label `Quickbooks` -> `QuickBooks`                          |
| `0.1.4`     | 2021-12-20 | [8960](https://github.com/airbytehq/airbyte/pull/8960)   | Update connector fields title/description                          |
| `0.1.3`     | 2021-08-10 | [4986](https://github.com/airbytehq/airbyte/pull/4986)   | Using number data type for decimal fields instead string           |
| `0.1.2`     | 2021-07-06 | [4539](https://github.com/airbytehq/airbyte/pull/4539)   | Add `AIRBYTE_ENTRYPOINT` for Kubernetes support                    |

</details>
