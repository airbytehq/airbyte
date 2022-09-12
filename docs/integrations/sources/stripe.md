# Stripe

This page guides you through the process of setting up the Stripe source connector.

## Prerequisites

- Your [Stripe `Account ID`](https://dashboard.stripe.com/settings/account)
- Your [Stripe `Secret Key`](https://dashboard.stripe.com/apikeys)

## Set up the Stripe source connector

1. Log into your [Airbyte Cloud](https://cloud.airbyte.io/workspaces) or Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**. 
3. On the Set up the source page, select **Stripe** from the Source type dropdown.
4. Enter a name for your source.
5. For **Account ID**, enter your [Stripe `Account ID`](https://dashboard.stripe.com/settings/account).
6. For **Secret Key**, enter your [Stripe `Secret Key`](https://dashboard.stripe.com/apikeys)

   We recommend creating a secret key specifically for Airbyte to control which resources Airbyte can access. For ease of use, we recommend granting read permission to all resources and configuring which resource to replicate in the Airbyte UI. You can also use the API keys for the [test mode](https://stripe.com/docs/keys#obtain-api-keys) to try out the Stripe integration with Airbyte.

7. For **Replication start date**, enter the date in YYYY-MM-DDTHH:mm:ssZ format. The data added on and after this date will be replicated. If this field is blank, Airbyte will replicate all data.
8. For **Lookback Window in days (Optional)**, select the number of days the value in days prior to the start date that you to sync your data with. If your data is updated after setting up this connector, you can use the this option to reload data from the past N days. Example: If the Replication start date is set to `2021-01-01T00:00:00Z`, then:
   - If you leave the Lookback Window in days parameter to its the default value of 0, Airbyte will sync data from the Replication start date `2021-01-01T00:00:00Z`
   - If the Lookback Window in days value is set to 1, Airbyte will consider the Replication start date to be `2020-12-31T00:00:00Z`
   - If the Lookback Window in days value is set to 7, Airbyte will sync data from `2020-12-31T00:00:00Z`
9. Click **Set up source**.

## Supported sync modes

The Stripe source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh
- Incremental

:::note
Since the Stripe API does not allow querying objects which were updated since the last sync, the Stripe connector uses the `created` field to query for new data in your Stripe account.
:::

## Supported Streams

The Stripe source connector supports the following streams:

- [Balance Transactions](https://stripe.com/docs/api/balance_transactions/list) \(Incremental\)
- [Bank accounts](https://stripe.com/docs/api/customer_bank_accounts/list)
- [Charges](https://stripe.com/docs/api/charges/list) \(Incremental\)
  - The `amount` column defaults to the smallest currency unit. (See [charge object](https://stripe.com/docs/api/charges/object) for more details)
- [Checkout Streams](https://stripe.com/docs/api/checkout/sessions/list)
- [Checkout Streams Line Items](https://stripe.com/docs/api/checkout/sessions/line_items)
- [Coupons](https://stripe.com/docs/api/coupons/list) \(Incremental\)
- [Customer Balance Transactions](https://stripe.com/docs/api/customer_balance_transactions/list)
- [Customers](https://stripe.com/docs/api/customers/list) \(Incremental\)
- [Disputes](https://stripe.com/docs/api/disputes/list) \(Incremental\)
- [Events](https://stripe.com/docs/api/events/list) \(Incremental\)
- [Invoice Items](https://stripe.com/docs/api/invoiceitems/list) \(Incremental\)
- [Invoice Line Items](https://stripe.com/docs/api/invoices/invoice_lines)
- [Invoices](https://stripe.com/docs/api/invoices/list) \(Incremental\)
- [PaymentIntents](https://stripe.com/docs/api/payment_intents/list) \(Incremental\)
- [Payouts](https://stripe.com/docs/api/payouts/list) \(Incremental\)
- [Promotion Code](https://stripe.com/docs/api/promotion_codes/list) \(Incremental\)
- [Plans](https://stripe.com/docs/api/plans/list) \(Incremental\)
- [Products](https://stripe.com/docs/api/products/list) \(Incremental\)
- [Refunds](https://stripe.com/docs/api/refunds/list) \(Incremental\)
- [Subscription Items](https://stripe.com/docs/api/subscription_items/list)
- [Subscriptions](https://stripe.com/docs/api/subscriptions/list) \(Incremental\)
- [Transfers](https://stripe.com/docs/api/transfers/list) \(Incremental\)

### Data type mapping

The [Stripe API](https://stripe.com/docs/api) uses the same [JSONSchema](https://json-schema.org/understanding-json-schema/reference/index.html) types that Airbyte uses internally \(`string`, `date-time`, `object`, `array`, `boolean`, `integer`, and `number`\), so no type conversions are performed for the Stripe connector.

### Performance considerations

The Stripe connector should not run into Stripe API limitations under normal usage. [Create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                                                                                |
|:--------|:-----------|:---------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0.1.37  | 2022-08-16 | [15686](https://github.com/airbytehq/airbyte/pull/15686) | Fixed the bug when the stream couldn't be fetched due to limited permission set, if so - it should be skipped                                                                                                                                 |
| 0.1.36  | 2022-08-04 | [15292](https://github.com/airbytehq/airbyte/pull/15292) | Implement slicing                                                                                                                                      |
| 0.1.35  | 2022-07-21 | [14924](https://github.com/airbytehq/airbyte/pull/14924) | Remove `additionalProperties` field from spec and schema                                                                                               |
| 0.1.34  | 2022-07-01 | [14357](https://github.com/airbytehq/airbyte/pull/14357) | added external account streams -                                                                                                                       |
| 0.1.33  | 2022-06-06 | [13449](https://github.com/airbytehq/airbyte/pull/13449) | added semi-incremental support for CheckoutSessions and CheckoutSessionsLineItems streams, fixed big in StripeSubStream, added unittests, updated docs |
| 0.1.32  | 2022-04-30 | [12500](https://github.com/airbytehq/airbyte/pull/12500) | Improve input configuration copy                                                                                                                       |
| 0.1.31  | 2022-04-20 | [12230](https://github.com/airbytehq/airbyte/pull/12230) | Update connector to use a `spec.yaml`                                                                                                                  |
| 0.1.30  | 2022-03-21 | [11286](https://github.com/airbytehq/airbyte/pull/11286) | Minor corrections to documentation and connector specification                                                                                         |
| 0.1.29  | 2022-03-08 | [10359](https://github.com/airbytehq/airbyte/pull/10359) | Improved performance for streams with substreams: invoice_line_items, subscription_items, bank_accounts                                                |
| 0.1.28  | 2022-02-08 | [10165](https://github.com/airbytehq/airbyte/pull/10165) | Improve 404 handling for `CheckoutSessionsLineItems` stream                                                                                            |
| 0.1.27  | 2021-12-28 | [9148](https://github.com/airbytehq/airbyte/pull/9148)   | Fix `date`, `arrival\_date` fields                                                                                                                     |
| 0.1.26  | 2021-12-21 | [8992](https://github.com/airbytehq/airbyte/pull/8992)   | Fix type `events.request` in schema                                                                                                                    |
| 0.1.25  | 2021-11-25 | [8250](https://github.com/airbytehq/airbyte/pull/8250)   | Rearrange setup fields                                                                                                                                 |
| 0.1.24  | 2021-11-08 | [7729](https://github.com/airbytehq/airbyte/pull/7729)   | Include tax data in `checkout_sessions_line_items` stream                                                                                              |
| 0.1.23  | 2021-11-08 | [7729](https://github.com/airbytehq/airbyte/pull/7729)   | Correct `payment_intents` schema                                                                                                                       |
| 0.1.22  | 2021-11-05 | [7345](https://github.com/airbytehq/airbyte/pull/7345)   | Add 3 new streams                                                                                                                                      |
| 0.1.21  | 2021-10-07 | [6841](https://github.com/airbytehq/airbyte/pull/6841)   | Fix missing `start_date` argument + update json files for SAT                                                                                          |
| 0.1.20  | 2021-09-30 | [6017](https://github.com/airbytehq/airbyte/pull/6017)   | Add lookback_window_days parameter                                                                                                                     |
| 0.1.19  | 2021-09-27 | [6466](https://github.com/airbytehq/airbyte/pull/6466)   | Use `start_date` parameter in incremental streams                                                                                                      |
| 0.1.18  | 2021-09-14 | [6004](https://github.com/airbytehq/airbyte/pull/6004)   | Fix coupons and subscriptions stream schemas by removing incorrect timestamp formatting                                                                |
| 0.1.17  | 2021-09-14 | [6004](https://github.com/airbytehq/airbyte/pull/6004)   | Add `PaymentIntents` stream                                                                                                                            |
| 0.1.16  | 2021-07-28 | [4980](https://github.com/airbytehq/airbyte/pull/4980)   | Remove Updated field from schemas                                                                                                                      |
| 0.1.15  | 2021-07-21 | [4878](https://github.com/airbytehq/airbyte/pull/4878)   | Fix incorrect percent_off and discounts data filed types                                                                                               |
| 0.1.14  | 2021-07-09 | [4669](https://github.com/airbytehq/airbyte/pull/4669)   | Subscriptions Stream now returns all kinds of subscriptions \(including expired and canceled\)                                                         |
| 0.1.13  | 2021-07-03 | [4528](https://github.com/airbytehq/airbyte/pull/4528)   | Remove regex for acc validation                                                                                                                        |
| 0.1.12  | 2021-06-08 | [3973](https://github.com/airbytehq/airbyte/pull/3973)   | Add `AIRBYTE_ENTRYPOINT` for Kubernetes support                                                                                                        |
| 0.1.11  | 2021-05-30 | [3744](https://github.com/airbytehq/airbyte/pull/3744)   | Fix types in schema                                                                                                                                    |
| 0.1.10  | 2021-05-28 | [3728](https://github.com/airbytehq/airbyte/pull/3728)   | Update data types to be number instead of int                                                                                                          |
| 0.1.9   | 2021-05-13 | [3367](https://github.com/airbytehq/airbyte/pull/3367)   | Add acceptance tests for connected accounts                                                                                                            |
| 0.1.8   | 2021-05-11 | [3566](https://github.com/airbytehq/airbyte/pull/3368)   | Bump CDK connectors                                                                                                                                    |
