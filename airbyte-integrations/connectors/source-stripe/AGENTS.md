> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-stripe: Unique Behaviors

## 1. Events-Based Incremental Sync via StateDelegatingStream

Most entity streams (customers, subscriptions, invoices, charges, refunds, transfers, etc.) use `StateDelegatingStream` with a 30-day `api_retention_period`. On the first sync (no state), the connector reads directly from the entity's own endpoint (e.g., `/v1/customers`). On subsequent incremental syncs, it switches to reading from `/v1/events` filtered by specific event types (e.g., `customer.created`, `customer.updated`, `customer.deleted`), then uses `DpathFlattenFields` to unwrap `data.object` and reconstruct the entity record from the event payload.

Stripe's Events API only retains events for 30 days. If the connector's state falls behind by more than 30 days (e.g., after a long pause in syncing), it automatically reverts to a full refresh from the entity endpoint rather than trying to read events that no longer exist.

**Why this matters:** What looks like a simple entity read is actually two completely different data paths depending on whether state exists and how old it is. Adding a new entity stream requires defining both the direct-read retriever AND the events-based retriever with the correct event type filter strings. If the event type strings are wrong, incremental syncs will silently miss updates.

## 2. Silent 403/400/404 Error Ignoring

The base error handler is configured to IGNORE (not fail) responses with HTTP status 403 (permission denied), 400 (bad request), and 404 (not found). When the Stripe API returns any of these errors for a specific resource or subresource, the connector silently skips that record and continues syncing.

**Why this matters:** If an API key loses access to a specific Stripe resource (e.g., Issuing endpoints require special permissions), those records will silently disappear from incremental syncs without any error or warning in the sync logs. A user may not notice they are missing data until they check record counts against the Stripe dashboard.

## 3. Inaccessible Expandable Fields in Events API

As of April 2024, the Stripe API does not support retrieving [expandable fields](https://docs.stripe.com/api/expanding_objects) from the Events API. This limits how the connector can process events during incremental syncs — it cannot reconstruct the full latest state of an object solely from event payloads when expandable fields are involved.

**Why this matters:** During incremental syncs (which read from `/v1/events`), the connector only sees the non-expanded version of each object. Fields that require expansion (e.g., nested customer details on a charge) will be missing or returned as just an ID string. This is a fundamental Stripe API limitation, not a connector bug.

## 4. Populating Data for Sandbox Accounts

Using `Stripe Sandbox Account` test credentials, connect to https://dashboard.stripe.com/ and toggle "Test mode". New records can be added here, but modifying or deleting existing records may cause CAT failures. To create payments, use [Stripe's test credit cards](https://docs.stripe.com/testing#cards) in test mode.

**Why this matters:** CAT tests depend on specific record states in the sandbox. Modifying or deleting records that tests rely on will break assertions. Only add new records when populating test data.

## 5. API Version-Dependent Data Discrepancies in Events

The data returned in event payloads depends on the Stripe API version the object was created with, not the version used to read the event. For example, `charge.refunds` may appear in events even though it is an [expandable field](https://docs.stripe.com/api/expanding_objects) that should not be present — this happens because the sandbox uses API version `2020-08-27`, and the `charge.refunds` field was only [removed in the 2022-11-15 upgrade](https://docs.stripe.com/upgrades#2022-11-15). See [Stripe API versioning](https://docs.stripe.com/api/versioning) for how versions are managed.

**Why this matters:** When debugging unexpected fields appearing (or missing) in event payloads, the root cause may be the API version the data was originally created with, not the connector's behavior. This is especially confusing in sandbox environments where the API version may be much older than production.

## 6. Per-Stream `Stripe-Version` Override (`invoice_payments`)

Every stream inherits `Stripe-Version: 2022-11-15` from `base_requester`. `invoice_payments` is the sole exception: both of its requesters set `Stripe-Version: 2025-03-31.basil`, because the InvoicePayment resource does not exist before [Basil](https://docs.stripe.com/changelog/basil/2025-03-31/add-support-for-multiple-partial-payments-on-invoices). The override is written inside that stream's own `requester` blocks, so it cannot leak into any other stream's requests.

Read this together with section 5, which says the `Stripe-Version` header does not control the shape of event payloads. Both are true, and they are not in conflict:

- **Full refresh path** (`/v1/invoice_payments`): the header is what makes the request work at all. Without it the endpoint is not available on the pinned 2022-11-15 version.
- **Incremental path** (`/v1/events`): the header does **not** re-render event payloads — section 5 still applies, and records come back shaped as of the API version in effect when the event was created. It is set so the `type=invoice_payment.paid` filter is interpreted by a version that knows that event type. This matters because of section 2: the base error handler ignores 400s, so a filter rejected as unknown would produce a silently empty stream instead of a visible failure.

**Why this matters:** if you add another Basil-era (or later) resource, copy this pattern — override `request_headers` on the new stream's requesters only, and do not raise the connector-wide pin. Changing `base_requester` would re-shape every existing stream's records at once. Note also that overriding `request_headers` replaces the mapping wholesale, so the override must re-declare `Stripe-Account` or the connected-account header is dropped.

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
