# source-notion: Unique Behaviors

## 1. Recursive Block Retrieval Up to 30 Levels Deep

The `BlocksRetriever` performs depth-first recursive fetching of Notion blocks. When a block has `has_children: true`, the retriever immediately makes a new API call to fetch that block's children before continuing to the next sibling. This recursion continues up to a maximum depth of 30 levels.

A single page with deeply nested content (e.g., toggles inside toggles inside columns) can trigger dozens of additional API calls as the retriever walks the entire block tree. Each level of nesting adds another round of paginated API requests for that block's children.

Incremental syncs still fetch children of unchanged blocks so they can find changed descendants, but only emit blocks within the cursor window. Records exactly at the saved timestamp can repeat; see [AGENTS.md](./AGENTS.md) for the filtering order.

**Why this matters:** What looks like a single blocks stream read can fan out into a large number of API calls proportional to the depth and breadth of the block hierarchy. A page with 5 levels of nested blocks and 10 children per level could trigger hundreds of requests from a single parent page slice. The 30-level depth limit exists to prevent infinite recursion but is otherwise not enforced by Notion's API.

## 2. Every 400 and 404 Is Skipped on Pages, Data Sources, Comments and Blocks

These streams share one error handler that skips every 400 (the invalid `start_cursor` case) and every 404 (objects not shared with the integration), regardless of the message, and treats 429 as rate limited using the `Retry-After` header. The `users` stream does not skip them; it fails with a configuration error when the integration lacks the "Read user information" capability. See `AGENTS.md` for the filter order and its limits.

## Incremental Stream Considerations

`pages`, `data_sources`, `comments`, and `blocks` use client-side incremental sync on `last_edited_time`: records are fetched from the API and filtered locally. `users` supports full refresh only. Stream definitions are declarative, with a custom retriever for recursive block traversal.
