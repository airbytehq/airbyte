> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-linear

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Rotating Refresh Tokens

Linear's OAuth implementation rotates refresh tokens on every exchange. Each successful access-token refresh invalidates the old refresh token and returns a replacement. The connector uses `refresh_token_updater` to persist the replacement token back to the connection configuration. The OAuth consent flow also persists the access token and expiry returned by the initial code exchange, so the first sync can use that token without immediately refreshing it.

**Why this matters:** Linear refresh tokens are single-use. An unnecessary first refresh can consume the newly issued refresh token, and the 30-minute replay grace period does not make relying on the old token safe indefinitely. If a refresh succeeds but the replacement token is not persisted, subsequent refreshes will fail and the connection will require re-authentication.

The consent URL pins `actor=app`, which provides a rate-limit uplift but requires a workspace administrator to install the application. With this actor, the connector can see only teams granted by the administrator, rather than everything visible to the installing user's normal permissions. This differs from the API-key path. Do not change `actor=app` in the manifest without maintainer approval.

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

Linear's GraphQL API returns errors in an `errors` array carrying a machine-readable `extensions.code` and a human-readable `extensions.userPresentableMessage`. HTTP status is an unreliable signal on its own — a malformed query returns 500, not 400 — so the ordered `response_filters` under `definitions.base_requester.error_handler` match on `extensions.code` rather than status. See `CONTRIBUTING.md` § Error handling for the code → action → failure-type table.

**Why this matters:** the filter list is ordered and the CDK returns the first match, so the `RATELIMITED` filter must stay first, `GRAPHQL_VALIDATION_FAILED` must stay before the 4b transport-status filters, and the catch-all must stay last. All 16 streams and the `check` operation share this single handler through `$ref: "#/definitions/base_requester"` and no stream overrides it, so any remediation text written into a filter is emitted for every stream. `FORBIDDEN` and `FEATURE_NOT_ACCESSIBLE` are unverified code strings; if Linear's real values differ, the `extensions.type` branch or catch-all handles those errors instead of misclassifying them.
