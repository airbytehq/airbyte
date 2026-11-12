# source-notion: Unique Behaviors

## 1. Recursive Block Retrieval Up to 30 Levels Deep

Block retrieval walks nested content up to 30 levels deep, including unchanged parents so updated children are still found. Incremental syncs therefore still fetch the block tree even when few blocks are emitted; see [AGENTS.md](./AGENTS.md) for details.

## 2. Every 400 and 404 Is Skipped on Pages, Data Sources, Comments and Blocks

These streams share one error handler that skips every 400 (the invalid `start_cursor` case) and every 404 (objects not shared with the integration), regardless of the message, and treats 429 as rate limited using the `Retry-After` header. The `users` stream does not skip them; it fails with a configuration error when the integration lacks the "Read user information" capability. See `AGENTS.md` for the filter order and its limits.

## Incremental Stream Considerations

`pages`, `data_sources`, `comments`, and `blocks` use client-side incremental sync on `last_edited_time`; `users` is full refresh only. Records at the saved cursor boundary can repeat. Streams are defined in `manifest.yaml`, with a custom Python retriever for recursive block traversal.
