> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-slack: Unique Behaviors

## 1. Auto-Joining Channels During Sync

When `join_channels` is enabled in the config, the `ChannelsRetriever` automatically joins Slack channels by making POST requests to `conversations.join` during the channels stream read. For each non-archived channel where the bot's `is_member` property is false, the connector fires a side-effect API call to join that channel before yielding the record. Archived channels are always skipped because the Slack API rejects `conversations.join` for archived channels. This means reading the channels stream can modify the Slack workspace state.

**Why this matters:** The channels stream is not read-only when `join_channels` is enabled. It actively modifies the workspace by joining channels, which is a side effect that no other connector stream produces. The Slack API only returns messages from channels the bot has joined, so this behavior exists to ensure the messages and threads streams can actually retrieve data. If the bot lacks permission to join a channel, it logs a warning but does not fail the sync.

## 2. Dynamic Rate Limit Policy Switching on First 429

The `MessagesAndThreadsApiBudget` starts with an `UnlimitedCallRatePolicy` (no rate limiting) and dynamically switches to a `MovingWindowCallRatePolicy` of 1 request per 60 seconds after the first 429 response. This switch is permanent for the duration of the sync and only applies to OAuth connections (API token connections do not use this budget).

**Why this matters:** The connector starts fast with no rate limiting and then abruptly drops to 1 request per minute after hitting its first 429. This dramatic slowdown is intentional but can make syncs appear to stall. The rate limit policy is not reset between stream reads within the same sync, so hitting a 429 on the messages stream will also throttle the threads stream.

## 3. Thread Replies Are Bounded by the Thread Cursor and Skipped from `latest_reply`

The `threads` stream sends its per-thread cursor as `oldest`/`latest` (with `inclusive`) on `conversations.replies`, so each sync reads only replies newer than the saved cursor minus the lookback window. `ThreadRepliesHttpRequester` returns `None` instead of sending the request when the parent message's `latest_reply` (passed through the partition's `extra_fields`) is finite and strictly older than that request's `oldest`; a missing, invalid or non-finite `latest_reply` still sends the request.

**Why this matters:** Slack returns the thread's parent message on every page of a bounded replies call, so the parent row is re-emitted whenever a request is made and left out when the request is skipped. Replies older than the window are never re-read, so edits to them are not picked up, and a thread that first appears after its replies were posted (a channel joined later, a widened `channel_filter`) starts from the global cursor minus the lookback window. Unit-test mocks for `conversations.replies` must return the parent regardless of `oldest`.

## Incremental Stream Considerations

The Slack API supports `oldest`/`latest` timestamp filtering on conversations.history and related endpoints. The connector uses Python custom components (`JoinChannelsStream`) referenced from the manifest.

**Connector type:** Python custom components (hybrid manifest + Python)

**Analysis status:** Streams are Python-defined via custom components. Full stream-by-stream analysis requires Python code review.

### Future incremental stream candidates

- **All streams deferred for Python code review:** This connector defines its streams in Python code rather than declarative manifest YAML. A full stream-by-stream incremental analysis table (per the standard CONTRIBUTING.md schema) should be added by a future agent after reviewing the Python stream definitions, their `cursor_field` properties, and the API endpoints they call.
