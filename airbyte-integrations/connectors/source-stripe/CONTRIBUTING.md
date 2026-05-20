# Contributing to source-stripe

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Stripe API supports `created` parameter filtering (e.g., `created[gte]`) on most list endpoints. However, Stripe does NOT support `updated_at` filtering. Since most Stripe resources are mutable (customers, subscriptions, invoices, etc.), `created`-only filtering is insufficient for true incremental sync. The `events` stream is an exception — events are immutable point-in-time records where `created[gte]` is semantically correct. The connector currently has all streams as full-refresh.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| accounts | small | top-level parent | none | none | deferred_no_api_support | Connected accounts list; no date filter |
| application_fees | medium | top-level parent | none | created_at_only | deferred_no_api_support |  |
| application_fees_refunds | medium | top-level parent | none | created_at_only | deferred_no_api_support |  |
| authorizations | medium | top-level parent | none | created_at_only | deferred_no_api_support |  |
| balance_transactions | xlarge | top-level parent | none | created_at_only | deferred_no_api_support | Effectively immutable; `created[gte]` filter available |
| bank_accounts | medium | top-level parent | none | created_at_only | deferred_no_api_support |  |
| cardholders | medium | top-level parent | none | created_at_only | deferred_no_api_support |  |
| cards | medium | top-level parent | none | created_at_only | deferred_no_api_support |  |
| charges | large | top-level parent | none | created_at_only | deferred_no_api_support | Mutable (refunds, disputes modify); `created` only |
| checkout_sessions | medium | top-level parent | none | created_at_only | deferred_no_api_support |  |
| coupons | small | top-level parent | none | created_at_only | deferred_no_api_support | Config-style; `created` only |
| credit_notes | medium | top-level parent | none | created_at_only | deferred_no_api_support |  |
| customers | large | top-level parent | none | created_at_only | deferred_no_api_support | Mutable; `created` only. No `updated` filter. |
| disputes | medium | top-level parent | none | created_at_only | deferred_no_api_support |  |
| early_fraud_warnings | medium | top-level parent | none | created_at_only | deferred_no_api_support |  |
| events | xlarge | top-level parent | none | created_at_only | deferred_no_api_support | Immutable point-in-time records; `created[gte]` is sufficient. Candidate for incremental in a future PR. |
| external_account_bank_accounts | medium | top-level parent | none | created_at_only | deferred_no_api_support |  |
| external_account_cards | medium | top-level parent | none | created_at_only | deferred_no_api_support |  |
| file_links | small | top-level parent | none | created_at_only | deferred_no_api_support | `created` only |
| files | small | top-level parent | none | created_at_only | deferred_no_api_support | `created` only |
| invoice_items | medium | top-level parent | none | created_at_only | deferred_no_api_support |  |
| invoice_line_items | medium | top-level parent | none | created_at_only | deferred_no_api_support |  |
| invoices | large | top-level parent | none | created_at_only | deferred_no_api_support | Mutable (payments, voids); `created` only |
| payment_intents | large | top-level parent | none | created_at_only | deferred_no_api_support | Mutable (confirmations); `created` only |
| payment_methods | medium | top-level parent | none | created_at_only | deferred_no_api_support |  |
| payouts | medium | top-level parent | none | created_at_only | deferred_no_api_support | Mostly immutable; `created[gte]` filter available |
| persons | medium | top-level parent | none | created_at_only | deferred_no_api_support |  |
| plans | small | top-level parent | none | created_at_only | deferred_no_api_support | Config-style; `created` only |
| prices | small | top-level parent | none | created_at_only | deferred_no_api_support | Config-style; `created` only |
| products | small | top-level parent | none | created_at_only | deferred_no_api_support | Mutable; `created` only |
| promotion_codes | medium | top-level parent | none | created_at_only | deferred_no_api_support |  |
| refunds | medium | top-level parent | none | created_at_only | deferred_no_api_support | Effectively immutable once created; `created` filter available |
| reviews | medium | top-level parent | none | created_at_only | deferred_no_api_support |  |
| setup_intents | medium | top-level parent | none | created_at_only | deferred_no_api_support |  |
| shipping_rates | small | top-level parent | none | created_at_only | deferred_no_api_support | Config-style; `created` only |
| subscription_items | medium | top-level parent | none | created_at_only | deferred_no_api_support |  |
| subscription_schedule | medium | top-level parent | none | created_at_only | deferred_no_api_support |  |
| subscriptions | large | top-level parent | none | created_at_only | deferred_no_api_support | Mutable (status changes); `created` only |
| top_ups | medium | top-level parent | none | created_at_only | deferred_no_api_support |  |
| transactions | medium | top-level parent | none | created_at_only | deferred_no_api_support |  |
| transfers | medium | top-level parent | none | created_at_only | deferred_no_api_support | Effectively immutable; `created[gte]` filter available |
| checkout_sessions_line_items | medium | child | checkout_session_updated | checkout_session_updated | incremental |  |
| customer_balance_transactions | medium | child | created | created | incremental |  |
| payout_balance_transactions | medium | child | updated | updated | incremental |  |
| setup_attempts | medium | child | created | created | incremental |  |
| transfer_reversals | medium | child | created | created | incremental |  |
| usage_records | medium | child | none | created_at_only | deferred_child |  |

### Deferred streams

- **No API date filter (1 streams):** `accounts` — these endpoints do not expose date-based filtering. A future agent should verify via live API probing whether undocumented filter parameters are accepted.
- **Created-at only (40 streams):** `application_fees`, `application_fees_refunds`, `authorizations`, `balance_transactions`, `bank_accounts`, `cardholders`, `cards`, `charges`, `checkout_sessions`, `coupons`, `credit_notes`, `customers`, `disputes`, `early_fraud_warnings`, `events`, `external_account_bank_accounts`, `external_account_cards`, `file_links`, `files`, `invoice_items`, `invoice_line_items`, `invoices`, `payment_intents`, `payment_methods`, `payouts`, `persons`, `plans`, `prices`, `products`, `promotion_codes`, `refunds`, `reviews`, `setup_intents`, `shipping_rates`, `subscription_items`, `subscription_schedule`, `subscriptions`, `top_ups`, `transactions`, `transfers` — these endpoints support `created` filtering but the resources are mutable, making `created_at`-only filtering insufficient for true incremental sync.
- **Child streams (1 streams):** `usage_records` — partitioned via `SubstreamPartitionRouter`. A follow-up session should evaluate incremental support.
