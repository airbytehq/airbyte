# source-intercom: Unique Behaviors

## 1. Proactive Rate Limiting Before Every Request

The connector uses a custom `ErrorHandlerWithRateLimiter` that wraps the standard error handler with a decorator-based rate limiter. Unlike typical backoff strategies that only activate after hitting a rate limit, this limiter adds a sleep BEFORE every single API request based on the ratio of remaining requests to the total rate limit capacity (from `X-RateLimit-Remaining` and `X-RateLimit-Limit` headers).

The sleep duration scales dynamically: 10ms when load is low (>50% capacity remaining), 1.5 seconds at medium load, and 8 seconds when remaining capacity drops below 10%. If headers are unavailable, it defaults to a 1-second hold.

**Why this matters:** The connector intentionally throttles itself even when not rate-limited, trading sync speed for stability. This means syncs will always be slower than the raw API rate limit would allow, and the slowdown increases as rate limit capacity decreases during a sync. This is not a bug but a deliberate design choice that may look like unnecessary latency if you are not aware of it.

## 2. Companies Scroll API — Single Active Scroll Constraint

The `companies` stream uses Intercom's Scroll API (`companies/scroll`) instead of standard cursor pagination. Intercom enforces a hard constraint: **only one scroll can be active per workspace at a time**. If a second scroll request is made while one is already in progress, the API returns HTTP 400. The connector treats this as a `transient_error` with the message: "Scroll already exists for this workspace. Please ensure you do not have multiple syncs running at the same time."

This constraint also applies to any substream that uses `companies` as a parent — specifically `company_segments` and `company_attributes`. Since these streams depend on iterating over company records, they inherit the single-scroll limitation. Running two syncs that involve any combination of companies, company_segments, or company_attributes against the same Intercom workspace simultaneously will cause one to fail.

Additionally, on HTTP 500 the connector uses `RESET_PAGINATION` to restart the scroll from the beginning, meaning a transient server error can cause the entire companies stream to re-read all data.

**Why this matters:** Unlike standard paginated streams where multiple readers can paginate independently, the scroll API is a workspace-level singleton. This makes it impossible to run parallel syncs or test syncs against the same Intercom workspace if any of them include the companies stream or its dependents.
