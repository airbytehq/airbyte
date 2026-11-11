# source-recurly: Unique Connector Behaviors

## 1. Site-wide quota versus per-sync budget

Recurly documents 400 requests/minute for sandbox sites and 1,000 GET requests/minute for production sites, enforced over a sliding five-minute window (`X-RateLimit-Limit` reports 2,000 for sandbox). The `api_budget` paces requests to 2,000 or 5,000 per five minutes based on `is_sandbox`, and matches every `GET` to `https://v3.recurly.com`. The budget is per sync, while Recurly's limit is per site, so other connections or integrations using the same site can still cause HTTP 429 responses. See [Recurly API limits](https://recurly.com/developers/api/v2021-02-25/index.html#section/Getting-Started/Limits).

**Why this matters:** Concurrent connections can exhaust the shared site quota even when each sync stays within its own budget. Increasing concurrency does not increase the site's allowance.

## 2. Reset header is not a retry timer

The requester uses exponential backoff (factor 5, five retries) for rate-limited and server error responses.

The handler does not use `WaitUntilTimeFromHeader` on `X-RateLimit-Reset`. Recurly sends that header on every response, and the CDK applies backoff strategies to every retryable response, so a header-based wait would also delay 5xx retries by up to five minutes. A `CompositeErrorHandler` does not help, because it merges the backoff strategies of its child handlers into one list.

The budget declares `X-RateLimit-Reset`, so `MovingWindowCallRatePolicy` ignores the response headers instead of marking its bucket full after a 429.

**Why this matters:** Replacing exponential backoff with a reset-header wait can delay unrelated server-error retries. Preserve the distinction between request pacing and retry timing when changing throttling.
