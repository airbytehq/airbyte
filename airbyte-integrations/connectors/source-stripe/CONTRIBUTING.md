# source-stripe: Unique Behaviors

## 1. Event-Based Incremental Sync Has Two Variants via StateDelegatingStream

Most entity streams (customers, subscriptions, invoices, charges, refunds, transfers, etc.) use `StateDelegatingStream` with a 30-day `api_retention_period`. On the first sync (no state), the connector reads directly from the entity's own endpoint (for example, `/v1/customers`). Once state exists, event-based incremental streams can follow one of two implementations selected by `event_based_incremental_sync_mode`:

- `events`: Read `/v1/events`, filter by the relevant event types, then use `DpathFlattenFields` to unwrap `data.object` and emit the object embedded in the Stripe event payload.
- `hydrated_events`: Still read `/v1/events` to determine which records changed, but then reread each changed object from the stream's own resource endpoint before emitting it. Nested collection streams such as `invoice_line_items` reread the child collection for the changed parent object.

In hydrated mode, partitioning is still manifest-only: a `GroupingPartitionRouter` wraps the events `SubstreamPartitionRouter` with `deduplicate: true`. This deduplicates duplicate object IDs before hydration, so multiple events for the same object in one sync window trigger one hydration request per unique object.

Stripe's Events API only retains events for 30 days. If the connector's state falls behind by more than 30 days (e.g., after a long pause in syncing), it automatically reverts to a full refresh from the entity endpoint rather than trying to read events that no longer exist.

**Why this matters:** What looks like a simple entity read is actually multiple data paths depending on whether state exists, how old it is, and which event-based mode is selected. Adding a new entity stream now means deciding whether its hydrated incremental variant should reread a detail endpoint or a child collection endpoint, in addition to defining the direct-read retriever and the event filters. If the event type strings or hydrated endpoint path are wrong, incremental syncs will silently miss updates or reread the wrong records.

## 2. Silent 403/400/404 Error Ignoring

The base error handler is configured to IGNORE (not fail) responses with HTTP status 403 (permission denied), 400 (bad request), and 404 (not found). When the Stripe API returns any of these errors for a specific resource or subresource, the connector silently skips that record and continues syncing.

**Why this matters:** If an API key loses access to a specific Stripe resource (e.g., Issuing endpoints require special permissions), those records will silently disappear from incremental syncs without any error or warning in the sync logs. A user may not notice they are missing data until they check record counts against the Stripe dashboard.

## 3. Hydrated Mode Exists to Compensate for Events API Payload Limits

As of April 2024, the Stripe API does not support retrieving [expandable fields](https://docs.stripe.com/api/expanding_objects) from the Events API. That limitation is exactly why the connector now exposes both `events` and `hydrated_events` modes.

**Why this matters:** In `events` mode, incremental syncs still emit the non-expanded object snapshot from the event payload, so fields that require expansion may be missing or reduced to IDs. In `hydrated_events` mode, the connector uses the event only as the change signal and fetches the emitted record from the object endpoint instead, reapplying any stream-specific `expand[]` parameters configured in the connector. This is the core functional difference between the new hydrated stream and the original event stream.

## 4. Populating Data for Sandbox Accounts

Using `Stripe Sandbox Account` test credentials, connect to https://dashboard.stripe.com/ and toggle "Test mode". New records can be added here, but modifying or deleting existing records may cause CAT failures. To create payments, use [Stripe's test credit cards](https://docs.stripe.com/testing#cards) in test mode.

**Why this matters:** CAT tests depend on specific record states in the sandbox. Modifying or deleting records that tests rely on will break assertions. Only add new records when populating test data.

## 5. API Version-Dependent Data Discrepancies in Events

The data returned in event payloads depends on the Stripe API version the object was created with, not the version used to read the event. For example, `charge.refunds` may appear in events even though it is an [expandable field](https://docs.stripe.com/api/expanding_objects) that should not be present — this happens because the sandbox uses API version `2020-08-27`, and the `charge.refunds` field was only [removed in the 2022-11-15 upgrade](https://docs.stripe.com/upgrades#2022-11-15). See [Stripe API versioning](https://docs.stripe.com/api/versioning) for how versions are managed.

**Why this matters:** When debugging unexpected fields appearing (or missing) in event payloads, the root cause may be the API version the data was originally created with, not the connector's behavior. This is especially confusing in sandbox environments where the API version may be much older than production.

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

### Future incremental stream candidates

- **No API date filter (1 streams):** `accounts` — these endpoints do not expose date-based filtering. A future agent should verify via live API probing whether undocumented filter parameters are accepted.
- **Created-at only (40 streams):** `application_fees`, `application_fees_refunds`, `authorizations`, `balance_transactions`, `bank_accounts`, `cardholders`, `cards`, `charges`, `checkout_sessions`, `coupons`, `credit_notes`, `customers`, `disputes`, `early_fraud_warnings`, `events`, `external_account_bank_accounts`, `external_account_cards`, `file_links`, `files`, `invoice_items`, `invoice_line_items`, `invoices`, `payment_intents`, `payment_methods`, `payouts`, `persons`, `plans`, `prices`, `products`, `promotion_codes`, `refunds`, `reviews`, `setup_intents`, `shipping_rates`, `subscription_items`, `subscription_schedule`, `subscriptions`, `top_ups`, `transactions`, `transfers` — these endpoints support `created` filtering but the resources are mutable, making `created_at`-only filtering insufficient for true incremental sync.
- **Child streams (1 streams):** `usage_records` — partitioned via `SubstreamPartitionRouter`. A follow-up session should evaluate incremental support.
