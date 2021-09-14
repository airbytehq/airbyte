# Stripe

## Overview

The Stripe source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Output schema

This Source is capable of syncing the following core Streams:

* [Balance Transactions](https://stripe.com/docs/api/balance_transactions/list) \(Incremental\)
* [Bank accounts](https://stripe.com/docs/api/customer_bank_accounts/list)
* [Charges](https://stripe.com/docs/api/charges/list) \(Incremental\)
* [Coupons](https://stripe.com/docs/api/coupons/list) \(Incremental\)
* [Customer Balance Transactions](https://stripe.com/docs/api/customer_balance_transactions/list) \(Incremental\)
* [Customers](https://stripe.com/docs/api/customers/list) \(Incremental\)
* [Disputes](https://stripe.com/docs/api/disputes/list) \(Incremental\)
* [Events](https://stripe.com/docs/api/events/list) \(Incremental\)
* [Invoice Items](https://stripe.com/docs/api/invoiceitems/list) \(Incremental\)
* [Invoice Line Items](https://stripe.com/docs/api/invoices/invoice_lines)
* [Invoices](https://stripe.com/docs/api/invoices/list) \(Incremental\)
* [PaymentIntents](https://stripe.com/docs/api/payment_intents/list) \(Incremental\)
* [Payouts](https://stripe.com/docs/api/payouts/list) \(Incremental\)
* [Plans](https://stripe.com/docs/api/plans/list) \(Incremental\)
* [Products](https://stripe.com/docs/api/products/list) \(Incremental\)
* [Refunds](https://stripe.com/docs/api/refunds/list) \(Incremental\)
* [Subscription Items](https://stripe.com/docs/api/subscription_items/list)
* [Subscriptions](https://stripe.com/docs/api/subscriptions/list) \(Incremental\)
* [Transfers](https://stripe.com/docs/api/transfers/list) \(Incremental\)

### Notes

The `created` field is used to organize Incremental streams. Filtration occurs by the date the entity was created, and it is impossible to filter by the update date, since:
  * The Stripe API allows filtering only by the `created` field for all streams.
  * There is no such field as `updated`.
The only alternative way at the moment is to do a Full Refresh sync and filtering client side.

### Data type mapping

The [Stripe API](https://stripe.com/docs/api) uses the same [JSONSchema](https://json-schema.org/understanding-json-schema/reference/index.html) types that Airbyte uses internally \(`string`, `date-time`, `object`, `array`, `boolean`, `integer`, and `number`\), so no type conversions happen as part of this source.

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |
| Replicate Incremental Deletes | Coming soon |
| SSL connection | Yes |
| Namespaces | No |

### Performance considerations

The Stripe connector should not run into Stripe API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Stripe Account
* Stripe API Secret Key

### Setup guide

Visit the [Stripe API Keys page](https://dashboard.stripe.com/apikeys) in the Stripe dashboard to access the secret key for your account. Secret keys for the live Stripe environment will be prefixed with `sk_live_`or `rk_live`.

We recommend creating a restricted key specifically for Airbyte access. This will allow you to control which resources Airbyte should be able to access. For ease of use, we recommend using read permissions for all resources and configuring which resource to replicate in the Airbyte UI.

If you would like to test Airbyte using test data on Stripe, `sk_test_` and `rk_test_` API keys are also supported.

## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.1.17   | 2021-09-14 | [6004](https://github.com/airbytehq/airbyte/pull/6004) | Add `PaymentIntents` stream |
| 0.1.16   | 2021-07-28 | [4980](https://github.com/airbytehq/airbyte/pull/4980) | Remove Updated field from schemas |
| 0.1.15   | 2021-07-21 | [4878](https://github.com/airbytehq/airbyte/pull/4878) | Fix incorrect percent_off and discounts data filed types|
| 0.1.14   | 2021-07-09 | [4669](https://github.com/airbytehq/airbyte/pull/4669) | Subscriptions Stream now returns all kinds of subscriptions (including expired and canceled)|
| 0.1.13   | 2021-07-03 | [4528](https://github.com/airbytehq/airbyte/pull/4528) | Remove regex for acc validation |
| 0.1.12   | 2021-06-08 | [3973](https://github.com/airbytehq/airbyte/pull/3973) | Add `AIRBYTE_ENTRYPOINT` for Kubernetes support |
| 0.1.11   | 2021-05-30 | [3744](https://github.com/airbytehq/airbyte/pull/3744) | Fix types in schema |
| 0.1.10   | 2021-05-28 | [3728](https://github.com/airbytehq/airbyte/pull/3728) | Update data types to be number instead of int |
| 0.1.9   | 2021-05-13 | [3367](https://github.com/airbytehq/airbyte/pull/3367) | Add acceptance tests for connected accounts |
| 0.1.8   | 2021-05-11 | [3566](https://github.com/airbytehq/airbyte/pull/3368) | Bump CDK connectors |
