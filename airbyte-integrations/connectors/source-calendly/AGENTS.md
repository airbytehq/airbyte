# source-calendly: Unique Connector Behaviors

## 1. Authentication Failures Stop the Sync, but Deleted Parent Events Do Not

Calendly personal access tokens created since March 2026 require explicit [authorization scopes](https://developer.calendly.com/docs/authentication/scopes). Keep one `DefaultErrorHandler` per requester and no `CompositeErrorHandler`: the shared handler classifies errors consistently, the invitee and routing-form-submission requesters override only the missing-parent 404, the fan-out requesters skip a stale member or event type (section 6), and the four plan-gated streams (contacts, outgoing communications, activity logs, meeting recaps) override only explicit upgrade/feature messages (section 7). Authentication messages tell the user how to fix the token and end with Calendly's response `message`. Keep the per-stream scope table in CONTRIBUTING.md synchronized with the connector docs.

| HTTP status | Base requester action / failure type | Invitee requester action / failure type | Meaning and response |
| --- | --- | --- | --- |
| 401 | `FAIL` / `config_error` | Same | Invalid or revoked token; create a new token (Profile menu, Developer, Personal access tokens, per [Calendly](https://developer.calendly.com/docs/authentication/how-to-authenticate-with-personal-access-tokens)) and update the source. |
| 403 | `FAIL` / `config_error` | Same | `Insufficient scope` (the body lists `required_scopes`, appended to the message); the message says the token needs the read scope of every selected stream, listed in the [source documentation](https://docs.airbyte.com/integrations/sources/calendly#token-scopes) and mirrored in [CONTRIBUTING.md](./CONTRIBUTING.md). `Permission Denied`: organization-wide `/scheduled_events` and `/webhook_subscriptions?scope=organization` need an owner or admin token, per the [OpenAPI spec](https://developer.calendly.com/openapi/calendly-api.yaml) and Calendly's [API conventions](https://developer.calendly.com/api-docs/overview/api/api-conventions). |
| 404 | `FAIL` / `system_error`, message names the URL | `IGNORE`, logged with the URL | A parent event can disappear between listing scheduled events and reading its invitees; skip that parent's invitees and continue. |
| 429 | `RATE_LIMITED` / `transient_error` (CDK default, no filter) | Same | Retry after the `X-RateLimit-Reset` delay; see [Calendly rate limits](https://developer.calendly.com/api-docs/overview/rate-limits). |
| 500, 502, 503, 504 | `RETRY` / `transient_error` | Same | Temporary Calendly server failure. |

**Why this matters:** Retrying invalid credentials hides an actionable configuration problem. Conversely, failing an invitee sync for a deleted parent prevents other events from syncing. Do not broaden the 404 ignore rule to the shared requester or change authentication failures into retries.

## 2. Rate-Limit Reset Headers Are Durations, Not Epoch Timestamps

Calendly documents [per-user rate limits](https://developer.calendly.com/api-docs/overview/rate-limits) of 500 requests/minute on paid plans and 50 requests/minute on free plans. The connector uses one 500/minute `MovingWindowCallRatePolicy` matching `https://api.calendly.com`, and updates it from `X-RateLimit-Remaining`. This lets paid plans use their allowance while a free plan waits when its remaining count reaches zero after its 50 requests; the configured ceiling is not a promise of 500 requests for every account. Concurrency is a fixed 4 worker threads.

Do not set the API budget's `ratelimit_reset_header` to `X-RateLimit-Reset`. CDK 7.45.0 parses that budget header as an epoch timestamp, but Calendly sends seconds until reset, typically 60. Leave the budget's default `ratelimit-reset` header unchanged: Calendly does not send it, so the moving-window policy applies the remaining count instead of skipping that update when a reset timestamp is present. A zero remaining count fills the window and blocks the next request until capacity is available.

Each requester's `WaitTimeFromHeader` reads `X-RateLimit-Reset`, which Calendly sends on every response, as seconds to wait before retrying a 429 or a 500, 502, 503 or 504. CDK adds one second, so a value of 60 normally produces a 61-second retry delay; a 5xx without the header backs off 1, 2, 4, 8 and 16 seconds.

**Why this matters:** Reusing the same reset header for the budget and retry handler looks natural but gives it two incompatible interpretations and prevents remaining-count updates. A fixed 50/minute ceiling unnecessarily throttles paid accounts; removing remaining-header handling risks repeated 429s on free accounts.

## 3. The Scheduled-Events Cursor Can Move Into the Future

`scheduled_events` uses `start_time`, not modification time, as its incremental cursor and sends only `min_start_time` (saved state minus `lookback_days`, bounded by the start date). Calendly returns upcoming events too, and CDK 7.45.0 saves the largest observed cursor value, so after a sync that reads an upcoming event the state is in the future. Later incremental syncs send `min_start_time` = that state minus `lookback_days` and make no `/scheduled_events` request while that point is still in the future, so bookings made in between for earlier times are never read. `event_invitees` follows this parent through `incremental_dependency: true`, so it stalls the same way. Fixing it changes emitted records and state, so it needs a breaking release; until then the docs tell users to sync both streams in Full refresh or to set `lookback_days` to their booking horizon.

`event_invitees` is not a data feed: the invitees endpoint has no date filter, and a `created_at` data feed dropped invitees booked before the start date in every sync mode. Each parent event's invitees are read in full and deduplicated by `uri`.

`lookback_days` is optional with default 0; keep `lookback_window: "P{{ [config.get('lookback_days') or 0, 0] | max }}D"`. The old `P{{config['lookback_days']}}D` rendered `PD` when the key was missing and caused an `ISO8601Error`; a negative value fails the same way, so the template clamps it to 0 instead of a spec minimum that would reject configs that still sync other streams.

`event_types` is a data feed sorted by `updated_at` descending, so pagination stops at the first record older than the cursor start. Its start is `1970-01-01`: a later floor (it was `2021-01-01`) silently drops every event type not updated since.

**Why this matters:** Treating either cursor as an update timestamp overstates freshness guarantees. Keep the missing-key-safe template and the parent dependency intact unless deliberately redesigning incremental state in a breaking release.

## 4. Existing Datetime Fields Intentionally Remain Strings Without Formats

Adding or changing `format` or `type` on an existing schema field is a breaking change for typed destinations. Existing datetime fields such as `start_time`, `end_time`, `created_at`, and `updated_at` intentionally remain string-valued fields without a datetime `format` for now, even where the [Calendly OpenAPI specification](https://developer.calendly.com/openapi/calendly-api.yaml) documents a timestamp. This includes properties already present inside cancellation objects.

New nullable fields may use documented formats, such as `date-time` inside the newly added `no_show` and `reconfirmation` objects. Do not use those additions as a reason to retype neighboring pre-existing fields. Schema tests preserve the exact type/format definitions of every field from the previous release and explicitly guard existing datetime fields against newly added formats.

**Why this matters:** Adding a format can change a destination column's type even when every API value stays the same. Keep schema expansion separate from breaking retypes and their migration requirements.

## 5. Connection Check Tests Only Current-User Access

The connection check reads `api_user` through `GET /users/me`, which requires `users:read` according to Calendly's [scope reference](https://developer.calendly.com/docs/authentication/scopes). It does not list event types or scheduled events and does not prove that the token has every scope needed by all selected streams, or that its owner is an organization owner or admin. Organization-scoped reads also obtain the current organization from this user response.

**Why this matters:** Switching the check back to a list stream creates unnecessary access requirements during setup. A successful check must not be presented as validation of all read scopes; missing stream-specific scopes still fail with an actionable 403 during a sync.

## 6. Organization-Member and Event-Type Fan-Out Streams

`user_availability_schedules` and `locations` partition on `organization_memberships` using `user/uri`, issuing one request per organization member; `event_type_memberships` partitions on `event_types` using `uri`. These three use `fan_out_error_handler`: a 404 (member or event type deleted mid-sync) and a 403 "This user is not in your organization" (member removed mid-sync) are skipped with an INFO log that names only the endpoint (CDK 7.45.0 strips the query string from `request_url`), while every other 403 still fails through the shared filter. Calendly documents the not-in-organization body for users outside the organization; if a live probe shows it for other members of a non-admin token, those members are skipped rather than failing the sync. The member-left filter matches only the message: CDK 7.45.0 ORs `http_codes` with `error_message_contains`, so adding `http_codes: [403]` would ignore every 403.

`teams` reads `GET /teams` once for the whole organization (the `user` parameter is an optional filter per Calendly's [OpenAPI spec](https://developer.calendly.com/openapi/calendly-api.yaml)); a per-member fan-out returned each team once per member under the same `uri`. `user_availability_schedules` and `locations` are not paginated, so their requests send only `user`. Location records have no identifier and Calendly's own example repeats a `kind` for one user, so `locations` has no primary key; the connector still adds `user` from the partition. `organization_invitations` uses the last path segment of `current_organization` as the organization UUID. `webhook_subscriptions` sends the required `scope` as `organization`, so user- and group-scoped subscriptions are not synced. Keep these streams out of `suggestedStreams`. New stream timestamps declare `format: date-time` (and `date` for availability rule dates); section 4 still governs existing streams.

**Why this matters:** The member- and event-type-based streams multiply requests, and one stale partition must not fail a long sync. Do not add a primary key Calendly does not guarantee: changing a key after release is a breaking change.

## 7. Plan-Gated Streams Skip Only Explicit Upgrade Messages

Outgoing communications and activity logs require Enterprise, meeting recaps require a paid plan with Notetaker features, and Calendly documents paid-plan and feature errors for contacts. Their stream-level `plan_gated_error_handler` inherits the shared backoff and puts a message-only IGNORE predicate before the shared filters. In CDK 7.45.0, `http_codes`, `predicate` and `error_message_contains` are ORed: never add `http_codes: [403]` to the plan filter, or all permission failures will be ignored.

The predicate strips a trailing period, because Calendly documents the paid-plan message both with and without it, and matches only these messages from the [OpenAPI specification](https://developer.calendly.com/openapi/calendly-api.yaml):

- `Please upgrade your Calendly account to Enterprise`
- `Please upgrade to a paid Calendly account`
- `Meeting recap access is not available. Required features are not enabled for your account`
- `Contact creation is not available. Required features are not enabled for your account` (documented for `GET /contacts`)

A body containing `required_scopes` must never match, even alongside an upgrade message. Both permission-denied variants and unknown 403 bodies fail through the shared config-error handler. CDK's IGNORE action logs the plan notice at INFO and completes the stream empty.

**Why this matters:** Plan unavailability is an expected empty stream, but invalid scopes or organization privileges require user action. A broad status filter hides misconfiguration.

## 8. New Incremental Streams Bound Both Requests and State

`outgoing_communications` uses `created_at` with `min_created_at`/`max_created_at`; `activity_log_entries` uses `occurred_at` with `min_occurred_at`/`max_occurred_at` and `sort=occurred_at:asc`; `meeting_recaps` uses meeting `start_time` with `start_time`/`end_time`. Each `DatetimeBasedCursor` ends at now and enables `is_client_side_incremental` to reject records beyond the request window before updating state. These cursors do not use the scheduled-events lookback.

Communications and activity logs use the current organization's URI from `api_user`. `activity_log_entries` uses `global_substream_cursor: true`, whose state adds a runtime `lookback_window` equal to the previous sync's duration, so each sync re-reads that span. `outgoing_communications` keeps per-partition state instead: it has no primary key, so a runtime lookback would emit duplicates nobody can remove. Recaps are token-scoped and use flat cursor state. Do not mark these as data feeds: the API does not guarantee descending cursor order for early pagination termination.

Calendly's recap `start_time` filter matches meetings that end at or after it and `end_time` matches meetings that start at or before it, and a recap is returned only once processing finishes. `meeting_recaps` therefore sets `lookback_window: P3D`, so a recap that becomes available after a later meeting's recap moved the cursor is still read; anything that becomes available or changes later than that needs Full refresh.

`routing_form_submissions` is full refresh, paginates every parent form, and sends `form=parent.uri` plus `sort=created_at:asc`. Its `submissions_error_handler` skips a 404 for a form deleted between the list and the submissions request and logs a notice; CDK 7.45.0 strips the query string from `request_url`, so the notice cannot name the form. Contacts send no organization parameter.

**Why this matters:** An unbounded cursor can stall future syncs, and a cursor that is not an update timestamp needs an explicit re-read window. Keep each stream's state shape: changing it later is a breaking change.

## 9. Outgoing Communications Have No Documented Unique Identifier

The OpenAPI email/SMS variants expose `created_at`, `event_uri`, `type`, `to`, and other message fields, but neither has a `uri` or documented stable ID. Keep `primary_key: []`; do not synthesize an allegedly unique key from fields without a uniqueness guarantee. Deduplicated modes need a primary key the user selects, and no field combination is guaranteed unique, so the docs recommend overwrite or append.

**Why this matters:** Declaring a nonexistent field breaks deduplication; inventing a composite can collapse distinct messages. Mock records must use the actual email/SMS shapes, not a fabricated URI.
