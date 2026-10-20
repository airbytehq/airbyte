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

## 5. Per-Ticket Substreams Must Key Error Handling on the Status Code, Not the Response Body

`side_conversations` and the stateful `ticket_metrics` path both request one URL per parent ticket (`GET /tickets/{ticket_id}/side_conversations`, `GET /tickets/{ticket_id}/metrics`). Both use IGNORE filters keyed exclusively on `http_codes`, and that is deliberate on two counts:

1. **Zendesk does not guarantee a response body.** Permission denials from the `collaboration-api` service arrive as a `403` with an empty `text/html` body. `HttpResponseFilter._response_contains_error_message` parses the body with `JsonErrorMessageParser`, which yields nothing for a non-JSON body, so an `error_message_contains` filter silently never matches. The same emptiness makes `{{ response.get('error') }}` render as `None` in any error message template.
2. **Denial is scoped to the ticket, not to the stream.** Side conversations require the Collaboration add-on and can be restricted per brand and per group, and the `tickets` incremental export also returns deleted tickets. So individual tickets are refused (`403`) or gone (`404`) while the rest of the stream reads normally. Failing the sync on one refused ticket blocks the whole stream.

There is a second-order trap here. Because these are substreams with `incremental_dependency: true`, the parent cursor is only checkpointed once the substream finishes. A refusal that fails the stream therefore prevents `parent_state` from ever advancing, so the next sync restarts the parent walk from the same position and fails on the same ticket forever — no self-healing, and heavy rate-limit pressure from re-walking the parent every run.

**Why this matters:** the shared `definitions.retriever.requester.error_handler` treats `403`/`404` as a whole-stream configuration error, which is correct for stream-level endpoints and wrong for per-partition ones. Any new substream that requests one URL per parent record needs its own status-code-keyed handler; inheriting the shared one lets a single unreachable parent record fail the sync. Note that `error_message_contains` is also unreliable in the shared handler for the same body-shape reason.

## 6. `num_workers` Minimum Is 2 — One Thread Leaves No Sibling to Beat the Heartbeat

The floor is enforced in three places, and all three are load-bearing:

1. the spec pins `num_workers` to `minimum: 2`;
2. `spec.config_normalization_rules` carries a `ConfigMigration` that rewrites a stored `num_workers: 1` to `2`;
3. `concurrency_level.default_concurrency` clamps with `{{ [config.get('num_workers', 4), 2] | max }}`.

