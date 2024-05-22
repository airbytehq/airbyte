# Stripe

<HideInUI>

This page contains the setup guide and reference information for the [Stripe](https://stripe.com/) source connector.

</HideInUI>

## Prerequisites

- Access to the Stripe account containing the data you wish to replicate

## Setup Guide

:::note
To authenticate the Stripe connector, you need to use a Stripe API key. Although you may use an existing key, we recommend that you create a new restricted key specifically for Airbyte and grant it **Read** privileges only. We also recommend granting **Read** privileges to all available permissions, and configuring the specific data you would like to replicate within Airbyte.
:::

### Step 1: Set up Stripe

1. Log in to your [Stripe account](https://dashboard.stripe.com/login).
2. In the top navigation bar, click **Developers**.
3. In the top-left corner, click **API keys**.
4. Click **+ Create restricted key**.
5. Choose a **Key name**, and select **Read** for all available permissions.
6. Click **Create key**. You may be prompted to enter a confirmation code sent to your email address.

For more information on Stripe API Keys, see the [Stripe documentation](https://stripe.com/docs/keys).

### Step 2: Set up the Stripe source connector in Airbyte

1. Log in to your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) account or your Airbyte Open Source account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. Find and select **Stripe** from the list of available sources.
4. For **Source name**, enter a name to help you identify this source.
5. For **Account ID**, enter your Stripe Account ID. This ID begins with `acct_`, and can be found in the top-right corner of your Stripe [account settings page](https://dashboard.stripe.com/settings/account).
6. For **Secret Key**, enter the restricted key you created for the connection.
7. For **Replication Start Date**, use the provided datepicker or enter a UTC date and time programmatically in the format `YYYY-MM-DDTHH:mm:ssZ`. The data added on and after this date will be replicated.
8. (Optional) For **Lookback Window**, you may specify a number of days from the present day to reread data. This allows the connector to retrieve data that might have been updated after its initial creation, and is useful for handling any post-transaction adjustments. This applies only to streams that do not support event-based incremental syncs, please see [the list below](#troubleshooting).

   - Leaving the **Lookback Window** at its default value of 0 means Airbyte will not re-export data after it has been synced.
   - Setting the **Lookback Window** to 1 means Airbyte will re-export data from the past day, capturing any changes made in the last 24 hours.
   - Setting the **Lookback Window** to 7 means Airbyte will re-export and capture any data changes within the last week.

9. (Optional) For **Data Request Window**, you may specify the time window in days used by the connector when requesting data from the Stripe API. This window defines the span of time covered in each request, with larger values encompassing more days in a single request. Generally speaking, the lack of overhead from making fewer requests means a larger window is faster to sync. However, this also means the state of the sync will persist less frequently. If an issue occurs or the sync is interrupted, a larger window means more data will need to be resynced, potentially causing a delay in the overall process.

   For example, if you are replicating three years worth of data:

   - A **Data Request Window** of 365 days means Airbyte makes 3 requests, each for a year. This is generally faster but risks needing to resync up to a year's data if the sync is interrupted.
   - A **Data Request Window** of 30 days means 36 requests, each for a month. This may be slower but minimizes the amount of data that needs to be resynced if an issue occurs.

   If you are unsure of which value to use, we recommend leaving this setting at its default value of 365 days.

10. Click **Set up source** and wait for the tests to complete.

<HideInUI>

## Supported sync modes

The Stripe source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh
- Incremental

## Supported streams

The Stripe source connector supports the following streams:

- [Accounts](https://stripe.com/docs/api/accounts/list)
- [Application Fees](https://stripe.com/docs/api/application_fees) \(Incremental\)
- [Application Fee Refunds](https://stripe.com/docs/api/fee_refunds/list) \(Incremental\)
- [Authorizations](https://stripe.com/docs/api/issuing/authorizations/list) \(Incremental\)
- [Balance Transactions](https://stripe.com/docs/api/balance_transactions/list) \(Incremental\)
- [Bank accounts](https://stripe.com/docs/api/customer_bank_accounts/list) \(Incremental\)
- [Cardholders](https://stripe.com/docs/api/issuing/cardholders/list) \(Incremental\)
- [Cards](https://stripe.com/docs/api/issuing/cards/list) \(Incremental\)
- [Charges](https://stripe.com/docs/api/charges/list) \(Incremental\)
  :::note
  The `amount` column defaults to the smallest currency unit. Check [the Stripe docs](https://stripe.com/docs/api/charges/object) for more details.
  :::
- [Checkout Sessions](https://stripe.com/docs/api/checkout/sessions/list) \(Incremental\)
- [Checkout Sessions Line Items](https://stripe.com/docs/api/checkout/sessions/line_items) \(Incremental\)
- [Coupons](https://stripe.com/docs/api/coupons/list) \(Incremental\)
- [Credit Notes](https://stripe.com/docs/api/credit_notes/list) \(Incremental\)
- [Customer Balance Transactions](https://stripe.com/docs/api/customer_balance_transactions/list) \(Incremental\)
- [Customers](https://stripe.com/docs/api/customers/list) \(Incremental\)
- [Disputes](https://stripe.com/docs/api/disputes/list) \(Incremental\)
- [Early Fraud Warnings](https://stripe.com/docs/api/radar/early_fraud_warnings/list) \(Incremental\)
- [Events](https://stripe.com/docs/api/events/list) \(Incremental\)
- [External Account Bank Accounts](https://stripe.com/docs/api/external_account_bank_accounts/list) \(Incremental\)
- [External Account Cards](https://stripe.com/docs/api/external_account_cards/list) \(Incremental\)
- [File Links](https://stripe.com/docs/api/file_links/list) \(Incremental\)
- [Files](https://stripe.com/docs/api/files/list) \(Incremental\)
- [Invoice Items](https://stripe.com/docs/api/invoiceitems/list) \(Incremental\)
- [Invoice Line Items](https://stripe.com/docs/api/invoices/invoice_lines)
- [Invoices](https://stripe.com/docs/api/invoices/list) \(Incremental\)
- [Payment Intents](https://stripe.com/docs/api/payment_intents/list) \(Incremental\)
- [Payment Methods](https://stripe.com/docs/api/payment_methods/list)
- [Payouts](https://stripe.com/docs/api/payouts/list) \(Incremental\)
- [Promotion Code](https://stripe.com/docs/api/promotion_codes/list) \(Incremental\)
- [Persons](https://stripe.com/docs/api/persons/list) \(Incremental\)
- [Plans](https://stripe.com/docs/api/plans/list) \(Incremental\)
- [Prices](https://stripe.com/docs/api/prices/list) \(Incremental\)
- [Products](https://stripe.com/docs/api/products/list) \(Incremental\)
- [Refunds](https://stripe.com/docs/api/refunds/list) \(Incremental\)
- [Reviews](https://stripe.com/docs/api/radar/reviews/list) \(Incremental\)
- [Setup Attempts](https://stripe.com/docs/api/setup_attempts/list) \(Incremental\)
- [Setup Intents](https://stripe.com/docs/api/setup_intents/list) \(Incremental\)
- [Shipping Rates](https://stripe.com/docs/api/shipping_rates/list) \(Incremental\)
- [Subscription Items](https://stripe.com/docs/api/subscription_items/list)
- [Subscription Schedule](https://stripe.com/docs/api/subscription_schedules) \(Incremental\)
- [Subscriptions](https://stripe.com/docs/api/subscriptions/list) \(Incremental\)
- [Top Ups](https://stripe.com/docs/api/topups/list) \(Incremental\)
- [Transactions](https://stripe.com/docs/api/transfers/list) \(Incremental\)
- [Transfers](https://stripe.com/docs/api/transfers/list) \(Incremental\)
- [Transfer Reversals](https://stripe.com/docs/api/transfer_reversals/list)
- [Usage Records](https://stripe.com/docs/api/usage_records/subscription_item_summary_list)

### Data type mapping

The [Stripe API](https://stripe.com/docs/api) uses the same [JSON Schema](https://json-schema.org/understanding-json-schema/reference/index.html) types that Airbyte uses internally \(`string`, `date-time`, `object`, `array`, `boolean`, `integer`, and `number`\), so no type conversions are performed for the Stripe connector.

## Limitations & Troubleshooting

<details>
<summary>
Expand to see details about Stripe connector limitations and troubleshooting.
</summary>

### Connector limitations

#### Rate limiting

The Stripe connector should not run into Stripe API limitations under normal usage. See Stripe [Rate limits](https://stripe.com/docs/rate-limits) documentation. [Create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

:::warning
**Stripe API Restriction on Events Data**: Access to the events endpoint is [guaranteed only for the last 30 days](https://stripe.com/docs/api/events) by Stripe. If you use the Full Refresh Overwrite sync, be aware that any events data older than 30 days will be **deleted** from your target destination and replaced with the data from the last 30 days only. Use an Append sync mode to ensure historical data is retained.
Please be aware: this also means that any change older than 30 days will not be replicated using the incremental sync mode. If you want all your synced data to remain up to date, please set up your sync frequency to no more than 30 days.
:::

### Troubleshooting

Since the Stripe API does not allow querying objects which were updated since the last sync, the Stripe connector uses the Events API under the hood to implement incremental syncs and export data based on its update date.
However, not all the entities are supported by the Events API, so the Stripe connector uses the `created` field or its analogue to query for new data in your Stripe account. These are the entities synced based on the date of creation:

- `Balance Transactions`
- `Events`
- `File Links`
- `Files`
- `Refunds`
- `Setup Attempts`
- `Shipping Rates`

On the other hand, the following streams use the `updated` field value as a cursor:

:::note

`updated` is an artificial cursor field introduced by Airbyte for the Incremental sync option.

:::

- `Application Fees`
- `Application Fee Refunds`
- `Authorizations`
- `Bank Accounts`
- `Cardholders`
- `Cards`
- `Charges`
- `Checkout Sessions`
- `Checkout Session Line Items` (cursor field is `checkout_session_updated`)
- `Coupons`
- `Credit Notes`
- `Customer Balance Transactions`
- `Customers`
- `Disputes`
- `Early Fraud Warnings`
- `External Account Bank Accounts`
- `External Account Cards`
- `Invoice Items`
- `Invoices`
- `Payment Intents`
- `Payouts`
- `Promotion Codes`
- `Persons`
- `Plans`
- `Prices`
- `Products`
- `Reviews`
- `Setup Intents`
- `Subscription Schedule`
- `Subscriptions`
- `Top Ups`
- `Transactions`
- `Transfers`

## Incremental deletes

The Stripe API also provides a way to implement incremental deletes for a limited number of streams:

- `Bank Accounts`
- `Coupons`
- `Customers`
- `External Account Bank Accounts`
- `External Account Cards`
- `Invoices`
- `Invoice Items`
- `Persons`
- `Plans`
- `Prices`
- `Products`
- `Subscriptions`

Each record is marked with `is_deleted` flag when the appropriate event happens upstream.

- Check out common troubleshooting issues for the Stripe source connector on our [Airbyte Forum](https://github.com/airbytehq/airbyte/discussions).

### Data type mapping

</details>

## Changelog

| Version | Date       | Pull Request                                              | Subject                                                                                                                                                                                                                       |
| :------ | :--------- | :-------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 5.3.9   | 2024-05-22 | [38550](https://github.com/airbytehq/airbyte/pull/38550)  | Update authenticator package                                                             |
| 5.3.8   | 2024-05-15 | [38248](https://github.com/airbytehq/airbyte/pull/38248)  | Replace AirbyteLogger with logging.Logger |
| 5.3.7   | 2024-04-24 | [36663](https://github.com/airbytehq/airbyte/pull/36663)  | Schema descriptions |
| 5.3.6   | 2024-04-18 | [37448](https://github.com/airbytehq/airbyte/pull/37448)  | Ensure AirbyteTracedException in concurrent CDK are emitted with the right type |
| 5.3.5   | 2024-04-18 | [37418](https://github.com/airbytehq/airbyte/pull/37418)  | Ensure python return code != 0 in case of error |
| 5.3.4   | 2024-04-11 | [37406](https://github.com/airbytehq/airbyte/pull/37406)  | Update CDK version to have partitioned state fix |
| 5.3.3   | 2024-04-11 | [37001](https://github.com/airbytehq/airbyte/pull/37001)  | Update airbyte-cdk to flush print buffer for every message |
| 5.3.2   | 2024-04-11 | [36964](https://github.com/airbytehq/airbyte/pull/36964)  | Update CDK version to fix breaking change before another devs work on it |
| 5.3.1   | 2024-04-10 | [36960](https://github.com/airbytehq/airbyte/pull/36960)  | Remove unused imports |
| 5.3.0   | 2024-03-12 | [35978](https://github.com/airbytehq/airbyte/pull/35978)  | Upgrade CDK to start emitting record counts with state and full refresh state |
| 5.2.4   | 2024-02-12 | [35137](https://github.com/airbytehq/airbyte/pull/35137)  | Fix license in `pyproject.toml` |
| 5.2.3   | 2024-02-09 | [35068](https://github.com/airbytehq/airbyte/pull/35068)  | Manage dependencies with Poetry. |
| 5.2.2   | 2024-01-31 | [34619](https://github.com/airbytehq/airbyte/pull/34619)  | Events stream concurrent on incremental syncs |
| 5.2.1   | 2024-01-18 | [34495](https://github.com/airbytehq/airbyte/pull/34495)  | Fix deadlock issue |
| 5.2.0   | 2024-01-18 | [34347](https://github.com/airbytehq/airbyte/pull//34347) | Add new fields invoices and subscription streams. Upgrade the CDK for better memory usage.                                                                                                                                    |
| 5.1.3   | 2023-12-18 | [33306](https://github.com/airbytehq/airbyte/pull/33306/) | Adding integration tests                                                                                                                                                                                                      |
| 5.1.2   | 2024-01-04 | [33414](https://github.com/airbytehq/airbyte/pull/33414)  | Prepare for airbyte-lib                                                                                                                                                                                                       |
| 5.1.1   | 2024-01-04 | [33926](https://github.com/airbytehq/airbyte/pull/33926/) | Update endpoint for `bank_accounts` stream                                                                                                                                                                                    |
| 5.1.0   | 2023-12-11 | [32908](https://github.com/airbytehq/airbyte/pull/32908/) | Read full refresh streams concurrently                                                                                                                                                                                        |
| 5.0.2   | 2023-12-01 | [33038](https://github.com/airbytehq/airbyte/pull/33038)  | Add stream slice logging for SubStream                                                                                                                                                                                        |
| 5.0.1   | 2023-11-17 | [32638](https://github.com/airbytehq/airbyte/pull/32638/) | Availability stretegy: check availability of both endpoints (if applicable) - common API + events API                                                                                                                         |
| 5.0.0   | 2023-11-16 | [32286](https://github.com/airbytehq/airbyte/pull/32286/) | Fix multiple issues regarding usage of the incremental sync mode for the `Refunds`, `CheckoutSessions`, `CheckoutSessionsLineItems` streams. Fix schemas for the streams: `Invoices`, `Subscriptions`, `SubscriptionSchedule` |
| 4.5.4   | 2023-11-16 | [32284](https://github.com/airbytehq/airbyte/pull/32284/) | Enable client-side rate limiting                                                                                                                                                                                              |
| 4.5.3   | 2023-11-14 | [32473](https://github.com/airbytehq/airbyte/pull/32473/) | Have all full_refresh stream syncs be concurrent                                                                                                                                                                              |
| 4.5.2   | 2023-11-03 | [32146](https://github.com/airbytehq/airbyte/pull/32146/) | Fix multiple BankAccount issues                                                                                                                                                                                               |
| 4.5.1   | 2023-11-01 | [32056](https://github.com/airbytehq/airbyte/pull/32056/) | Use CDK version 0.52.8                                                                                                                                                                                                        |
| 4.5.0   | 2023-10-25 | [31327](https://github.com/airbytehq/airbyte/pull/31327/) | Use concurrent CDK when running in full-refresh                                                                                                                                                                               |
| 4.4.2   | 2023-10-24 | [31764](https://github.com/airbytehq/airbyte/pull/31764)  | Base image migration: remove Dockerfile and use the python-connector-base image                                                                                                                                               |
| 4.4.1   | 2023-10-18 | [31553](https://github.com/airbytehq/airbyte/pull/31553)  | Adjusted `Setup Attempts` and extended `Checkout Sessions` stream schemas                                                                                                                                                     |
| 4.4.0   | 2023-10-04 | [31046](https://github.com/airbytehq/airbyte/pull/31046)  | Added margins field to invoice_line_items stream.                                                                                                                                                                             |
| 4.3.1   | 2023-09-27 | [30800](https://github.com/airbytehq/airbyte/pull/30800)  | Handle permission issues a non breaking                                                                                                                                                                                       |
| 4.3.0   | 2023-09-26 | [30752](https://github.com/airbytehq/airbyte/pull/30752)  | Do not sync upcoming invoices, extend stream schemas                                                                                                                                                                          |
| 4.2.0   | 2023-09-21 | [30660](https://github.com/airbytehq/airbyte/pull/30660)  | Fix updated state for the incremental syncs                                                                                                                                                                                   |
| 4.1.1   | 2023-09-15 | [30494](https://github.com/airbytehq/airbyte/pull/30494)  | Fix datatype of invoices.lines property                                                                                                                                                                                       |
| 4.1.0   | 2023-08-29 | [29950](https://github.com/airbytehq/airbyte/pull/29950)  | Implement incremental deletes, add suggested streams                                                                                                                                                                          |
| 4.0.1   | 2023-09-07 | [30254](https://github.com/airbytehq/airbyte/pull/30254)  | Fix cursorless incremental streams                                                                                                                                                                                            |
| 4.0.0   | 2023-08-15 | [29330](https://github.com/airbytehq/airbyte/pull/29330)  | Implement incremental syncs based on date of update                                                                                                                                                                           |
| 3.17.4  | 2023-08-15 | [29425](https://github.com/airbytehq/airbyte/pull/29425)  | Revert 3.17.3                                                                                                                                                                                                                 |
| 3.17.3  | 2023-08-01 | [28911](https://github.com/airbytehq/airbyte/pull/28911)  | Revert 3.17.2 and fix atm_fee property                                                                                                                                                                                        |
| 3.17.2  | 2023-08-01 | [28911](https://github.com/airbytehq/airbyte/pull/28911)  | Fix stream schemas, remove custom 403 error handling                                                                                                                                                                          |
| 3.17.1  | 2023-08-01 | [28887](https://github.com/airbytehq/airbyte/pull/28887)  | Fix `Invoices` schema                                                                                                                                                                                                         |
| 3.17.0  | 2023-07-28 | [26127](https://github.com/airbytehq/airbyte/pull/26127)  | Add `Prices` stream                                                                                                                                                                                                           |
| 3.16.0  | 2023-07-27 | [28776](https://github.com/airbytehq/airbyte/pull/28776)  | Add new fields to stream schemas                                                                                                                                                                                              |
| 3.15.0  | 2023-07-09 | [28709](https://github.com/airbytehq/airbyte/pull/28709)  | Remove duplicate streams                                                                                                                                                                                                      |
| 3.14.0  | 2023-07-09 | [27217](https://github.com/airbytehq/airbyte/pull/27217)  | Add `ShippingRates` stream                                                                                                                                                                                                    |
| 3.13.0  | 2023-07-18 | [28466](https://github.com/airbytehq/airbyte/pull/28466)  | Pin source API version                                                                                                                                                                                                        |
| 3.12.0  | 2023-05-20 | [26208](https://github.com/airbytehq/airbyte/pull/26208)  | Add new stream `Persons`                                                                                                                                                                                                      |
| 3.11.0  | 2023-06-26 | [27734](https://github.com/airbytehq/airbyte/pull/27734)  | License Update: Elv2 stream                                                                                                                                                                                                   |
| 3.10.0  | 2023-06-22 | [27132](https://github.com/airbytehq/airbyte/pull/27132)  | Add `CreditNotes` stream                                                                                                                                                                                                      |
| 3.9.1   | 2023-06-20 | [27522](https://github.com/airbytehq/airbyte/pull/27522)  | Fix formatting                                                                                                                                                                                                                |
| 3.9.0   | 2023-06-19 | [27362](https://github.com/airbytehq/airbyte/pull/27362)  | Add new Streams: Transfer Reversals, Setup Attempts, Usage Records, Transactions                                                                                                                                              |
| 3.8.0   | 2023-06-12 | [27238](https://github.com/airbytehq/airbyte/pull/27238)  | Add `Topups` stream; Add `Files` stream; Add `FileLinks` stream                                                                                                                                                               |
| 3.7.0   | 2023-06-06 | [27083](https://github.com/airbytehq/airbyte/pull/27083)  | Add new Streams: Authorizations, Cardholders, Cards, Payment Methods, Reviews                                                                                                                                                 |
| 3.6.0   | 2023-05-24 | [25893](https://github.com/airbytehq/airbyte/pull/25893)  | Add `ApplicationFeesRefunds` stream with parent `ApplicationFees`                                                                                                                                                             |
| 3.5.0   | 2023-05-20 | [22859](https://github.com/airbytehq/airbyte/pull/22859)  | Add stream `Early Fraud Warnings`                                                                                                                                                                                             |
| 3.4.3   | 2023-05-10 | [25965](https://github.com/airbytehq/airbyte/pull/25965)  | Fix Airbyte date-time data-types                                                                                                                                                                                              |
| 3.4.2   | 2023-05-04 | [25795](https://github.com/airbytehq/airbyte/pull/25795)  | Added `CDK TypeTransformer` to guarantee declared JSON Schema data-types                                                                                                                                                      |
| 3.4.1   | 2023-04-24 | [23389](https://github.com/airbytehq/airbyte/pull/23389)  | Add `customer_tax_ids` to `Invoices`                                                                                                                                                                                          |
| 3.4.0   | 2023-03-20 | [23963](https://github.com/airbytehq/airbyte/pull/23963)  | Add `SetupIntents` stream                                                                                                                                                                                                     |
| 3.3.0   | 2023-04-12 | [25136](https://github.com/airbytehq/airbyte/pull/25136)  | Add stream `Accounts`                                                                                                                                                                                                         |
| 3.2.0   | 2023-04-10 | [23624](https://github.com/airbytehq/airbyte/pull/23624)  | Add new stream `Subscription Schedule`                                                                                                                                                                                        |
| 3.1.0   | 2023-03-10 | [19906](https://github.com/airbytehq/airbyte/pull/19906)  | Expand `tiers` when syncing `Plans` streams                                                                                                                                                                                   |
| 3.0.5   | 2023-03-25 | [22866](https://github.com/airbytehq/airbyte/pull/22866)  | Specified date formatting in specification                                                                                                                                                                                    |
| 3.0.4   | 2023-03-24 | [24471](https://github.com/airbytehq/airbyte/pull/24471)  | Fix stream slices for single sliced streams                                                                                                                                                                                   |
| 3.0.3   | 2023-03-17 | [24179](https://github.com/airbytehq/airbyte/pull/24179)  | Get customer's attributes safely                                                                                                                                                                                              |
| 3.0.2   | 2023-03-13 | [24051](https://github.com/airbytehq/airbyte/pull/24051)  | Cache `customers` stream; Do not request transactions of customers with zero balance.                                                                                                                                         |
| 3.0.1   | 2023-02-22 | [22898](https://github.com/airbytehq/airbyte/pull/22898)  | Add missing column to Subscriptions stream                                                                                                                                                                                    |
| 3.0.0   | 2023-02-21 | [23295](https://github.com/airbytehq/airbyte/pull/23295)  | Fix invoice schema                                                                                                                                                                                                            |
| 2.0.0   | 2023-02-14 | [22312](https://github.com/airbytehq/airbyte/pull/22312)  | Another fix of `Invoices` stream schema + Remove http urls from openapi_spec.json                                                                                                                                             |
| 1.0.2   | 2023-02-09 | [22659](https://github.com/airbytehq/airbyte/pull/22659)  | Set `AvailabilityStrategy` for all streams                                                                                                                                                                                    |
| 1.0.1   | 2023-01-27 | [22042](https://github.com/airbytehq/airbyte/pull/22042)  | Set `AvailabilityStrategy` for streams explicitly to `None`                                                                                                                                                                   |
| 1.0.0   | 2023-01-25 | [21858](https://github.com/airbytehq/airbyte/pull/21858)  | Update the `Subscriptions` and `Invoices` stream schemas                                                                                                                                                                      |
| 0.1.40  | 2022-10-20 | [18228](https://github.com/airbytehq/airbyte/pull/18228)  | Update the `PaymentIntents` stream schema                                                                                                                                                                                     |
| 0.1.39  | 2022-09-28 | [17304](https://github.com/airbytehq/airbyte/pull/17304)  | Migrate to per-stream states.                                                                                                                                                                                                 |
| 0.1.38  | 2022-09-09 | [16537](https://github.com/airbytehq/airbyte/pull/16537)  | Fix `redeem_by` field type for `customers` stream                                                                                                                                                                             |
| 0.1.37  | 2022-08-16 | [15686](https://github.com/airbytehq/airbyte/pull/15686)  | Fix the bug when the stream couldn't be fetched due to limited permission set, if so - it should be skipped                                                                                                                   |
| 0.1.36  | 2022-08-04 | [15292](https://github.com/airbytehq/airbyte/pull/15292)  | Implement slicing                                                                                                                                                                                                             |
| 0.1.35  | 2022-07-21 | [14924](https://github.com/airbytehq/airbyte/pull/14924)  | Remove `additionalProperties` field from spec and schema                                                                                                                                                                      |
| 0.1.34  | 2022-07-01 | [14357](https://github.com/airbytehq/airbyte/pull/14357)  | Add external account streams -                                                                                                                                                                                                |
| 0.1.33  | 2022-06-06 | [13449](https://github.com/airbytehq/airbyte/pull/13449)  | Add semi-incremental support for CheckoutSessions and CheckoutSessionsLineItems streams, fixed big in StripeSubStream, added unittests, updated docs                                                                          |
| 0.1.32  | 2022-04-30 | [12500](https://github.com/airbytehq/airbyte/pull/12500)  | Improve input configuration copy                                                                                                                                                                                              |
| 0.1.31  | 2022-04-20 | [12230](https://github.com/airbytehq/airbyte/pull/12230)  | Update connector to use a `spec.yaml`                                                                                                                                                                                         |
| 0.1.30  | 2022-03-21 | [11286](https://github.com/airbytehq/airbyte/pull/11286)  | Minor corrections to documentation and connector specification                                                                                                                                                                |
| 0.1.29  | 2022-03-08 | [10359](https://github.com/airbytehq/airbyte/pull/10359)  | Improved performance for streams with substreams: invoice_line_items, subscription_items, bank_accounts                                                                                                                       |
| 0.1.28  | 2022-02-08 | [10165](https://github.com/airbytehq/airbyte/pull/10165)  | Improve 404 handling for `CheckoutSessionsLineItems` stream                                                                                                                                                                   |
| 0.1.27  | 2021-12-28 | [9148](https://github.com/airbytehq/airbyte/pull/9148)    | Fix `date`, `arrival\_date` fields                                                                                                                                                                                            |
| 0.1.26  | 2021-12-21 | [8992](https://github.com/airbytehq/airbyte/pull/8992)    | Fix type `events.request` in schema                                                                                                                                                                                           |
| 0.1.25  | 2021-11-25 | [8250](https://github.com/airbytehq/airbyte/pull/8250)    | Rearrange setup fields                                                                                                                                                                                                        |
| 0.1.24  | 2021-11-08 | [7729](https://github.com/airbytehq/airbyte/pull/7729)    | Include tax data in `checkout_sessions_line_items` stream                                                                                                                                                                     |
| 0.1.23  | 2021-11-08 | [7729](https://github.com/airbytehq/airbyte/pull/7729)    | Correct `payment_intents` schema                                                                                                                                                                                              |
| 0.1.22  | 2021-11-05 | [7345](https://github.com/airbytehq/airbyte/pull/7345)    | Add 3 new streams                                                                                                                                                                                                             |
| 0.1.21  | 2021-10-07 | [6841](https://github.com/airbytehq/airbyte/pull/6841)    | Fix missing `start_date` argument + update json files for SAT                                                                                                                                                                 |
| 0.1.20  | 2021-09-30 | [6017](https://github.com/airbytehq/airbyte/pull/6017)    | Add lookback_window_days parameter                                                                                                                                                                                            |
| 0.1.19  | 2021-09-27 | [6466](https://github.com/airbytehq/airbyte/pull/6466)    | Use `start_date` parameter in incremental streams                                                                                                                                                                             |
| 0.1.18  | 2021-09-14 | [6004](https://github.com/airbytehq/airbyte/pull/6004)    | Fix coupons and subscriptions stream schemas by removing incorrect timestamp formatting                                                                                                                                       |
| 0.1.17  | 2021-09-14 | [6004](https://github.com/airbytehq/airbyte/pull/6004)    | Add `PaymentIntents` stream                                                                                                                                                                                                   |
| 0.1.16  | 2021-07-28 | [4980](https://github.com/airbytehq/airbyte/pull/4980)    | Remove Updated field from schemas                                                                                                                                                                                             |
| 0.1.15  | 2021-07-21 | [4878](https://github.com/airbytehq/airbyte/pull/4878)    | Fix incorrect percent_off and discounts data filed types                                                                                                                                                                      |
| 0.1.14  | 2021-07-09 | [4669](https://github.com/airbytehq/airbyte/pull/4669)    | Subscriptions Stream now returns all kinds of subscriptions \(including expired and canceled\)                                                                                                                                |
| 0.1.13  | 2021-07-03 | [4528](https://github.com/airbytehq/airbyte/pull/4528)    | Remove regex for acc validation                                                                                                                                                                                               |
| 0.1.12  | 2021-06-08 | [3973](https://github.com/airbytehq/airbyte/pull/3973)    | Add `AIRBYTE_ENTRYPOINT` for Kubernetes support                                                                                                                                                                               |
| 0.1.11  | 2021-05-30 | [3744](https://github.com/airbytehq/airbyte/pull/3744)    | Fix types in schema                                                                                                                                                                                                           |
| 0.1.10  | 2021-05-28 | [3728](https://github.com/airbytehq/airbyte/pull/3728)    | Update data types to be number instead of int                                                                                                                                                                                 |
| 0.1.9   | 2021-05-13 | [3367](https://github.com/airbytehq/airbyte/pull/3367)    | Add acceptance tests for connected accounts                                                                                                                                                                                   |
| 0.1.8   | 2021-05-11 | [3566](https://github.com/airbytehq/airbyte/pull/3368)    | Bump CDK connectors                                                                                                                                                                                                           |

</HideInUI>
