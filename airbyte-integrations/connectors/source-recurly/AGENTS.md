# source-recurly: Unique Connector Behaviors

## 1. Site-wide quota versus per-sync budget

Recurly documents 400 requests/minute for sandbox sites and 1,000 GET requests/minute for production sites, enforced over a sliding five-minute window (`X-RateLimit-Limit` reports 2,000 for sandbox). The `api_budget` paces requests to 2,000 or 5,000 per five minutes based on `is_sandbox`, and matches every `GET` to `https://v3.recurly.com`. The budget is per sync, while Recurly's limit is per site, so other connections or integrations using the same site can still cause HTTP 429 responses. See [Recurly API limits](https://recurly.com/developers/api/v2021-02-25/index.html#section/Getting-Started/Limits).

**Why this matters:** Concurrent connections can exhaust the shared site quota even when each sync stays within its own budget. Increasing concurrency does not increase the site's allowance.

## 2. Reset header is not a retry timer

The requester uses exponential backoff (factor 5, five retries) for rate-limited and server error responses. The waits are approximately 11, 21, 41, 81, and 161 seconds, totaling about 315 seconds: longer than Recurly's five-minute quota window.

The handler does not use `WaitUntilTimeFromHeader` on `X-RateLimit-Reset`. Recurly sends that header on every response, and the CDK applies backoff strategies to every retryable response, so a header-based wait would also delay 5xx retries by up to five minutes. A `CompositeErrorHandler` does not help, because it merges the backoff strategies of its child handlers into one list.

The budget declares `X-RateLimit-Reset`, so `MovingWindowCallRatePolicy` ignores the response headers instead of marking its bucket full after a 429.

**Why this matters:** Replacing exponential backoff with a reset-header wait can delay unrelated server-error retries. Preserve the distinction between request pacing and retry timing when changing throttling.

## 3. Usage Records fan-out

Every Usage Records sync pages through all subscriptions using the internal `subscription_add_ons_parent` stream, without a date filter or saved incremental progress. It extracts each subscription's `add_ons`, then requests `/subscriptions/{subscription_id}/add_ons/{add_on_id}/usage` for each add-on, with `billing_status: all` to include billed and unbilled usage. Each request can itself require pagination.

**Why this matters:** Selecting one stream triggers a subscription scan plus a separate, potentially paginated request per subscription add-on. Large sites can consume much of the shared API quota even when few usage records have changed.

## 4. Positional error-filter coupling

`missing_feature_error_handler` first ignores responses whose `error.type` is `missing_feature`. It then reuses `#/definitions/base_requester/error_handler/response_filters/0` and `#/definitions/base_requester/error_handler/response_filters/1`, which must remain the 401 and 403 configuration-error filters, respectively. Its `max_retries` and `backoff_strategies` also reference the corresponding properties of the base handler.

This handler is used by Account Acquisitions, Gift Cards, External Subscriptions, External Subscription Payment Phases, Items, Usage Records, and the internal subscription add-ons parent stream.

**Why this matters:** Inserting or reordering base response filters silently changes which errors these seven streams handle. Preserve or update the positional references together with the base filters so missing features remain skippable while authentication errors still fail.
