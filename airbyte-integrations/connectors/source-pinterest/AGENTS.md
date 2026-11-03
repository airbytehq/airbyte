> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-pinterest: Unique Behaviors

## 1. Analytics Retry Wait Time Parsed from Response Body Text

The `PinterestAnalyticsBackoffStrategy` extracts the retry wait time from the response body's `message` field using a regex pattern (`Retry after N seconds`), not from standard HTTP headers like `Retry-After`. Pinterest's analytics endpoints return rate limit information as human-readable text embedded in the error message rather than in response headers.

**Why this matters:** Standard retry logic that only reads HTTP headers will miss Pinterest's retry guidance entirely and fall back to exponential backoff. The connector's regex-based extraction is brittle and will break if Pinterest changes the wording of their error message. If the regex fails to match, it falls back to exponential backoff capped at 120 seconds.

## 2. Targeting Columns Are Returned, Not Requested

Targeting-level async reports (`*_targeting_report` streams and custom reports at a `*_TARGETING` level) come back with `TARGETING_TYPE` and `TARGETING_VALUE` on every row even though the report request never lists them. The report endpoint rejects `TARGETING_TYPE`, `TARGETING_VALUE`, `TARGETING_VALUE_NAME`, `KEYWORD_ID`, `PRODUCT_ITEM_ID` and `ITEM_ID` in `columns` with a 400 (`'<COLUMN>' is not one of [...]`), although Pinterest's OpenAPI `ReportingColumn` enum lists all of them. The endpoint's own allowlist is the list in that 400 message.

**Why this matters:** never add these columns to a report request; it fails report creation for every stream that shares the column list. To expose a column that Pinterest adds on its own, declare it in `reports_schema` and `custom_reports_schema` instead. Destinations build typed columns from the declared schema, so an undeclared column gets no column of its own.

## Incremental Stream Considerations

The Pinterest API supports date-based filtering on analytics endpoints. The connector uses Python custom components referenced from the manifest.

**Connector type:** Python custom components (hybrid manifest + Python)

**Analysis status:** Streams are Python-defined via custom components. Full stream-by-stream analysis requires Python code review.

### Future incremental stream candidates

- **All streams deferred for Python code review:** This connector defines its streams in Python code rather than declarative manifest YAML. A full stream-by-stream incremental analysis table (per the standard CONTRIBUTING.md schema) should be added by a future agent after reviewing the Python stream definitions, their `cursor_field` properties, and the API endpoints they call.
