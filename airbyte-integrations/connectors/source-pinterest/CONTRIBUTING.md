# source-pinterest: Unique Behaviors

## 1. Analytics Retry Wait Time Parsed from Response Body Text

The `PinterestAnalyticsBackoffStrategy` extracts the retry wait time from the response body's `message` field using a regex pattern (`Retry after N seconds`), not from standard HTTP headers like `Retry-After`. Pinterest's analytics endpoints return rate limit information as human-readable text embedded in the error message rather than in response headers.

**Why this matters:** Standard retry logic that only reads HTTP headers will miss Pinterest's retry guidance entirely and fall back to exponential backoff. The connector's regex-based extraction is brittle and will break if Pinterest changes the wording of their error message. If the regex fails to match, it falls back to exponential backoff capped at 120 seconds.
