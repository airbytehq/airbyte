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

`side_conversations`, the stateful `ticket_metrics` path and the `ticket_audits_per_ticket` stream all request one URL per parent ticket (`GET /tickets/{ticket_id}/side_conversations`, `GET /tickets/{ticket_id}/metrics`, `GET /tickets/{ticket_id}/audits.json`). All three use IGNORE filters keyed exclusively on `http_codes`, and that is deliberate on two counts:

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

## 7. `ticket_audits_per_ticket` Exists Because `ticket_audits` Cannot See Archived Tickets

`ticket_audits` reads `GET /api/v2/ticket_audits`, which Zendesk documents as excluding archived tickets (closed tickets are archived about 120 days after they close) and as unsuitable for change data capture. A bulk update of archived tickets therefore writes audits that `ticket_audits` never returns. `ticket_audits_per_ticket` reads `GET /api/v2/tickets/{ticket_id}/audits.json` for each ticket the `tickets` incremental export returns, and that endpoint does return archived tickets' audits. `ticket_audits` was deliberately left unchanged: switching it to the per-ticket endpoint would change its state shape and make every user pay the per-ticket cost.

How it is built, and why:

1. **Opt-in through stream selection only: no spec flag, no `ConditionalStreams`.** The stream is always discovered, like every other stream. It is left out of `metadata.yaml` `suggestedStreams`, so a new connection does not select it by default, and an existing connection only starts syncing it when the user selects it or the connection automatically enables new streams. That auto-enable case is the one users must act on, so the user docs and changelog warn about it.
2. **Global substream cursor.** The cursor mirrors the stateful `ticket_metrics` path (`_ab_updated_at` = the parent ticket's `generated_timestamp`, via `extra_fields` and `AddFields`), but `global_substream_cursor: true` stores one cursor value instead of one entry per ticket. Each changed ticket re-emits all of its audits; `id` deduplicates them downstream.
3. **No `api_budget` policy of its own.** Like the per-ticket `ticket_metrics` calls (`GET /tickets/{ticket_id}/metrics`), `^/api/v2/tickets/\d+/audits` matches no policy, so requests go out at the connector's concurrency and count against the account-wide plan limit shared with other integrations. On a `429` the error handler waits for `Retry-After` (`WaitTimeFromHeader`). The parent walk is a separate pass over the incremental ticket export and stays under that endpoint's 10 req/min policy. Do not add a broad policy that matches `^/api/v2/tickets/` without deciding what it does to this stream and `ticket_metrics`.
4. **Pagination** reuses `links_next_paginator` (`page[size]=100`, `links.next`, `meta.has_more`). Zendesk returns audits for archived tickets unpaginated; a response without `meta.has_more` stops after one page.
5. **Schema** `schemas.ticket_audits_per_ticket` `$ref`s each `ticket_audits` property and adds `_ab_updated_at`. A unit test fails if `ticket_audits` gains a property this schema does not list.

**Why this matters:** do not add the stream to `suggestedStreams`. That would select it on every new connection, exposing users who never asked for archived-ticket audits to a request per updated ticket, and a single bulk update can mean six-figure request counts on the next sync. The first sync after the stream is selected reads every ticket since `start_date`, which is also how a user backfills archived-ticket audits.

## 8. Zendesk Marketplace Headers Are Sent in Airbyte Cloud Only, Through a Derived Config Key

Zendesk asks Marketplace integrations to send `X-Zendesk-Marketplace-Name`, `X-Zendesk-Marketplace-Organization-Id` and `X-Zendesk-Marketplace-App-Id` on [every request made from outside the Zendesk Apps framework](https://developer.zendesk.com/documentation/marketplace/building-a-marketplace-app/request-header-requirements-for-marketplace-apps/). In Airbyte Cloud the connector sends them on every data request, on article attachment downloads and on the OAuth token refresh, for every authentication option. Self-managed deployments send none: they run with the customer's own OAuth client or API token, and their traffic should not be attributed to Airbyte's Marketplace listing.

How it is built, and why:

1. **The edition reaches the manifest through the config.** Interpolation cannot read the environment, so `MarketplaceHeaders` in `components.py` (a `CustomConfigTransformation` under `spec.config_normalization_rules.transformations`) sets `config['__marketplace_headers']` when `AIRBYTE_EDITION` is `CLOUD` and removes the key otherwise. The gate reads `AIRBYTE_EDITION`, not the CDK's `is_cloud_environment()`, which reads `DEPLOYMENT_MODE`.
2. **Three places read the key, and each has to.** `definitions.retriever.requester` covers every stream that `$ref`s it. The `file_uploader` requester of `article_attachments` is written out separately and repeats `request_headers`. `oauth_refresh_authenticator` lists the three headers under `refresh_request_headers`; a header that evaluates to `None` is not sent.
3. **`$ref` with siblings is a shallow merge.** A stream that sets `request_headers` next to `$ref: "#/definitions/retriever/requester"` replaces the Marketplace headers instead of adding to them. `test_every_requester_in_the_manifest_sends_the_marketplace_headers` walks the resolved manifest and fails on any `HttpRequester` without the template, and on any `CustomRequester`.
4. **The key is derived on every run, but it can end up in the stored config.** A transformation is not persisted by itself. The single-use refresh-token flow, however, emits the whole in-memory config as a control message when the token rotates, so a Cloud source on `OAuth2.0 with Refresh Token` stores `__marketplace_headers`. That is harmless: the spec allows additional properties, the transformation overwrites the key in Cloud and removes it elsewhere, and the values are not secret.
5. **The authorization-code exchange is made by the platform, not by the connector.** It does not send these headers. `advanced_auth.oauth_config_specification.oauth_connector_input_specification` accepts `access_token_headers` if Zendesk asks for them there too.

**Why this matters:** a new requester that is written out instead of `$ref`'d, or a custom component that makes its own HTTP call, silently sends no Marketplace headers. The IDs live in `MARKETPLACE_HEADERS` in `components.py`; `test_marketplace_ids_are_not_placeholders` fails while either is a placeholder.

## Incremental Stream Considerations

The Zendesk Support API supports incremental export endpoints (`/api/v2/incremental/...`) for tickets, users, organizations, and other high-volume resources. The connector uses Python custom components referenced from the manifest.

**Connector type:** Python custom components (hybrid manifest + Python)

**Analysis status:** Streams are Python-defined via custom components. The connector is mature with extensive incremental support already in place via Zendesk's incremental export API.

### Future incremental stream candidates

- **All streams deferred for Python code review:** This connector defines its streams in Python code rather than declarative manifest YAML. A full stream-by-stream incremental analysis table (per the standard CONTRIBUTING.md schema) should be added by a future agent after reviewing the Python stream definitions, their `cursor_field` properties, and the API endpoints they call.
