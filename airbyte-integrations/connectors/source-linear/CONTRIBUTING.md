# Contributing to source-linear

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Rate-Limit Budget

The connector uses an `HttpAPIBudget` to proactively pace requests against Linear's documented request ceilings: 2,500 requests per hour for API-key authentication and 5,000 requests per hour for OAuth authentication. Workspace OAuth applications can receive dynamically increased limits based on the number of paid seats.

The budget uses 10-second, 1-minute, and hourly `MovingWindowCallRatePolicy` rates instead of one hourly rate. Because the policy uses a moving window, a single hourly rate would allow the whole quota to be spent in a burst and then block until the window slid. The 1-minute rate averages requests below the documented hourly ceiling, the 10-second rate caps bursts across concurrent workers, and the hourly rate enforces the documented ceiling.

`ratelimit_reset_header` is deliberately left unset. Linear sends `X-RateLimit-*-Reset` values as epoch milliseconds, while `HttpAPIBudget.get_reset_ts_from_response` passes the value to `datetime.fromtimestamp`, which expects seconds and raises on a 13-digit value. `MovingWindowCallRatePolicy.update` ignores a reset timestamp anyway, and supplying one suppresses the bucket-fill behavior used when no calls remain. The existing `WaitUntilTimeFromHeader` strategies already handle Linear's reset header with the `regex` `^\d{10}`.

The reactive `DefaultErrorHandler` remains the safety net because the budget cannot see quota consumed elsewhere or model Linear's complexity and per-endpoint quotas.

## Incremental Stream Considerations

The Linear GraphQL API supports `updatedAt` filtering via `filter: { updatedAt: { gte: ... } }` on most entity types, which the connector uses extensively — 14 of the 20 streams are incremental (12 from PR airbytehq/airbyte#76429; `initiatives` and `project_updates` from PR airbytehq/airbyte#85056). The remaining 6 are the config-style lookups (`customer_statuses`, `customer_tiers`, `project_statuses`), `issue_relations` and `initiative_to_projects` which expose no `updatedAt` filter, and the `issue_history` substream child.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| attachments | medium | top-level parent | updatedAt | updated_at | incremental | `filter.updatedAt.gte` via `incremental_sync_updated_at` |
| comments | medium | top-level parent | updatedAt | updated_at | incremental | `filter.updatedAt.gte` via `incremental_sync_updated_at` |
| customer_needs | medium | top-level parent | updatedAt | updated_at | incremental | `filter.updatedAt.gte` via `incremental_sync_updated_at` |
| customer_statuses | small | top-level parent | none | none | deferred_no_api_support | Config-style enum lookup; no `updatedAt` filter |
| customer_tiers | small | top-level parent | none | none | deferred_no_api_support | Config-style enum lookup; no `updatedAt` filter |
| customers | medium | top-level parent | updatedAt | updated_at | incremental | `filter.updatedAt.gte` via `incremental_sync_updated_at` |
| cycles | medium | top-level parent | updatedAt | updated_at | incremental | `filter.updatedAt.gte` via `incremental_sync_updated_at` |
| initiatives | medium | top-level parent | updatedAt | updated_at | incremental | `filter.updatedAt.gte` via `incremental_sync_updated_at` |
| initiative_to_projects | medium | top-level parent | none | none | deferred_no_api_support | `initiativeToProjects` rejects a `filter` argument; full refresh |
| issue_history | medium | substream child | none | none | full_refresh_child | Parent `issues`; full parent read on each sync |
| issue_labels | medium | top-level parent | updatedAt | updated_at | incremental | `filter.updatedAt.gte` via `incremental_sync_updated_at` |
| issue_relations | medium | top-level parent | none | none | deferred_no_api_support | No documented `updatedAt` filter in GraphQL schema. Verify via introspection. |
| issues | medium | top-level parent | updatedAt | updated_at | incremental | `filter.updatedAt.gte` via `incremental_sync_updated_at` |
| project_milestones | medium | top-level parent | updatedAt | updated_at | incremental | `filter.updatedAt.gte` via `incremental_sync_updated_at` |
| project_statuses | small | top-level parent | none | none | deferred_no_api_support | Config-style enum lookup; no `updatedAt` filter |
| projects | medium | top-level parent | updatedAt | updated_at | incremental | `filter.updatedAt.gte` via `incremental_sync_updated_at` |
| project_updates | medium | top-level parent | updatedAt | updated_at | incremental | `filter.updatedAt.gte` via `incremental_sync_updated_at` |
| teams | medium | top-level parent | updatedAt | updated_at | incremental | `filter.updatedAt.gte` via `incremental_sync_updated_at` |
| users | medium | top-level parent | updatedAt | updated_at | incremental | `filter.updatedAt.gte` via `incremental_sync_updated_at` |
| workflow_states | medium | top-level parent | updatedAt | updated_at | incremental | `filter.updatedAt.gte` via `incremental_sync_updated_at` |

### Future incremental stream candidates

- **No API date filter (5 streams):** `customer_statuses`, `customer_tiers`, `initiative_to_projects`, `issue_relations`, `project_statuses` — these endpoints do not expose date-based filtering. Verified via live API probing on 2026-08-28: each of the five queries rejects a `filter` argument with `GRAPHQL_VALIDATION_FAILED` (`Unknown argument "filter" on field "Query.<name>"`), while the `issues` control query accepts `filter` and fails only on authentication.

## Deletions

Linear soft-deletes records by archiving them. The API provides no hard-delete signal or deleted-records endpoint, so the connector uses `archivedAt` on the primary stream as its single canonical deletion flag. Every query must pass `includeArchived: true`; without it, Linear omits archived records entirely and `archivedAt` is always null. Linear can also permanently hard-delete records, which leaves no signal for the connector to detect.

## Error handling

Linear's GraphQL API returns errors in an `errors` array with a machine-readable
`extensions.code` and a human-readable `extensions.userPresentableMessage`. HTTP status
is an unreliable signal on its own — a malformed query returns 500, not 400 — so the
response filters in `definitions.base_requester.error_handler` match on `extensions.code`.

| `extensions.code` | HTTP | Action | Failure type |
|---|---|---|---|
| `RATELIMITED` | 400 (Linear's documented GraphQL status; 429 can appear at the edge) | RATE_LIMITED | resolved from the HTTP status, not from the manifest — see note |
| `AUTHENTICATION_ERROR` | 401 | FAIL | config_error |
| `FORBIDDEN`, `FEATURE_NOT_ACCESSIBLE` (or `extensions.type` `forbidden`, `feature not accessible`) | 400/403 | FAIL | config_error |
| `GRAPHQL_VALIDATION_FAILED` | 400 or 500 | FAIL | system_error |
| anything else with an `errors` array | any | FAIL | system_error |

The explicit HTTP 429 and 408/500/502/503/504 status filters preserve rate limiting and
transport retries before the catch-all is considered.

A filter's declared `failure_type` is honored only when its action is `FAIL`
(`HttpResponseFilter.matches`); for `RATE_LIMITED` the CDK takes the failure type from
`DEFAULT_ERROR_MAPPING[status]`. So filter 1's `failure_type: transient_error` is inert:
the rate-limit filter resolves to `system_error` at Linear's HTTP 400 and to
`transient_error` only at 429. Do not add `http_codes` guards from this table without
re-probing Linear — the status column records observed statuses, not a contract.

Order matters — the CDK applies the first matching filter. The catch-all must stay last.
Its predicate tests that `errors` is populated and no top-level `data` value is usable, so
partial-success pages flow to the extractor. The explicit status filters above it classify
408, 429 and 5xx responses before the catch-all, preserving retry and rate-limit behavior.
