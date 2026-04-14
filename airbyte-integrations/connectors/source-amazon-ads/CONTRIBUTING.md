# source-amazon-ads: Unique Behaviors

## 1. Async Report Generation with Polling and Download

Report streams use the `AsyncRetriever` pattern instead of standard REST pagination. The connector creates a report via POST, polls a separate endpoint for the report's completion status, and then downloads the finished report from a URL provided in the polling response. This three-phase workflow (create → poll → download) means report streams have fundamentally different timing characteristics than standard entity streams: each report slice involves multiple sequential HTTP requests with wait intervals between polls.

The connector enforces a configurable `max_concurrent_async_job_count` (default 10) to limit how many reports are being generated simultaneously across all streams.

**Why this matters:** Report streams cannot be treated like standard paginated streams. They require polling intervals, have separate error handlers for creation vs. polling phases, and can take minutes to complete per slice. If you add a new report stream, you must configure all three phases (creation requester, polling requester, download requester) and their respective error handlers independently.

## 2. HTTP 425 (Too Early) for Duplicate Report Requests

When a user syncs the same report type with different time granularities simultaneously (e.g., daily and monthly versions of the same report), Amazon detects these as duplicate requests and returns HTTP 425. The connector treats this as a config error because the only fix is to either use separate sources for different granularities or set the number of concurrent threads to 2 for sequential processing.

**Why this matters:** HTTP 425 is extremely rare in REST APIs and is not handled by default error handlers. If you see a config error mentioning "duplicate report requests," it is not a credential or permission issue — it is a concurrency conflict that requires changing the source configuration or splitting into separate connections.
