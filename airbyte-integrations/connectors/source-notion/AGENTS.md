> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-notion: Unique Behaviors

## 1. Recursive Block Retrieval Up to 30 Levels Deep

The `BlocksRetriever` performs depth-first recursive fetching of Notion blocks. When a block has `has_children: true`, the retriever immediately makes a new API call to fetch that block's children before continuing to the next sibling. This recursion continues up to a maximum depth of 30 levels.

A single page with deeply nested content (e.g., toggles inside toggles inside columns) can trigger dozens of additional API calls as the retriever walks the entire block tree. Each level of nesting adds another round of paginated API requests for that block's children.

**Why this matters:** What looks like a single blocks stream read can fan out into a large number of API calls proportional to the depth and breadth of the block hierarchy. A page with 5 levels of nested blocks and 10 children per level could trigger hundreds of requests from a single parent page slice. The 30-level depth limit exists to prevent infinite recursion but is otherwise not enforced by Notion's API.

## 2. Every 400 and 404 Is Skipped on Pages, Data Sources, Comments and Blocks

`definitions.error_handler` is one `DefaultErrorHandler` shared by `pages`, `data_sources`, `comments` and `blocks`. Its filters, in order:

1. `rate_limited_filter`: 429 is `RATE_LIMITED`, waiting for the `Retry-After` header (`retry_after_backoff`).
2. `bad_request_filter`: `IGNORE` on every 400, for example Notion's "The start_cursor provided is invalid" error.
3. `object_not_found_filter`: `IGNORE` on every 404, for example pages and databases that are not shared with the integration.

Pages and blocks that are not shared with the integration therefore drop out silently instead of failing the sync. The filters match on status code only. Do not add `error_message_contains` to them: `HttpResponseFilter` matches on `http_codes` OR the message, so a message match would also skip a retryable 408, 5xx or 529 that carries the same text, and the sync would complete without those records. Keep the rate-limit filter first so a 429 is never ignored.

`users` has its own `DefaultErrorHandler` and does not skip 400 or 404: it keeps the rate-limit filter and backoff, then fails with a `config_error` when Notion answers `code: restricted_resource` (the integration lacks the "Read user information" capability). All other statuses use the CDK default mapping (5xx and 408 retried, other 4xx fail, unmapped codes such as 409 and 529 retried), with the CDK default of 5 retries. `unit_tests/test_error_handling.py` pins each case.

## 3. `blocks` Filters Incremental Records in `BlocksRetriever`, Not in the Record Selector

The CDK only attaches the client-side incremental filter (`ClientSideIncrementalRecordFilterDecorator`) to a record selector built by `create_simple_retriever`. The `blocks` record selector is nested in a `CustomRetriever`, so on CDK 7.47 that filter is never attached and the manifest's `is_client_side_incremental` does nothing for `blocks`. `BlocksRetriever` therefore does the filtering itself. It drops a block whose `last_edited_time` is earlier than the slice `start_time`, but only when that start comes from state, meaning it is later than the configured or default `start_date` (`DEFAULT_START_DATE_DAYS_AGO` must match the manifest default). First syncs and full refreshes are not filtered, so they still emit every block. The check runs after a block's children have been read, so an edited child of an unchanged parent is still emitted. `unit_tests/mock_server/test_blocks.py` pins this behaviour.

## Incremental Stream Considerations

All streams are defined declaratively in `manifest.yaml`. The only custom Python component is `BlocksRetriever` in `components.py` (recursive block traversal, see above).

`pages`, `data_sources`, `comments`, and `blocks` use client-side incremental sync on `last_edited_time` (`definitions.client_side_incremental_sync`): records are still fetched from the API and filtered locally. `users` is full refresh only.
