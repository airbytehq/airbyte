> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-pinterest: Unique Behaviors

## 1. Analytics Retry Wait Time Parsed from Response Body Text

The `PinterestAnalyticsBackoffStrategy` extracts the retry wait time from the response body's `message` field using a regex pattern (`Retry after N seconds`), not from standard HTTP headers like `Retry-After`. Pinterest's analytics endpoints return rate limit information as human-readable text embedded in the error message rather than in response headers.

**Why this matters:** Standard retry logic that only reads HTTP headers will miss Pinterest's retry guidance entirely and fall back to exponential backoff. The connector's regex-based extraction is brittle and will break if Pinterest changes the wording of their error message. If the regex fails to match, it falls back to exponential backoff capped at 120 seconds.

## 2. Analytics Errors Must Not Skip Partitions

The synchronous analytics retriever uses one `DefaultErrorHandler`, inheriting `PinterestAnalyticsBackoffStrategy` and referencing the shared analytics filters. It retains retries for every HTTP 400 (CDK matches `http_codes` OR `predicate`) and HTTP 409; it does not inherit the base handler's 409 `IGNORE`. HTTP 429 uses the Pinterest rate-limit message when the body has `code: 8`, otherwise the default 429 message. Body-only `code: 8` does not override other HTTP classifications, including successful responses. The re-authentication message is restricted to HTTP 401. The shared base and async report-creation handlers remain independent.

**Why this matters:** Copying the base handler's filters into analytics would silently skip 409 partitions and treat successful `code: 8` payloads as rate-limited. Keep those filters separate when changing analytics error handling.

## Incremental Stream Considerations

The Pinterest API supports date-based filtering on analytics endpoints. The connector uses Python custom components referenced from the manifest.

**Connector type:** Python custom components (hybrid manifest + Python)

**Analysis status:** Streams are Python-defined via custom components. Full stream-by-stream analysis requires Python code review.

### Future incremental stream candidates

- **All streams deferred for Python code review:** This connector defines its streams in Python code rather than declarative manifest YAML. A full stream-by-stream incremental analysis table (per the standard CONTRIBUTING.md schema) should be added by a future agent after reviewing the Python stream definitions, their `cursor_field` properties, and the API endpoints they call.
