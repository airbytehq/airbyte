> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-zendesk-support: Unique Behaviors

## 1. Tickets Incremental Export Uses `generated_timestamp`, Not `updated_at`

The tickets stream uses Zendesk's [Time Based Incremental Ticket Export](https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/#incremental-ticket-export-time-based) (`GET /api/v2/incremental/tickets.json?start_time={unix_time}`). This endpoint compares `start_time` against each ticket's `generated_timestamp`, **not** its `updated_at` value. The `generated_timestamp` is updated on every ticket change (including silent system updates), while `updated_at` only changes when a [ticket event](https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/#incremental-ticket-event-export) is generated. This means the API can return tickets whose `updated_at` is earlier than the requested `start_time`, because a system update bumped the `generated_timestamp` after the last user-visible change.

**Why this matters:** `updated_at` is not a reliable cursor for this endpoint. If you filter or deduplicate based on `updated_at`, you will misclassify tickets — some will appear "stale" despite being legitimately returned by the API. The connector uses `generated_timestamp` as the true cursor.

## 2. StateDelegatingStream for Ticket Metrics — Two Completely Different Sync Paths

The `ticket_metrics` stream uses `StateDelegatingStream` to choose between two completely different retrieval strategies based on whether stream state exists:

**Without state (initial sync / full refresh) — `StatelessTicketMetrics`:**
Queries the bulk `GET /ticket_metrics` endpoint, which returns records sorted by `created_at` descending (newest first). However, the cursor field is `updated_at`, not `created_at`. Because the sort order doesn't match the cursor field, the stream **must read all records** and cannot checkpoint mid-stream (checkpointing would create state, which would switch to the stateful path on the next page). The stream tracks the most recent `updated_at` value across all records and converts it to a unix timestamp saved as `_ab_updated_at` in state:
```json
{ "_ab_updated_at": 1728670522 }
```

**With state (incremental syncs) — `StatefulTicketMetrics`:**
Uses a two-step approach: first queries `GET /tickets/cursor.json` to get updated ticket IDs (filtered by `generated_timestamp`), then fetches `GET /tickets/{ticket_id}/metrics` for each ticket. This is more efficient for small deltas but makes one API call per updated ticket. The `generated_timestamp` from the tickets endpoint is converted to the `_ab_updated_at` state cursor to maintain consistency with the stateless path.

**Why this matters:** The synthetic `_ab_updated_at` cursor bridges two fundamentally different data flows. The stateless path is efficient for initial bulk loads but cannot checkpoint. The stateful path scales linearly with the number of updated tickets — efficient for small incremental syncs but disastrous if state is reset and it tries to re-read all tickets one by one. Understanding which path is active (based on state presence) is critical for diagnosing performance issues.

## 3. Enterprise-Only Streams Disabled at Manifest Level

Several streams (`ticket_forms`, `account_attributes`, `attribute_definitions`) are commented out in the manifest because they require Zendesk Enterprise plans and the CDK does not yet support `ConditionalStreams` based on API endpoint availability. The `ticket_forms` stream definition exists but will FAIL with a descriptive error on 403/404 rather than being silently skipped.

**Why this matters:** These streams cannot be enabled without CDK changes to support conditional stream availability. If a user on an Enterprise plan expects these streams, they will not appear in the catalog at all despite the stream definitions existing in the manifest.

## 4. Ticket Events Stream — Raw Incremental Ticket Event Export

The `ticket_events` stream uses Zendesk's [Incremental Ticket Event Export](https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/#incremental-ticket-event-export) (`GET /api/v2/incremental/ticket_events.json`). Unlike the `ticket_comments` stream which also hits this endpoint but extracts only Comment child events, `ticket_events` returns the full top-level ticket event objects (including all child events). The cursor field is `timestamp` (unix epoch), filtered via `start_time`. Pagination uses `end_of_stream` to signal the last page.

**Why this matters:** This stream is distinct from `ticket_comments` — both use the same API endpoint but extract different data. `ticket_comments` uses a custom extractor (`ZendeskSupportExtractorEvents`) to drill into `child_events` and filter for Comment events. `ticket_events` uses the default `DpathExtractor` to return the raw ticket event envelope, giving users access to all event types and metadata.

## Incremental Stream Considerations

The Zendesk Support API supports incremental export endpoints (`/api/v2/incremental/...`) for tickets, users, organizations, and other high-volume resources. The connector uses Python custom components referenced from the manifest.

**Connector type:** Python custom components (hybrid manifest + Python)

**Analysis status:** Streams are Python-defined via custom components. The connector is mature with extensive incremental support already in place via Zendesk's incremental export API.

### Future incremental stream candidates

- **All streams deferred for Python code review:** This connector defines its streams in Python code rather than declarative manifest YAML. A full stream-by-stream incremental analysis table (per the standard CONTRIBUTING.md schema) should be added by a future agent after reviewing the Python stream definitions, their `cursor_field` properties, and the API endpoints they call.