The clamp is not redundant with the migration. In CDK 7.23.8 and later (unfixed as of 7.28.3, tracked in [airbyte-python-cdk#1147](https://github.com/airbytehq/airbyte-python-cdk/issues/1147)) `ConcurrentDeclarativeSource.__init__` builds the `ConcurrencyLevel` component from the **pre-migration** config (`config=config or {}`, not `self._config`), so on the first sync after an upgrade a stored `1` would still run a single worker — exactly the sync that needs two. Verified locally: with a stored `num_workers: 1`, `self._config['num_workers']` is `2` while the thread pool is built with `max_workers=1`. The clamp makes the floor effective immediately; the migration keeps the persisted config consistent with the spec minimum. If the CDK is fixed to interpolate the migrated config, the clamp becomes redundant but stays harmless.

Unclamped, `default_concurrency` is `config.get('num_workers', 4)`, so `num_workers: 1` makes the concurrent framework run a single worker thread and every stream is processed strictly one at a time. The `tickets` stream is the problem case: it reads the Incremental Ticket Export endpoint, which the `api_budget` limits to 10 requests per minute, and it uses `cursor_incremental_sync` with no `step` and no `end_datetime`, so the whole date range is a single partition. The concurrent cursor only emits state when a partition closes, so a long `tickets` walk produces no state message until it finishes.

The platform heartbeat resets on a RECORD **or** a STATE message. With two or more workers, a sibling stream keeps emitting during the walk and the sync stays alive. With one worker there is no sibling: once `tickets` is past its first pages, nothing is emitted at all, and the platform cancels the attempt at the `heartbeat-max-seconds-between-messages` threshold (5400s on Cloud). Because the partition never closes, no cursor is checkpointed, so every retry re-enters the identical state and the connection is wedged permanently rather than making partial progress.

What `airbytehq/oncall#13250` establishes is narrower than the mechanism above: every wedged connection ran 1 thread, and one thread leaves no sibling stream to keep the heartbeat alive during the `tickets` walk. Why that walk runs beat-free long enough to trip the threshold is not confirmed (the sync logs carry no source stdout), and a second worker only helps while sibling streams still have work. Treat the floor as a mitigation, not as the root-cause fix.

**Why this matters:** the failure looks unrelated to concurrency — the heartbeat error names whichever stream happens to be queued (often `group_memberships`), not `tickets`, and the sync logs carry no source stdout. Adding a `step` to `tickets` is not an alternative fix: the endpoint accepts `start_time` with no end bound, so each slice re-walks to the present and duplicates records. See `airbytehq/oncall#13250`.

## 7. `ticket_comments` Pages by `start_time`, Not `next_page`, So a Timed-Out Page Can Shrink

`ticket_comments` reads `GET /incremental/ticket_events.json?include=comment_events`. A heavy page makes Zendesk answer `504`, and re-issuing the identical request asks it to do the same work again. So the `504` filter uses `action: REDUCE_PAGE_SIZE` with a retriever-level `page_size_reduction`: the same page is re-requested with half the `per_page` (down to 1), and `reset_policy: AFTER_SUCCESSFUL_PAGE` restores the configured size on the next page. The stream is a single partition, so `NEVER` would keep the reduced size for the rest of the sync after one heavy page.

This forces the paginator shape. The CDK (7.35.0) rejects `page_size_reduction` with a `RequestPath` page token, because the `next_page` URL Zendesk builds already carries the original `per_page` and the reduced size would be sent next to it. The paginator is therefore a `CursorPagination` with `cursor_value: '{{ response.get("end_time") }}'` injected as the `start_time` request parameter. That is what `next_page` contains anyway: verified on a test account, `next_page` is the same request plus `start_time=<end_time>`, and requesting it directly returns the identical events and the identical next `end_time`. A response without `end_time` yields no token and ends the pagination instead of re-requesting the first page.

Details that keep this correct:

- `ignore_stream_slicer_parameters_on_paginated_requests: true` keeps the cursor's own `start_time` off every page but the first; without it the two `start_time` values collide. `include` is a requester parameter, which that flag never drops.
- The paginator is inline on purpose. `end_of_stream_paginator` is shared by `ticket_events`, `ticket_metric_events` and others that are not set up for page size reduction; do not edit it for this stream.
- The `stop_condition` must not compare `last_page_size` (or a count from the body) against a fixed number: a full page at a reduced size would read as the last page and silently drop the rest of the stream. `end_of_stream` is safe.
- The reduction path ignores `backoff_strategies` and `Retry-After`, so `backoff_seconds` (10, multiplied by the attempt number) and `retries_at_minimum_page_size` (3) carry the waiting: a `504` here can also mean Zendesk is briefly overloaded. `failure_type` is not set on the filter because `HttpResponseFilter` only applies it to `FAIL`.
- Zendesk keeps events that share a `generated_timestamp` on one page, so a page can exceed `per_page` and no reduction can split such a group.

The default page size is 1000. The setup form saves the spec default, so most configs stored the old default of 100 explicitly; a `ConfigMigration` rewrites exactly `100` (int or numeric string) to `1000` and leaves every other value, which users set on purpose (usually lowered after timeouts). `page_size` is top-level, so the migrated config is emitted as `CONNECTOR_CONFIG` and persisted.

## Incremental Stream Considerations

The Zendesk Support API supports incremental export endpoints (`/api/v2/incremental/...`) for tickets, users, organizations, and other high-volume resources. The connector uses Python custom components referenced from the manifest.

**Connector type:** Python custom components (hybrid manifest + Python)

**Analysis status:** Streams are Python-defined via custom components. The connector is mature with extensive incremental support already in place via Zendesk's incremental export API.

### Future incremental stream candidates

- **All streams deferred for Python code review:** This connector defines its streams in Python code rather than declarative manifest YAML. A full stream-by-stream incremental analysis table (per the standard CONTRIBUTING.md schema) should be added by a future agent after reviewing the Python stream definitions, their `cursor_field` properties, and the API endpoints they call.
