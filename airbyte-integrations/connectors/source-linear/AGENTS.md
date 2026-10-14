> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-linear

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Rotating Refresh Tokens

Linear's OAuth implementation rotates refresh tokens on every exchange. Each successful access-token refresh invalidates the old refresh token and returns a replacement. The connector uses `refresh_token_updater` to persist the replacement token back to the connection configuration. The OAuth consent flow also persists the access token and expiry returned by the initial code exchange, so the first sync can use that token without immediately refreshing it.

**Why this matters:** Linear refresh tokens are single-use. An unnecessary first refresh can consume the newly issued refresh token, and the 30-minute replay grace period does not make relying on the old token safe indefinitely. If a refresh succeeds but the replacement token is not persisted, subsequent refreshes will fail and the connection will require re-authentication.

The consent URL pins `actor=app`, which provides a rate-limit uplift but requires a workspace administrator to install the application. With this actor, the connector can see only teams granted by the administrator, rather than everything visible to the installing user's normal permissions. This differs from the API-key path. Do not change `actor=app` in the manifest without maintainer approval.

## Incremental Stream Considerations

The Linear GraphQL API supports `updatedAt` filtering via `filter: { updatedAt: { gte: ... } }` on most entity types, which the connector uses extensively — 14 of the 20 streams are incremental (12 from PR airbytehq/airbyte#76429; `initiatives` and `project_updates` from PR airbytehq/airbyte#85056). The remaining 6 streams are full-refresh or child streams without a usable `updatedAt` filter.

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

`issue_history` is the connector's first substream; each sync performs a full parent `issues` read. `initiativeToProjects` has no `updatedAt` filter.

### Future incremental stream candidates

- **No API date filter (5 streams):** `customer_statuses`, `customer_tiers`, `initiative_to_projects`, `issue_relations`, `project_statuses` — these endpoints do not expose date-based filtering. Verified via live API probing on 2026-08-28: each of the five queries rejects a `filter` argument with `GRAPHQL_VALIDATION_FAILED` (`Unknown argument "filter" on field "Query.<name>"`), while the `issues` control query accepts `filter` and fails only on authentication.

## Deletions

Linear soft-deletes records by archiving them. The API provides no hard-delete signal or deleted-records endpoint, so the connector uses `archivedAt` on the primary stream as its single canonical deletion flag. Every query must pass `includeArchived: true`; without it, Linear omits archived records entirely and `archivedAt` is always null. Linear can also permanently hard-delete records, which leaves no signal for the connector to detect.

## Error handling

Linear's GraphQL API returns errors in an `errors` array carrying a machine-readable `extensions.code` and a human-readable `extensions.userPresentableMessage`. HTTP status is an unreliable signal on its own — a malformed query returns 500, not 400 — so the ordered `response_filters` under `definitions.base_requester.error_handler` match on `extensions.code` rather than status. See `CONTRIBUTING.md` § Error handling for the code → action → failure-type table.

**Why this matters:** the filter list is ordered and the CDK returns the first match, so the `RATELIMITED` filter must stay first, `GRAPHQL_VALIDATION_FAILED` must stay before the 4b transport-status filters, and the catch-all must stay last. All 20 streams and the `check` operation share this single handler through `$ref: "#/definitions/base_requester"` and no stream overrides it, so any remediation text written into a filter is emitted for every stream. `FORBIDDEN` and `FEATURE_NOT_ACCESSIBLE` are unverified code strings; if Linear's real values differ, the `extensions.type` branch or catch-all handles those errors instead of misclassifying them.
