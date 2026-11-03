# source-calendly: Unique Connector Behaviors

## 1. Authentication Failures Stop the Sync, but Deleted Parent Events Do Not

Calendly personal access tokens created since March 2026 require explicit [authorization scopes](https://developer.calendly.com/docs/authentication/scopes). Keep one `DefaultErrorHandler` per requester and no `CompositeErrorHandler`: the shared handler classifies errors consistently, while the invitee requester overrides only the missing-parent case. Authentication messages tell the user how to fix the token and end with Calendly's response `message`.

| HTTP status | Base requester action / failure type | Invitee requester action / failure type | Meaning and response |
| --- | --- | --- | --- |
| 401 | `FAIL` / `config_error` | Same | Invalid or revoked token; create a new token (Profile menu, Developer, Personal access tokens, per [Calendly](https://developer.calendly.com/docs/authentication/how-to-authenticate-with-personal-access-tokens)) and update the source. |
| 403 | `FAIL` / `config_error` | Same | `Insufficient scope` (the body lists `required_scopes`, appended to the message); the message says the token needs the read scope of every selected stream and points to the per-stream scope table in [CONTRIBUTING.md](./CONTRIBUTING.md) and the [source documentation](https://docs.airbyte.com/integrations/sources/calendly). `Permission Denied`: organization-wide `/scheduled_events` needs an owner or admin token, per the [OpenAPI spec](https://developer.calendly.com/openapi/calendly-api.yaml). |
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

`teams`, `user_availability_schedules`, and `locations` partition on `organization_memberships` using `user/uri`, issuing one request per organization member; `teams` can emit the same team once for each member who belongs to it. `event_type_memberships` partitions on `event_types` using `uri`. `user_availability_schedules` and `locations` are not paginated according to Calendly's OpenAPI spec, so their requests send only `user` (no `count` or `page_token`). Location records have no `uri`, so the connector adds `user` from the partition and uses `[user, kind]` as the primary key. `organization_invitations` uses the last path segment of `current_organization` as the organization UUID. `webhook_subscriptions` requires both `organization` and `scope=organization`. Keep these streams out of `suggestedStreams`. New stream timestamps declare `format: date-time`; section 4 still governs existing streams.

**Why this matters:** The member- and event-type-based streams fan out into multiple requests and can return repeated teams, while the unpaginated endpoints do not accept count or page-token parameters. Preserve the partition and request shapes, and do not suggest streams that multiply requests or can emit duplicate teams by default.
