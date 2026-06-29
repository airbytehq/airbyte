# Contributing to source-monday

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

**Connector type:** Hybrid (manifest.yaml + Python custom components for GraphQL request handling, record extraction, and pagination)

**Analysis status:** Complete. 8 streams analyzed. 1 uses incremental sync. 7 are full-refresh. Monday.com uses a GraphQL API which does not support traditional date-based filtering on most resource queries.

### Incremental Streams

| Stream | Cursor Field | API Filter | Notes |
|--------|-------------|------------|-------|
| activity_logs | created_at_int | `from`/`to` params in GraphQL query | Monday.com activity logs with timestamp filtering |

### Full-Refresh Streams (Not Actionable)

| Stream | Reason | Evidence |
|--------|--------|----------|
| items | GraphQL API; no `updated_since` filter | Monday.com `boards.items_page` query has no date filter; uses cursor-based pagination only |
| boards | GraphQL API; no date filter | Monday.com `boards` query returns all boards; no `updated_since` |
| tags | Small dataset; no date filter | Monday.com `tags` query returns all tags |
| teams | Small dataset; no date filter | Monday.com `teams` query returns all teams |
| updates | GraphQL API; no `updated_since` filter | Monday.com `updates` query has no date-based filtering |
| users | Small dataset; no date filter | Monday.com `users` query returns all users |
| workspaces | Small dataset; no date filter | Monday.com `workspaces` query returns all workspaces |
