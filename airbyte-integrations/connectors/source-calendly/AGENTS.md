# source-calendly: Unique Connector Behaviors

## 1. Authentication Failures Stop the Sync, but Deleted Parent Events Do Not

Calendly personal access tokens created since March 2026 require explicit [authorization scopes](https://developer.calendly.com/docs/authentication/scopes). Keep one `DefaultErrorHandler` per requester and no `CompositeErrorHandler`: the shared handler classifies errors consistently, while the invitee requester overrides only the missing-parent case. Authentication messages include Calendly's response `message` and tell the user how to fix the token.

| HTTP status | Base requester action / failure type | Invitee requester action / failure type | Meaning and response |
| --- | --- | --- | --- |
| 401 | `FAIL` / `config_error` | Same | Invalid or revoked token; create a new personal access token under Integrations → API & Webhooks and update Airbyte. |
| 403 | `FAIL` / `config_error` | Same | Missing scope; grant `users:read`, `event_types:read`, `groups:read`, `organizations:read`, and `scheduled_events:read`. |
| 404 | `FAIL` / `system_error` | `IGNORE` / `system_error` | A parent event can disappear between listing scheduled events and reading its invitees; skip that parent's invitees and continue. |
| 429 | `RATE_LIMITED` / `transient_error` | Same | Retry after the reset-header delay; see [Calendly rate limits](https://developer.calendly.com/api-docs/overview/rate-limits). |
| 500, 502, 503, 504 | `RETRY` / `transient_error` | Same | Temporary Calendly server failure. |

**Why this matters:** Retrying invalid credentials hides an actionable configuration problem. Conversely, failing an invitee sync for a deleted parent prevents other events from syncing. Do not broaden the 404 ignore rule to the shared requester or change authentication failures into retries.

## 2. Rate-Limit Reset Headers Are Durations, Not Epoch Timestamps

Calendly documents [per-user rate limits](https://developer.calendly.com/api-docs/overview/rate-limits) of 500 requests/minute on paid plans and 50 requests/minute on free plans. The connector uses one 500/minute `MovingWindowCallRatePolicy` matching `https://api.calendly.com`, and updates it from `X-RateLimit-Remaining`. This lets paid plans use their allowance while a free plan waits when its remaining count reaches zero after its 50 requests; the configured ceiling is not a promise of 500 requests for every account. Concurrency defaults to 4 with a maximum of 10.

Do not set the API budget's `ratelimit_reset_header` to `X-RateLimit-Reset`. CDK 7.45.0 parses that budget header as an epoch timestamp, but Calendly sends seconds until reset, typically 60. Leave the budget's default `ratelimit-reset` header unchanged: Calendly does not send it, so the moving-window policy applies the remaining count instead of skipping that update when a reset timestamp is present. A zero remaining count fills the window and blocks the next request until capacity is available.

For HTTP 429, each requester's `WaitTimeFromHeader` reads `X-RateLimit-Reset` as seconds to wait. CDK adds one second to the returned backoff, so a value of 60 normally produces a 61-second retry delay.

**Why this matters:** Reusing the same reset header for the budget and retry handler looks natural but gives it two incompatible interpretations and prevents remaining-count updates. A fixed 50/minute ceiling unnecessarily throttles paid accounts; removing remaining-header handling risks repeated 429s on free accounts.

## 3. Start-Time Lookback Does Not Track Every Event Update

`scheduled_events` uses `start_time`, not modification time, as its incremental cursor. It sends `min_start_time` from saved state minus `lookback_days`, bounded by the configured start date. `lookback_days` is optional with default 0; keep `lookback_window: "P{{ config.get('lookback_days') or 0 }}D"` so a missing key produces `P0D`. The old `P{{config['lookback_days']}}D` rendered `PD` when the key was missing and caused an `ISO8601Error`. Explicit null is still rejected by the number-valued configuration spec.

`event_invitees` follows the scheduled-event parent through `incremental_dependency: true` and uses a `created_at` data-feed cursor for invitees. Its coverage therefore depends on which parent events are read, rather than independently finding all modified invitees. A redesign of this incremental behavior is tracked separately. Lookback re-reads recent scheduled events to pick up reschedules and cancellations, but changes outside that window can still require a full refresh.

**Why this matters:** Treating either cursor as an update timestamp overstates freshness guarantees. Keep the missing-key-safe template and parent dependency intact unless deliberately redesigning incremental state and validating backward compatibility.

## 4. Existing Datetime Fields Intentionally Remain Strings Without Formats

Adding or changing `format` or `type` on an existing schema field is a breaking change for typed destinations. Existing datetime fields such as `start_time`, `end_time`, `created_at`, and `updated_at` intentionally remain string-valued fields without a datetime `format` for now, even where the [Calendly OpenAPI specification](https://developer.calendly.com/openapi/calendly-api.yaml) documents a timestamp. This includes properties already present inside cancellation objects.

New nullable fields may use documented formats, such as `date-time` inside the newly added `no_show` and `reconfirmation` objects. Do not use those additions as a reason to retype neighboring pre-existing fields. Schema tests preserve the exact type/format definitions of every field from the previous release and explicitly guard existing datetime fields against newly added formats.

**Why this matters:** Adding a format can change a destination column's type even when every API value stays the same. Keep schema expansion separate from breaking retypes and their migration requirements.

## 5. Connection Check Tests Only Current-User Access

The connection check reads `api_user` through `GET /users/me`, which requires `users:read` according to Calendly's [scope reference](https://developer.calendly.com/docs/authentication/scopes). It does not list event types or scheduled events and does not prove that the token has every scope needed by all selected streams. Organization-scoped reads also obtain the current organization from this user response.

**Why this matters:** Switching the check back to a list stream creates unnecessary access requirements during setup. A successful check must not be presented as validation of all read scopes; missing stream-specific scopes still fail with an actionable 403 during a sync.
