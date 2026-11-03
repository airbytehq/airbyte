# source-calendly: Unique Connector Behaviors

## 1. Authentication Failures Stop the Sync, but Deleted Parent Events Do Not

Calendly personal access tokens created since March 2026 require explicit [authorization scopes](https://developer.calendly.com/docs/authentication/scopes). Keep one `DefaultErrorHandler` per requester and no `CompositeErrorHandler`: the shared handler classifies errors consistently, while the invitee requester overrides only the missing-parent case. Authentication messages tell the user how to fix the token and end with Calendly's response `message`.

| HTTP status | Base requester action / failure type | Invitee requester action / failure type | Meaning and response |
| --- | --- | --- | --- |
| 401 | `FAIL` / `config_error` | Same | Invalid or revoked token; create a new token (Profile menu, Developer, Personal access tokens, per [Calendly](https://developer.calendly.com/docs/authentication/how-to-authenticate-with-personal-access-tokens)) and update the source. |
| 403 | `FAIL` / `config_error` | Same | `Insufficient scope` (the body lists `required_scopes`, appended to the message) or `Permission Denied`: organization-wide `/scheduled_events` needs an owner or admin token, per the [OpenAPI spec](https://developer.calendly.com/openapi/calendly-api.yaml). |
| 404 | `FAIL` / `system_error`, message names the URL | `IGNORE`, logged with the URL | A parent event can disappear between listing scheduled events and reading its invitees; skip that parent's invitees and continue. |
| 429 | `RATE_LIMITED` / `transient_error` (CDK default, no filter) | Same | Retry after the `X-RateLimit-Reset` delay; see [Calendly rate limits](https://developer.calendly.com/api-docs/overview/rate-limits). |
| 500, 502, 503, 504 | `RETRY` / `transient_error` | Same | Temporary Calendly server failure. |

**Why this matters:** Retrying invalid credentials hides an actionable configuration problem. Conversely, failing an invitee sync for a deleted parent prevents other events from syncing. Do not broaden the 404 ignore rule to the shared requester or change authentication failures into retries.

## 2. Rate-Limit Reset Headers Are Durations, Not Epoch Timestamps

Calendly documents [per-user rate limits](https://developer.calendly.com/api-docs/overview/rate-limits) of 500 requests/minute on paid plans and 50 requests/minute on free plans. The connector uses one 500/minute `MovingWindowCallRatePolicy` matching `https://api.calendly.com`, and updates it from `X-RateLimit-Remaining`. This lets paid plans use their allowance while a free plan waits when its remaining count reaches zero after its 50 requests; the configured ceiling is not a promise of 500 requests for every account. Concurrency is a fixed 4 worker threads.

Do not set the API budget's `ratelimit_reset_header` to `X-RateLimit-Reset`. CDK 7.45.0 parses that budget header as an epoch timestamp, but Calendly sends seconds until reset, typically 60. Leave the budget's default `ratelimit-reset` header unchanged: Calendly does not send it, so the moving-window policy applies the remaining count instead of skipping that update when a reset timestamp is present. A zero remaining count fills the window and blocks the next request until capacity is available.

Each requester's `WaitTimeFromHeader` reads `X-RateLimit-Reset`, which Calendly sends on every response, as seconds to wait before retrying a 429 or a 500, 502, 503 or 504. CDK adds one second, so a value of 60 normally produces a 61-second retry delay; a 5xx without the header backs off 1, 2, 4, 8 and 16 seconds.

**Why this matters:** Reusing the same reset header for the budget and retry handler looks natural but gives it two incompatible interpretations and prevents remaining-count updates. A fixed 50/minute ceiling unnecessarily throttles paid accounts; removing remaining-header handling risks repeated 429s on free accounts.

## 3. Scheduled Events Use `updated_at`; Invitees Follow Changed Events

`scheduled_events` uses `updated_at` as a client-side incremental cursor. Every request still sends `min_start_time` from the configured `start_date` and sorts by `start_time:desc`; it does not derive the request boundary from state. This lets Calendly return upcoming events while the client emits records whose update time is at or after the saved cursor minus `lookback_days` and a fixed five-minute buffer. Upcoming event start times therefore cannot move the update cursor into the future and suppress later bookings, cancellations, or reschedules.

`lookback_days` is optional with default 0. Keep `lookback_window: "P{{ [config.get('lookback_days') or 0, 0] | max }}DT5M"`: the template clamps negative values to zero, handles a missing key, and adds five minutes for updates made during a scan. Since every request scans from `start_date`, a zero-day lookback is sufficient for normal incremental syncs.

`event_invitees` remains a child stream with `incremental_dependency: true` on `scheduled_events`. Its `created_at` cursor is only a state vehicle: the child has no `start_time_option` or client-side incremental flag and must not filter invitees by `created_at`. The invitee endpoint has no date filter, so each invitee of a new or changed parent event is read, including invitees booked before `start_date`. The parent stream's changed-event filter limits which invitee endpoints are called. State changed in 1.0.0, so incremental connections must clear both streams when upgrading.

`event_types` is a data feed sorted by `updated_at` descending, so pagination stops at the first record older than the cursor start. Its start is `1970-01-01`: a later floor (it was `2021-01-01`) silently drops every event type not updated since.

**Why this matters:** Keeping the request boundary at the configured start date prevents a future event from stalling later updates, while the cursor avoids re-emitting unchanged events. The child cursor must remain state-only so older invitees are not filtered out when their parent changes.

## 4. Existing Datetime and Position Fields Carry Documented Types

Since 1.0.0, existing datetime fields on all streams declare `format: date-time`; integer-valued positions in `event_types` and `event_invitees` declare `integer`, and `event_types.duration_options` items are integers. The retyped paths are enumerated in the schema tests and migration guide. Adding or changing a format or type on any other existing field can retype a destination column and requires a breaking release with migration guidance.

**Why this matters:** Typed destinations can reject or null values after a column type change. Keep the schema tests' exact retyped-field list in sync with the manifest, and do not make further existing-field retypes in a non-breaking release.

## 5. Connection Check Tests Only Current-User Access

The connection check reads `api_user` through `GET /users/me`, which requires `users:read` according to Calendly's [scope reference](https://developer.calendly.com/docs/authentication/scopes). It does not list event types or scheduled events and does not prove that the token has every scope needed by all selected streams, or that its owner is an organization owner or admin. Organization-scoped reads also obtain the current organization from this user response.

**Why this matters:** Switching the check back to a list stream creates unnecessary access requirements during setup. A successful check must not be presented as validation of all read scopes; missing stream-specific scopes still fail with an actionable 403 during a sync.
