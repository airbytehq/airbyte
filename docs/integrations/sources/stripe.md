# Stripe

## Overview

The Stripe source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Output schema

This Source is capable of syncing the following core Streams:

* [Balance Transactions](https://stripe.com/docs/api/balance_transactions/list) \(Incremental\)
* [Bank accounts](https://stripe.com/docs/api/customer_bank_accounts/list)
* [Charges](https://stripe.com/docs/api/charges/list) \(Incremental\)
* [Checkout Streams](https://stripe.com/docs/api/checkout/sessions/list) 
* [Checkout Streams Line Items](https://stripe.com/docs/api/checkout/sessions/line_items)
* [Coupons](https://stripe.com/docs/api/coupons/list) \(Incremental\)
* [Customer Balance Transactions](https://stripe.com/docs/api/customer_balance_transactions/list)
* [Customers](https://stripe.com/docs/api/customers/list) \(Incremental\)
* [Disputes](https://stripe.com/docs/api/disputes/list) \(Incremental\)
* [Events](https://stripe.com/docs/api/events/list) \(Incremental\)
* [Invoice Items](https://stripe.com/docs/api/invoiceitems/list) \(Incremental\)
* [Invoice Line Items](https://stripe.com/docs/api/invoices/invoice_lines)
* [Invoices](https://stripe.com/docs/api/invoices/list) \(Incremental\)
* [PaymentIntents](https://stripe.com/docs/api/payment_intents/list) \(Incremental\)
* [Payouts](https://stripe.com/docs/api/payouts/list) \(Incremental\)
* [Promotion Code](https://stripe.com/docs/api/promotion_codes/list) \(Incremental\)
* [Plans](https://stripe.com/docs/api/plans/list) \(Incremental\)
* [Products](https://stripe.com/docs/api/products/list) \(Incremental\)
* [Refunds](https://stripe.com/docs/api/refunds/list) \(Incremental\)
* [Subscription Items](https://stripe.com/docs/api/subscription_items/list)
* [Subscriptions](https://stripe.com/docs/api/subscriptions/list) \(Incremental\)
* [Transfers](https://stripe.com/docs/api/transfers/list) \(Incremental\)

### Note on Incremental Syncs

The Stripe API does not allow querying objects which were updated since the last sync. Therefore, this connector uses the `created` field to query for new data in your Stripe account.

### Data type mapping

The [Stripe API](https://stripe.com/docs/api) uses the same [JSONSchema](https://json-schema.org/understanding-json-schema/reference/index.html) types that Airbyte uses internally \(`string`, `date-time`, `object`, `array`, `boolean`, `integer`, and `number`\), so no type conversions happen as part of this source.

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |
| Incremental - Dedupe Sync | Yes |
| SSL connection | Yes |
| Namespaces | No |

### Performance considerations

The Stripe connector should not run into Stripe API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Stripe `Account ID` - the `Account ID` of your [Stripe Account](https://dashboard.stripe.com/settings/account)
* Stripe `Secret Key` - the `Secret Key` to be used with [authorized API calls](https://dashboard.stripe.com/apikeys) to retrieve your Stripe data. 
* `Lookback Window (in days)` (Optional) - the value in days, which allows you to sync your data with shift equals to the number of days set. If your data is updated after creation, you can use the this option to always reload data from the past N days. This allows you to pick up updates to the data. 
Example usage: `Start Date` is set to "2021-01-01T00:00:00Z" then:
    * Default is 0, meaning data will be synced from the `Start Date`.
    * 1 - means (`Start Date` - 1 day), so the start point of the sync will be "2020-12-31T00:00:00Z"
    * 7 - means (`Start Date` - 7 days) then `Start Date` will be "2020-12-25T00:00:00Z"
    * 30 - means (`Start Date` - 30 days) then `Start Date` will be "2020-12-02T00:00:00Z"
        

### Setup guide

Visit the [Stripe API Keys page](https://dashboard.stripe.com/apikeys) in the Stripe dashboard to access the secret key for your account. Secret keys for the live Stripe environment will be prefixed with `sk_live_`or `rk_live`.

We recommend creating a restricted key specifically for Airbyte access. This will allow you to control which resources Airbyte should be able to access. For ease of use, we recommend using read permissions for all resources and configuring which resource to replicate in the Airbyte UI.

If you would like to test Airbyte using test data on Stripe, `sk_test_` and `rk_test_` API keys are also supported.

## Changelog

| Version | Date       | Pull Request | Subject |
|:--------|:-----------| :--- |:---------|
| 0.1.32  | 2022-04-30 | [12500](https://github.com/airbytehq/airbyte/pull/12500) | Improve input configuration copy                                                             |
| 0.1.31  | 2022-04-20 | [12230](https://github.com/airbytehq/airbyte/pull/12230) | Update connector to use a `spec.yaml`                                                               |
| 0.1.30  | 2022-03-21 | [11286](https://github.com/airbytehq/airbyte/pull/11286) | Minor corrections to documentation and connector specification |
| 0.1.29  | 2022-03-08 | [10359](https://github.com/airbytehq/airbyte/pull/10359) | Improved performance for streams with substreams: invoice_line_items, subscription_items, bank_accounts |
| 0.1.28  | 2022-02-08 | [10165](https://github.com/airbytehq/airbyte/pull/10165) | Improve 404 handling for `CheckoutSessionsLineItems` stream                                             |
| 0.1.27  | 2021-12-28 | [9148](https://github.com/airbytehq/airbyte/pull/9148) | Fix `date`, `arrival\_date` fields                                                                      |
| 0.1.26  | 2021-12-21 | [8992](https://github.com/airbytehq/airbyte/pull/8992) | Fix type `events.request` in schema                                                                     |
| 0.1.25  | 2021-11-25 | [8250](https://github.com/airbytehq/airbyte/pull/8250) | Rearrange setup fields                                                                                  |
| 0.1.24  | 2021-11-08 | [7729](https://github.com/airbytehq/airbyte/pull/7729) | Include tax data in `checkout_sessions_line_items` stream                                               |
| 0.1.23  | 2021-11-08 | [7729](https://github.com/airbytehq/airbyte/pull/7729) | Correct `payment_intents` schema                                                                        |
| 0.1.22  | 2021-11-05 | [7345](https://github.com/airbytehq/airbyte/pull/7345) | Add 3 new streams                                                                                       |
| 0.1.21  | 2021-10-07 | [6841](https://github.com/airbytehq/airbyte/pull/6841) | Fix missing `start_date` argument + update json files for SAT                                           |
| 0.1.20  | 2021-09-30 | [6017](https://github.com/airbytehq/airbyte/pull/6017) | Add lookback\_window\_days parameter                                                                    |
| 0.1.19  | 2021-09-27 | [6466](https://github.com/airbytehq/airbyte/pull/6466) | Use `start_date` parameter in incremental streams                                                       |
| 0.1.18  | 2021-09-14 | [6004](https://github.com/airbytehq/airbyte/pull/6004) | Fix coupons and subscriptions stream schemas by removing incorrect timestamp formatting                 |
| 0.1.17  | 2021-09-14 | [6004](https://github.com/airbytehq/airbyte/pull/6004) | Add `PaymentIntents` stream                                                                             |
| 0.1.16  | 2021-07-28 | [4980](https://github.com/airbytehq/airbyte/pull/4980) | Remove Updated field from schemas                                                                       |
| 0.1.15  | 2021-07-21 | [4878](https://github.com/airbytehq/airbyte/pull/4878) | Fix incorrect percent\_off and discounts data filed types                                               |
| 0.1.14  | 2021-07-09 | [4669](https://github.com/airbytehq/airbyte/pull/4669) | Subscriptions Stream now returns all kinds of subscriptions \(including expired and canceled\)          |
| 0.1.13  | 2021-07-03 | [4528](https://github.com/airbytehq/airbyte/pull/4528) | Remove regex for acc validation                                                                         |
| 0.1.12  | 2021-06-08 | [3973](https://github.com/airbytehq/airbyte/pull/3973) | Add `AIRBYTE_ENTRYPOINT` for Kubernetes support                                                         |
| 0.1.11  | 2021-05-30 | [3744](https://github.com/airbytehq/airbyte/pull/3744) | Fix types in schema                                                                                     |
| 0.1.10  | 2021-05-28 | [3728](https://github.com/airbytehq/airbyte/pull/3728) | Update data types to be number instead of int                                                           |
| 0.1.9   | 2021-05-13 | [3367](https://github.com/airbytehq/airbyte/pull/3367) | Add acceptance tests for connected accounts                                                             |
| 0.1.8   | 2021-05-11 | [3566](https://github.com/airbytehq/airbyte/pull/3368) | Bump CDK connectors                                                                                     |

