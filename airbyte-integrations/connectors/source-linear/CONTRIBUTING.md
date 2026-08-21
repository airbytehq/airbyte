# Contributing to source-linear

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

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
