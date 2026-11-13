# source-revenuecat: Unique Connector Behaviors

## 1. Pagination follows the vendor's `next_page` path

Every RevenueCat v2 list endpoint uses keyset pagination: the response carries `next_page`, an API-relative path to the next page ([Pagination](https://www.revenuecat.com/docs/api-v2#tag/Pagination)). The vendor does not document how `starting_after` is encoded inside it; observed responses carry it already URL-encoded, such as `/v2/projects/proj1/customers?starting_after=%24RCAnonymousID%3Aabc` ([airbyte#70315](https://github.com/airbytehq/airbyte/issues/70315)). The paginator uses `page_token_option: RequestPath` and `cursor_value: "{{ response.get('next_page') }}"`, so the next request goes to that exact path. `limit` is still injected as a request parameter (100, the vendor maximum; larger values are clamped), and the CDK drops it when `next_page` already carries the same value.

The connector used to cut `starting_after` out of `next_page` and inject it as a request parameter. That encoded the cursor a second time, so default anonymous app user IDs (`$RCAnonymousID:...`) turned into `%2524RCAnonymousID%253A...`, the API returned the same page again, and `customers` and its substreams looped forever ([airbyte#70315](https://github.com/airbytehq/airbyte/issues/70315)).

**Why this matters:** Do not go back to extracting `starting_after` from `next_page`, and do not URL-encode the cursor again. Any customer with an anonymous ID makes the sync loop.

## 2. Incremental sync is client-side only

No list endpoint accepts a date filter, and none documents a sort order (only the subscription transactions endpoint, which the connector does not read, takes `sort`). Each incremental stream's `DatetimeBasedCursor` therefore sets `is_client_side_incremental: true`. Every sync reads every page, and the CDK drops records older than the saved state. Paging uses `starting_after` keys, so offset drift and sort skew do not apply. A partition the saved state does not hold yet, such as a customer reached for the first time, starts from the stream's global cursor (less the previous sync's duration), not from `start_date`. State written by 0.1.x, whose `is_data_feed` stop skipped later pages, therefore never backfills the rows it missed; only a refresh recovers them.

**Why this matters:** Do not set `is_data_feed: true`. On unsorted endpoints it stops at the first record older than the state and silently skips every later page. An incremental sync makes as many requests as a full refresh, so runtime is driven by rate limits (see 3), not by how much data changed.

## 3. Rate limits differ by endpoint domain, and customer substreams fan out

RevenueCat applies a separate per-minute budget to each endpoint domain ([Rate Limit](https://www.revenuecat.com/docs/api-v2#tag/Rate-Limit)). Customer Information (customers, subscriptions, purchases, active entitlements, aliases, invoices) allows 480 requests per minute. Project Configuration (projects, apps, entitlements, offerings, packages, products) allows 60. Charts & Metrics (`metrics_overview`) allows 25. A 429 response carries `backoff_ms` and a `Retry-After` header in seconds, and `base_requester` waits for `Retry-After` before it retries. `customers_subscriptions`, `customers_purchases`, `customers_active_entitlements`, `customers_aliases` and `customers_invoices` each send at least one request per customer, so a large project means long syncs that can emit no records for a long time. `metadata.yaml` sets `maxSecondsBetweenMessages: 3600` for the certification check, but the platform raises any value below its default heartbeat threshold (10800 seconds) to that default, so the effective timeout is three hours.

**Why this matters:** A value below 10800 changes nothing. If large projects hit heartbeat timeouts, raise `maxSecondsBetweenMessages` above 10800. Adding more per-customer substreams makes those timeouts more likely. `customers_subscriptions` is the only per-customer stream in `suggestedStreams`, on purpose: [airbyte-internal-issues#18779](https://github.com/airbytehq/airbyte-internal-issues/issues/18779) (M-4) treats subscription revenue as headline data. Keep `customers_purchases`, `customers_active_entitlements`, `customers_aliases` and `customers_invoices` out of it.

## 4. `metrics_overview` is a point-in-time snapshot

`GET /projects/{project_id}/metrics/overview` returns the current value of each overview metric. It takes no paging parameters (`NoPagination`) and has no stable timestamp to use as a cursor (`last_updated_at` changes on every refresh). The stream stays full refresh.

**Why this matters:** Do not make this stream incremental or add a paginator. Each sync replaces the previous snapshot, and the primary key `id` (for example `active_trials`) is unique only within one project.

## 5. Known defects held for a major release

These are breaking changes, so they wait for a 1.0.0 with a migration guide ([airbyte-internal-issues#18779](https://github.com/airbytehq/airbyte-internal-issues/issues/18779)):

- `customers_active_entitlements` uses primary key `[entitlement_id]`, which repeats across customers. Its cursor `expires_at` can be null or in the future.
- `metrics_overview` uses primary key `[id]`, which repeats across projects.
- `customers_subscriptions` uses cursor `starts_at`, which never changes, so status and period updates are not picked up again.
- `customers_purchases` uses cursor `purchased_at`, which never changes, so a purchase that later becomes `refunded` is not picked up again.
- `customers_invoices` uses cursor `issued_at`, which never changes, so a `paid_at` set after the invoice was first synced is not picked up again.
- `store_subscription_identifier` and `store_purchase_identifier` are declared `integer`, but the vendor schema says `string`. The `created_at`, `first_seen_at` and `last_seen_at` fields are declared `number`, but the vendor schema says `integer`.

**Why this matters:** Fixing any of these changes a primary key, cursor or column type in users' destinations. Ship them together in one major version with a `breakingChanges` entry, not in a patch or minor release.
