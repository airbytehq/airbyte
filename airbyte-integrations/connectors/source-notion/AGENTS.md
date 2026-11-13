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

## Incremental Stream Considerations

All streams are defined declaratively in `manifest.yaml`. The only custom Python component is `BlocksRetriever` in `components.py` (recursive block traversal, see above).

`pages`, `data_sources`, `comments`, and `blocks` use client-side incremental sync on `last_edited_time` (`definitions.client_side_incremental_sync`): records are still fetched from the API and filtered locally. `users` is full refresh only.

`blocks` is the exception to where that filtering happens. Its manifest sets `is_client_side_incremental: false` and `BlocksRetriever` drops blocks whose `last_edited_time` is before the slice's `start_time` itself, after it has fetched their children. Two reasons:

1. A block's `last_edited_time` is not guaranteed to move when a nested child is edited, so filtering in the record selector (before the recursion) would also skip the recently edited children of an unchanged parent block.
2. In newer CDK versions (confirmed on 7.47.0; 7.1.0 still filtered) the factory no longer hands the client-side cursor to a `CustomRetriever`'s record selector, so `is_client_side_incremental: true` silently stopped filtering and every block was emitted on every sync. `unit_tests/mock_server/test_blocks.py` pins the behavior.
