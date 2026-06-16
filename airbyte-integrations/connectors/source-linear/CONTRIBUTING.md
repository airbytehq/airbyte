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
