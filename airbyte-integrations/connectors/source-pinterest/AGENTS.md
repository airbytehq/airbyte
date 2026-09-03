> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-pinterest: Unique Behaviors

## 1. Analytics Retry Wait Time Parsed from Response Body Text

The `PinterestAnalyticsBackoffStrategy` extracts the retry wait time from the response body's `message` field using a regex pattern (`Retry after N seconds`), not from standard HTTP headers like `Retry-After`. Pinterest's analytics endpoints return rate limit information as human-readable text embedded in the error message rather than in response headers.

**Why this matters:** Standard retry logic that only reads HTTP headers will miss Pinterest's retry guidance entirely and fall back to exponential backoff. The connector's regex-based extraction is brittle and will break if Pinterest changes the wording of their error message. If the regex fails to match, it falls back to exponential backoff capped at 120 seconds.

## Incremental Stream Considerations

The Pinterest API supports date-based filtering on analytics endpoints. The connector uses Python custom components referenced from the manifest.

**Connector type:** Python custom components (hybrid manifest + Python)

**Analysis status:** Streams are Python-defined via custom components. Full stream-by-stream analysis requires Python code review.

### Future incremental stream candidates

- **All streams deferred for Python code review:** This connector defines its streams in Python code rather than declarative manifest YAML. A full stream-by-stream incremental analysis table (per the standard CONTRIBUTING.md schema) should be added by a future agent after reviewing the Python stream definitions, their `cursor_field` properties, and the API endpoints they call.
