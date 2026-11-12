# source-notion: Unique Behaviors

## 1. Recursive Block Retrieval Up to 30 Levels Deep

The `BlocksRetriever` performs depth-first recursive fetching of Notion blocks. When a block has `has_children: true`, the retriever immediately makes a new API call to fetch that block's children before continuing to the next sibling. This recursion continues up to a maximum depth of 30 levels.

Incremental reads still visit unchanged ancestor blocks to find updated descendants, but only emit blocks within the cursor bounds. See [AGENTS.md](./AGENTS.md) for the traversal and filtering details.

## 2. Every 400 and 404 Is Skipped on Pages, Data Sources, Comments and Blocks

These streams share one error handler that skips every 400 (the invalid `start_cursor` case) and every 404 (objects not shared with the integration), regardless of the message, and treats 429 as rate limited using the `Retry-After` header. The `users` stream does not skip them; it fails with a configuration error when the integration lacks the "Read user information" capability. See `AGENTS.md` for the filter order and its limits.

## Incremental Stream Considerations

All streams are defined in the declarative manifest. `pages`, `data_sources`, `comments`, and `blocks` use client-side filtering on `last_edited_time`; `users` supports full refresh only. Notion's block-children endpoint provides pagination but no date filter, so incremental reads still fetch the block tree. The saved cursor boundary and the CDK's runtime lookback may repeat some records intentionally.
