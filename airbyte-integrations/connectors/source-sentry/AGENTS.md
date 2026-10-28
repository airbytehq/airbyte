> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-sentry

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Rate limits

Sentry applies a **fixed-window requests-per-second limit** and a **concurrent in-flight request limit** per caller and endpoint ([rate limits](https://docs.sentry.io/api/ratelimits/)). Responses include `X-Sentry-Rate-Limit-Limit`, `X-Sentry-Rate-Limit-Remaining`, `X-Sentry-Rate-Limit-Reset`, `X-Sentry-Rate-Limit-ConcurrentLimit`, and `X-Sentry-Rate-Limit-ConcurrentRemaining`.

The manifest `api_budget` reads **Remaining** and **Reset** (UTC epoch seconds) to pause before hitting 429, treats **429** as a rate-limit hit, and applies a stricter fallback on **`GET …/events/`** (2/s, 60/min) plus **3/s** for other endpoints. `base_requester.error_handler` backs off on **Retry-After** first, then **X-Sentry-Rate-Limit-Reset** (up to ~61 minutes), then a **60s** constant wait. The **events** stream slices time in **7-day** steps to limit request volume on backfills. Lower **`num_workers`** when syncing **`events`** (especially with `full=true`) or when partitions multiply traffic across project slugs.

## Start dates

See also `manifests/sentry.yaml` for the spec text and stream mapping.

- **`event_start_date`** (default `1900-01-01T00:00:00Z`) — **events** stream only; maps to Sentry's [`start`](https://docs.sentry.io/api/events/list-a-projects-error-events/) query parameter. Use UTC without fractional seconds (e.g. `2026-06-01T00:00:00Z`). Legacy configs may still store **`start_date`**; the manifest uses that as a fallback for events when `event_start_date` is unset.
- **`sync_start_date`** (optional; default `1900-01-01T00:00:00Z` when omitted) — **issues**, **projects**, and **releases** incremental lower bound. Does not apply to events.

The events upper bound is always the current time (`end`). Incremental runs still advance from saved state when state is newer than the configured start.

## Incremental Stream Considerations

The Sentry API supports date-based filtering on events and issues endpoints, which the connector already uses for incremental streams. The remaining FR parent stream `project_detail` is a singleton config endpoint that returns a single project object — not suitable for incremental sync.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| events | medium | top-level parent | dateCreated | dateCreated | incremental |  |
| issues | medium | top-level parent | lastSeen | lastSeen | incremental |  |
| project_detail | small | top-level parent | none | none | deferred_no_api_support | Singleton project config endpoint |
| projects | medium | top-level parent | dateCreated | dateCreated | incremental |  |
| all_projects_detail | medium | child of `projects_all` | none | none | full refresh | Parent is a full org project list (no `start_date` record filter) so overwrite/deduped destinations keep every project detail row each sync. |
| releases | medium | top-level parent | dateCreated | dateCreated | incremental |  |

### Future incremental stream candidates

- **No API date filter (1 streams):** `project_detail` — these streams do not have a documented date-based filter on their list endpoints. A future agent should verify via live API probing whether undocumented filter parameters are accepted.
