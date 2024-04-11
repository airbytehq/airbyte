# Stripe

This page contains the setup guide and reference information for Stripe.

## Prerequisites

* Stripe developer account access
* Stripe API key
* Stripe Account ID

## Features

| Feature | Supported? |
| --- | --- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| Namespaces | No |

## Setup guide

### Step 1: Obtain Stripe account ID

1. Click the gear icon in the top navigation bar. The click **Settings**.
![Stripe Settings](/docs/setup-guide/assets/images/stripe-settings.jpg "Stripe Settings")

2. Inside Business settings, click **Account details**.
![Stripe Account Details](/docs/setup-guide/assets/images/stripe-account-details.jpg "Stripe Account Details")

3. Inside the Account details page, you can find your **Account ID**. This ID begins with **acct_**.
![Stripe Account ID](/docs/setup-guide/assets/images/stripe-account-id.jpg "Stripe Account ID")

### Step 2: Obtain Stripe API key

1. Log in to your [Stripe account](https://dashboard.stripe.com/login).

2. In the top navigation bar, click **Developers**. Then click **API keys** from the tabs.
![Stripe API Keys](/docs/setup-guide/assets/images/stripe-api-keys.jpg "Stripe API Keys")

3. Click **+ Create restricted key**.

4. Enter a **Key name**, and select **Read** for all available permissions.
![Stripe Create API Key](/docs/setup-guide/assets/images/stripe-create-api-key.jpg "Stripe Create API Key")

5. Click **Create key**. You may be prompted to enter a confirmation code. Write down your API key.
![Stripe API Key](/docs/setup-guide/assets/images/stripe-api-key.jpg "Stripe API Key")

For more information on Stripe API Keys, see the [Stripe documentation](https://stripe.com/docs/keys).

### Step 3: Set up Stripe in Daspire

1. Select **Stripe** from the Source list.

2. Enter a **Source Name**.

3. Enter the **Stripe Account ID** you obtained in Step 1.

4. Enter the **Stripe Secret Key** you obtained in Step 2.

5. For **Replication Start Date**, enter a UTC date and time in the format `YYYY-MM-DDTHH:mm:ssZ`. The data added on and after this date will be replicated.

6. (Optional) For **Lookback Window**, you may specify a number of days from the present day to reread data. This allows the integration to retrieve data that might have been updated after its initial creation, and is useful for handling any post-transaction adjustments. This applies only to streams that do not support event-based incremental syncs.

  > * Leaving the Lookback Window at its default value of 0 means Daspire will not re-export data after it has been synced.
  > * Setting the Lookback Window to 1 means Daspire will re-export data from the past day, capturing any changes made in the last 24 hours.
  > * Setting the Lookback Window to 7 means Daspire will re-export and capture any data changes within the last week.

7. (Optional) For **Data Request Window**, you may specify the time window in days used by the integration when requesting data from the Stripe API. This window defines the span of time covered in each request, with larger values encompassing more days in a single request. Generally speaking, the lack of overhead from making fewer requests means a larger window is faster to sync. However, this also means the state of the sync will persist less frequently. If an issue occurs or the sync is interrupted, a larger window means more data will need to be resynced, potentially causing a delay in the overall process.

  For example, if you are replicating three years worth of data:

  > * A Data Request Window of 365 days means Daspire makes 3 requests, each for a year. This is generally faster but risks needing to resync up to a year's data if the sync is interrupted.
  > * A Data Request Window of 30 days means 36 requests, each for a month. This may be slower but minimizes the amount of data that needs to be resynced if an issue occurs.
  > * If you are unsure of which value to use, we recommend leaving this setting at its default value of 365 days.

8. Click **Save & Test**.

## Supported streams

This source is capable of syncing the following streams:

* [Accounts](https://stripe.com/docs/api/accounts/list)
* [Application Fees](https://stripe.com/docs/api/application_fees) (Incremental)
* [Application Fee Refunds](https://stripe.com/docs/api/fee_refunds/list) (Incremental)
* [Authorizations](https://stripe.com/docs/api/issuing/authorizations/list) (Incremental)
* [Balance Transactions](https://stripe.com/docs/api/balance_transactions/list) (Incremental)
* [Bank accounts](https://stripe.com/docs/api/customer_bank_accounts/list) (Incremental)
* [Cardholders](https://stripe.com/docs/api/issuing/cardholders/list) (Incremental)
* [Cards](https://stripe.com/docs/api/issuing/cards/list) (Incremental)
* [Charges](https://stripe.com/docs/api/charges/list) (Incremental - The amount column defaults to the smallest currency unit.)
* [Checkout Sessions](https://stripe.com/docs/api/checkout/sessions/list) (Incremental)
* [Checkout Sessions Line Items](https://stripe.com/docs/api/checkout/sessions/line_items) (Incremental)
* [Coupons](https://stripe.com/docs/api/coupons/list) (Incremental)
* [Credit Notes](https://stripe.com/docs/api/credit_notes/list) (Incremental)
* [Customer Balance Transactions](https://stripe.com/docs/api/customer_balance_transactions/list) (Incremental)
* [Customers](https://stripe.com/docs/api/customers/list) (Incremental)
* [Disputes](https://stripe.com/docs/api/disputes/list) (Incremental)
* [Early Fraud Warnings](https://stripe.com/docs/api/radar/early_fraud_warnings/list) (Incremental)
* [Events](https://stripe.com/docs/api/events/list) (Incremental)
* [External Account Bank Accounts](https://stripe.com/docs/api/external_account_bank_accounts/list) (Incremental)
* [External Account Cards](https://stripe.com/docs/api/external_account_cards/list) (Incremental)
* [File Links](https://stripe.com/docs/api/file_links/list) (Incremental)
* [Files](https://stripe.com/docs/api/files/list) (Incremental)
* [Invoice Items](https://stripe.com/docs/api/invoiceitems/list) (Incremental)
* [Invoice Line Items](https://stripe.com/docs/api/invoices/invoice_lines)
* [Invoices](https://stripe.com/docs/api/invoices/list) (Incremental)
* [Payment Intents](https://stripe.com/docs/api/payment_intents/list) (Incremental)
* [Payment Methods](https://stripe.com/docs/api/payment_methods/list)
* [Payouts](https://stripe.com/docs/api/payouts/list) (Incremental)
* [Promotion Code](https://stripe.com/docs/api/promotion_codes/list) (Incremental)
* [Persons](https://stripe.com/docs/api/persons/list) (Incremental)
* [Plans](https://stripe.com/docs/api/plans/list) (Incremental)
* [Prices](https://stripe.com/docs/api/prices/list) (Incremental)
* [Products](https://stripe.com/docs/api/products/list) (Incremental)
* [Refunds](https://stripe.com/docs/api/refunds/list) (Incremental)
* [Reviews](https://stripe.com/docs/api/radar/reviews/list) (Incremental)
* [Setup Attempts](https://stripe.com/docs/api/setup_attempts/list) (Incremental)
* [Setup Intents](https://stripe.com/docs/api/setup_intents/list) (Incremental)
* [Shipping Rates](https://stripe.com/docs/api/shipping_rates/list) (Incremental)
* [Subscription Items](https://stripe.com/docs/api/subscription_items/list)
* [Subscription Schedule](https://stripe.com/docs/api/subscription_schedules) (Incremental)
* [Subscriptions](https://stripe.com/docs/api/subscriptions/list) (Incremental)
* [Top Ups](https://stripe.com/docs/api/topups/list) (Incremental)
* [Transactions](https://stripe.com/docs/api/transfers/list) (Incremental)
* [Transfers](https://stripe.com/docs/api/transfers/list) (Incremental)
* [Transfer Reversals](https://stripe.com/docs/api/transfer_reversals/list)
* [Usage Records](https://stripe.com/docs/api/usage_records/subscription_item_summary_list)

## Data type mapping

The Stripe API uses the same [JSON Schema](https://json-schema.org/understanding-json-schema/reference/index.html) types that Daspire uses internally (string, date-time, object, array, boolean, integer, and number), so no type conversions are performed for the Stripe integration.

## Troubleshooting

1. Rate limit

  The Stripe integration should not run into Stripe API limitations under normal usage. See [Stripe Rate limits documentation](https://stripe.com/docs/rate-limits).

2. Incremental syncs

  Since the Stripe API does not allow querying objects which were updated since the last sync, the Stripe integration uses the Events API under the hood to implement incremental syncs and export data based on its update date. However, not all the entities are supported by the Events API, so the Stripe integration uses the **created** field or its analogue to query for new data in your Stripe account. These are the entities synced based on the date of creation:

  > * Balance Transactions
  > * Events
  > * File Links
  > * Files
  > * Refunds
  > * Setup Attempts
  > * Shipping Rates

  On the other hand, the following streams use the **updated** field value as a cursor:

  > * Application Fees
  > * Application Fee Refunds
  > * Authorizations
  > * Bank Accounts
  > * Cardholders
  > * Cards
  > * Charges
  > * Checkout Sessions
  > * Checkout Session Line Items (cursor field is `checkout_session_updated`)
  > * Coupons
  > * Credit Notes
  > * Customer Balance Transactions
  > * Customers
  > * Disputes
  > * Early Fraud Warnings
  > * External Account Bank Accounts
  > * External Account Cards
  > * Invoice Items
  > * Invoices
  > * Payment Intents
  > * Payouts
  > * Promotion Codes
  > * Persons
  > * Plans
  > * Prices
  > * Products
  > * Reviews
  > * Setup Intents
  > * Subscription Schedule
  > * Subscriptions
  > * Top Ups
  > * Transactions
  > * Transfers

3. Incremental deletes

  The Stripe API also provides a way to implement incremental deletes for a limited number of streams:

  > * Bank Accounts
  > * Coupons
  > * Customers
  > * External Account Bank Accounts
  > * External Account Cards
  > * Invoices
  > * Invoice Items
  > * Persons
  > * Plans
  > * Prices
  > * Products
  > * Subscriptions

  Each record is marked with `is_deleted` flag when the appropriate event happens upstream.

4. Max number of tables that can be synced at a time is 6,000. We advise you to adjust your settings if it fails to fetch schema due to max number of tables reached.
