# source-intercom: Unique Behaviors

## 1. Proactive Rate Limiting Before Every Request

The connector uses a custom `ErrorHandlerWithRateLimiter` that wraps the standard error handler with a decorator-based rate limiter. Unlike typical backoff strategies that only activate after hitting a rate limit, this limiter adds a sleep BEFORE every single API request based on the ratio of remaining requests to the total rate limit capacity (from `X-RateLimit-Remaining` and `X-RateLimit-Limit` headers).

The sleep duration scales dynamically: 10ms when load is low (>50% capacity remaining), 1.5 seconds at medium load, and 8 seconds when remaining capacity drops below 10%. If headers are unavailable, it defaults to a 1-second hold.

**Why this matters:** The connector intentionally throttles itself even when not rate-limited, trading sync speed for stability. This means syncs will always be slower than the raw API rate limit would allow, and the slowdown increases as rate limit capacity decreases during a sync. This is not a bug but a deliberate design choice that may look like unnecessary latency if you are not aware of it.
