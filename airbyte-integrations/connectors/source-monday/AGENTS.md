> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

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

## 3. Cursor Expiration After 60 Minutes (CursorExpiredError)

Monday.com's `items_page`/`next_items_page` pagination cursors expire after 60 minutes. If the connector takes longer than an hour to process records within a single paginated sequence (e.g., due to rate limiting, large boards, or slow downstream processing), the API returns a `CursorExpiredError` with a 200 status code:

```json
{
  "error_code": "CursorException",
  "status_code": 200,
  "error_message": "CursorExpiredError: The cursor provided for pagination has expired. Please refresh your query and obtain a new cursor to continue fetching items"
}
```

The connector handles this by triggering `RESET_PAGINATION`, which restarts pagination from the beginning of the current stream. This means all records fetched before the expiration are re-read. See [Monday.com community discussion](https://developer-community.monday.com/api-apps-framework-4/cursor-used-for-pagination-expires-alternate-way-to-paginate-4083) for API context.

Two API facts make this unavoidable rather than a bug that can be fixed locally: cursors are generated on the first request for a board and are cached for 60 minutes ([Monday `items_page` cursor docs](https://developer.monday.com/api-reference/reference/items-page#cursor-based-pagination-using-next_items_page)), and the API does **not** guarantee a stable item order. Because items are unordered, the connector cannot checkpoint partial progress within a board and resume — it can only restart from the beginning (the code resets pagination on `CursorExpiredError`; see the `RESET_PAGINATION` predicate in `manifest.yaml`).

**Why this matters:** For large boards, cursor expiration can cause repeated full re-reads if processing consistently takes longer than an hour. Each reset restarts from page 1, so syncs may never complete for very large boards if the processing time per page exceeds the cursor TTL. Historically this problem was *first misdiagnosed* as a `ComplexityException` (`status_code: 429`) before it was traced to the expiring cursor, so a `429` on the items stream may be correlated with cursor expiration — but the connector only explicitly resets on `CursorExpiredError`, so check for that error code when diagnosing.

## Incremental Stream Considerations

The Monday.com GraphQL API supports filtering by `updated_at` on boards and items. The connector uses Python custom components referenced from the manifest.

**Connector type:** Python custom components (hybrid manifest + Python)

**Analysis status:** Streams are Python-defined via custom components. Full stream-by-stream analysis requires Python code review.

### `updates` incremental sync

`updates` is a plain incremental stream on `created_at`. `MondayGraphqlRequester._build_updates_query` turns the `DatetimeBasedCursor` slice into the root-level `from_date`/`to_date` arguments; `DatetimeBasedCursor` request options can't express them because the request body is a GraphQL string assembled in Python.

- `from_date` and `to_date` are inclusive, minute-granular (`%Y-%m-%dT%H:%M`), and must be sent together. They only work on the root `updates` query, not on updates nested under `boards`.
- A slice that starts at the `start_datetime` epoch (`1970-01-01T00:00:00Z`, meaning no state yet) sends no filter, so full refresh and first incremental syncs read every update. There is no `start_date` in the spec and no `step`, so each sync is a single slice from the saved state to now.
- The filter is on creation date only. `updated_at`/`edited_at` can't be filtered, so edits to an update and new replies on an update are only picked up while the parent update was created within the `lookback_window` (`P1D`). Older edits and replies need a full refresh.
- `items_per_page: 100` must stay on the stream. Without it no `limit` is sent, monday returns its default of 25 and `PageIncrement` (page size 100) stops after the first page.

### Future incremental stream candidates

- **All streams deferred for Python code review:** This connector defines its streams in Python code rather than declarative manifest YAML. A full stream-by-stream incremental analysis table (per the standard CONTRIBUTING.md schema) should be added by a future agent after reviewing the Python stream definitions, their `cursor_field` properties, and the API endpoints they call.
