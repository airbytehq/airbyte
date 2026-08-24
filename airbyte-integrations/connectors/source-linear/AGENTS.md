> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-linear

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Rotating Refresh Tokens

Linear's OAuth token endpoint returns a new refresh token alongside each new access token. The connector uses `refresh_token_updater` to persist that replacement back to the connection configuration. The OAuth consent flow also persists the access token and expiry returned by the initial code exchange, so the first sync uses that token instead of refreshing immediately.

**Why this matters:** Refreshing is replay-safe for a limited window — repeated exchanges with the same stored refresh token return the same successor token, and the stored token keeps working. Linear documents a 30-minute grace period for retrying a refresh whose response was lost, which is consistent with the three consecutive successful exchanges a maintainer observed with a single stored token in airbytehq/airbyte#84947. Outside that window the successor is the only valid token, so a connection that never persists the replacement breaks permanently and requires re-authentication. Note that re-authorizing (a new consent grant) does invalidate previously issued refresh tokens — that, not refreshing, is the destructive operation.

**Acceptance testing note:** Do not seed `credentials.access_token` or `credentials.token_expiry_date` into the `config_oauth.json` acceptance secret. The CDK short-circuits the token request when the stored token has not expired, so a seeded unexpired token makes the acceptance run skip `https://api.linear.app/oauth/token` entirely and never exercise `refresh_token_updater`. Store only `client_id`, `client_secret` and `refresh_token` there.

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
