> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-notion: Unique Behaviors

## 1. Recursive Block Retrieval Up to 30 Levels Deep

The `BlocksRetriever` performs depth-first recursive fetching of Notion blocks. When a block has `has_children: true`, the retriever immediately makes a new API call to fetch that block's children before continuing to the next sibling. This recursion continues up to a maximum depth of 30 levels.

A single page with deeply nested content (e.g., toggles inside toggles inside columns) can trigger dozens of additional API calls as the retriever walks the entire block tree. Each level of nesting adds another round of paginated API requests for that block's children.

**Why this matters:** What looks like a single blocks stream read can fan out into a large number of API calls proportional to the depth and breadth of the block hierarchy. A page with 5 levels of nested blocks and 10 children per level could trigger hundreds of requests from a single parent page slice. The 30-level depth limit exists to prevent infinite recursion but is otherwise not enforced by Notion's API.

## 2. Every 400 and 404 Is Skipped on Pages, Data Sources, Comments and Blocks

`definitions.error_handler` is one `DefaultErrorHandler` shared by `pages`, `data_sources`, `comments` and `blocks`. Its filters, in order:

1. `rate_limited_filter`: 429 is `RATE_LIMITED`, waiting for the `Retry-After` header (`retry_after_backoff`).
2. `invalid_start_cursor_filter`: `IGNORE` on 400.
3. `not_shared_with_integration_filter`: `IGNORE` on 404.

`HttpResponseFilter` matches on `http_codes` OR `error_message_contains`, so filters 2 and 3 skip every 400 and every 404, whatever the message, plus any other non-2xx whose `message` contains the Notion text (for example a 403 or 5xx carrying the sharing hint). Pages and blocks that are not shared with the integration therefore drop out silently instead of failing the sync. Keep the rate-limit filter first so a 429 is never ignored.

`users` has its own `DefaultErrorHandler` and does not skip 400 or 404: it keeps the rate-limit filter and backoff, then fails with a `config_error` when Notion answers `code: restricted_resource` (the integration lacks the "Read user information" capability). All other statuses use the CDK default mapping (5xx and 408 retried, other 4xx fail, unmapped codes such as 409 and 529 retried), with the CDK default of 5 retries. `unit_tests/test_error_handling.py` pins each case.

## Incremental Stream Considerations

All streams are defined declaratively in `manifest.yaml`. The only custom Python component is `BlocksRetriever` in `components.py` (recursive block traversal, see above).

`pages`, `data_sources`, `comments`, and `blocks` use client-side incremental sync on `last_edited_time` (`definitions.client_side_incremental_sync`): records are still fetched from the API and filtered locally. `users` is full refresh only.
