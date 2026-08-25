# Contributing to source-linear

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Rate-Limit Budget

The connector uses an `HttpAPIBudget` to proactively pace requests against Linear's documented request ceilings: 2,500 requests per hour for API-key authentication and 5,000 requests per hour for OAuth authentication. Workspace OAuth applications can receive dynamically increased limits based on the number of paid seats.

The budget uses 10-second, 1-minute, and hourly `MovingWindowCallRatePolicy` rates instead of one hourly rate. Because the policy uses a moving window, a single hourly rate would allow the whole quota to be spent in a burst and then block until the window slid. The 1-minute rate averages requests below the documented hourly ceiling, the 10-second rate caps bursts across concurrent workers, and the hourly rate enforces the documented ceiling.

`ratelimit_reset_header` is deliberately left unset. Linear sends `X-RateLimit-*-Reset` values as epoch milliseconds, while `HttpAPIBudget.get_reset_ts_from_response` passes the value to `datetime.fromtimestamp`, which expects seconds and raises on a 13-digit value. `MovingWindowCallRatePolicy.update` ignores a reset timestamp anyway, and supplying one suppresses the bucket-fill behavior used when no calls remain. The existing `WaitUntilTimeFromHeader` strategies already handle Linear's reset header with the `regex` `^\d{10}`.

The reactive `DefaultErrorHandler` remains the safety net because the budget cannot see quota consumed elsewhere or model Linear's complexity and per-endpoint quotas.

## Incremental Stream Considerations

The Linear GraphQL API supports `updatedAt` filtering via `filter: { updatedAt: { gte: ... } }` on most entity types, which the connector uses extensively — 12 streams are already incremental (added in PR airbytehq/airbyte#76429). The remaining 4 FR parent streams are config-style lookups (`customer_statuses`, `customer_tiers`, `project_statuses`) and `issue_relations` which lacks a documented `updatedAt` filter in the GraphQL schema.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| attachments | medium | top-level parent | updatedAt | updated_at | incremental | `filter.updatedAt.gte` via `incremental_sync_updated_at` |
| comments | medium | top-level parent | updatedAt | updated_at | incremental | `filter.updatedAt.gte` via `incremental_sync_updated_at` |
| customer_needs | medium | top-level parent | updatedAt | updated_at | incremental | `filter.updatedAt.gte` via `incremental_sync_updated_at` |
| customer_statuses | small | top-level parent | none | none | deferred_no_api_support | Config-style enum lookup; no `updatedAt` filter |
| customer_tiers | small | top-level parent | none | none | deferred_no_api_support | Config-style enum lookup; no `updatedAt` filter |
| customers | medium | top-level parent | updatedAt | updated_at | incremental | `filter.updatedAt.gte` via `incremental_sync_updated_at` |
| cycles | medium | top-level parent | updatedAt | updated_at | incremental | `filter.updatedAt.gte` via `incremental_sync_updated_at` |
| issue_labels | medium | top-level parent | updatedAt | updated_at | incremental | `filter.updatedAt.gte` via `incremental_sync_updated_at` |
| issue_relations | medium | top-level parent | none | none | deferred_no_api_support | No documented `updatedAt` filter in GraphQL schema. Verify via introspection. |
| issues | medium | top-level parent | updatedAt | updated_at | incremental | `filter.updatedAt.gte` via `incremental_sync_updated_at` |
| project_milestones | medium | top-level parent | updatedAt | updated_at | incremental | `filter.updatedAt.gte` via `incremental_sync_updated_at` |
| project_statuses | small | top-level parent | none | none | deferred_no_api_support | Config-style enum lookup; no `updatedAt` filter |
| projects | medium | top-level parent | updatedAt | updated_at | incremental | `filter.updatedAt.gte` via `incremental_sync_updated_at` |
| teams | medium | top-level parent | updatedAt | updated_at | incremental | `filter.updatedAt.gte` via `incremental_sync_updated_at` |
| users | medium | top-level parent | updatedAt | updated_at | incremental | `filter.updatedAt.gte` via `incremental_sync_updated_at` |
| workflow_states | medium | top-level parent | updatedAt | updated_at | incremental | `filter.updatedAt.gte` via `incremental_sync_updated_at` |

### Future incremental stream candidates

- **No API date filter (4 streams):** `customer_statuses`, `customer_tiers`, `issue_relations`, `project_statuses` — these endpoints do not expose date-based filtering. A future agent should verify via live API probing whether undocumented filter parameters are accepted.

## Error handling

Linear's GraphQL API returns errors in an `errors` array with a machine-readable
`extensions.code` and a human-readable `extensions.userPresentableMessage`. HTTP status
is an unreliable signal on its own — a malformed query returns 500, not 400 — so the
response filters in `definitions.base_requester.error_handler` match on `extensions.code`.

| `extensions.code` | HTTP | Action | Failure type |
|---|---|---|---|
| `RATELIMITED` | 429 | RATE_LIMITED | transient_error |
| `AUTHENTICATION_ERROR` | 401 | FAIL | config_error |
| `FORBIDDEN`, `FEATURE_NOT_ACCESSIBLE` | 400/403 | FAIL | config_error |
| `GRAPHQL_VALIDATION_FAILED` | 400 or 500 | FAIL | system_error |
| anything else with an `errors` array | any | FAIL | system_error |

Order matters — the CDK applies the first matching filter. The catch-all must stay last;
it exists because GraphQL can return HTTP 200 with a populated `errors` array, which would
otherwise be extracted as zero records and reported as a successful empty stream.
