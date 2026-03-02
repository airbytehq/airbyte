# source-monday: Unique Behaviors

## 1. GraphQL API with Schema-Driven Query Building

Unlike REST-based connectors, source-monday uses a single GraphQL endpoint for all streams. The `MondayGraphqlRequester` dynamically builds GraphQL queries at runtime by traversing the stream's JSON schema to determine which fields to request. The query structure varies significantly by stream:

- **items:** Must be queried through `boards` (Monday.com removed direct item queries in October 2022). The connector wraps item queries inside a `boards` query.
- **activity_logs:** Also wrapped inside a `boards` query with timestamp filtering via a `from` parameter.
- **column_values:** Requires GraphQL inline fragments (`... on MirrorValue`, `... on BoardRelationValue`, `... on DependencyValue`) because Monday.com uses union types for the `display_value` field.

**Why this matters:** Modifying a stream's JSON schema directly affects the GraphQL query that gets sent to the API. Adding or removing fields from the schema will change the query structure. The stream-specific query builders (`_build_items_query`, `_build_activity_query`, `_build_teams_query`) each have different logic, so changes to one stream's query pattern do not apply to others.

## 2. Two-Level Nested Pagination for Items

The items stream uses a two-level pagination strategy where boards are paginated on the outer level and items within each board are paginated on the inner level. The `ItemPaginationStrategy` tracks both a `_page` (board page number) and a `_sub_page` (item cursor within a board). When items within a board are exhausted, the strategy advances to the next board page and resets the item cursor. A separate `ItemCursorPaginationStrategy` handles cursor-based pagination for the newer `items_page`/`next_items_page` API.

**Why this matters:** A single items sync involves nested iteration that is not visible from the manifest. If pagination breaks, you need to determine whether the failure is at the board level or the item level within a board. The connector also maintains two different pagination strategies for items depending on whether it uses page-based or cursor-based pagination.
