> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-slack: Unique Behaviors

## 1. Auto-Joining Channels During Sync

When `join_channels` is enabled in the config, the `ChannelsRetriever` automatically joins Slack channels by making POST requests to `conversations.join` during the channels stream read. For each non-archived channel where the bot's `is_member` property is false, the connector fires a side-effect API call to join that channel before yielding the record. Archived channels are always skipped because the Slack API rejects `conversations.join` for archived channels. This means reading the channels stream can modify the Slack workspace state.

**Why this matters:** The channels stream is not read-only when `join_channels` is enabled. It actively modifies the workspace by joining channels, which is a side effect that no other connector stream produces. The Slack API only returns messages from channels the bot has joined, so this behavior exists to ensure the messages and threads streams can actually retrieve data. If the bot lacks permission to join a channel, it logs a warning but does not fail the sync.

## 2. Dynamic Rate Limit Policy Switching on First 429

The `MessagesAndThreadsApiBudget` starts with an `UnlimitedCallRatePolicy` (no rate limiting) and dynamically switches to a `MovingWindowCallRatePolicy` of 1 request per 60 seconds after the first 429 response. This switch is permanent for the duration of the sync and only applies to OAuth connections (API token connections do not use this budget).

**Why this matters:** The connector starts fast with no rate limiting and then abruptly drops to 1 request per minute after hitting its first 429. This dramatic slowdown is intentional but can make syncs appear to stall. The rate limit policy is not reset between stream reads within the same sync, so hitting a 429 on the messages stream will also throttle the threads stream.

## 3. Threads State Migration Only Rewrites Legacy State

`ThreadsStateMigration` converts legacy `threads` state (a top-level `float_ts`, or per-thread `states` with no `parent_state`) into a single `parent_state.channel_messages` cursor. State that already contains `parent_state.channel_messages` is left untouched, so per-channel cursors survive restarts and resumed attempts continue from where each channel left off. The `lookback_window` is applied by the parent `channel_messages` cursor itself.

**Why this matters:** Rewriting current-format state on every sync collapses all per-channel cursors into one value and, when no thread cursor has been saved yet, resets every channel to `start_date`.

## 4. Message and Thread Partitions Skip Unjoinable Channels

The `channel_messages` and `threads` streams only build partitions for channels where the bot is a member, or for non-archived channels when `join_channels` is enabled. Archived channels the bot is not a member of are skipped because they cannot be joined and `conversations.history` would return `not_in_channel`. The `channels` and `channel_members` streams still return every channel.

## Incremental Stream Considerations

The Slack API supports `oldest`/`latest` timestamp filtering on conversations.history and related endpoints. The connector uses Python custom components (`JoinChannelsStream`) referenced from the manifest.

**Connector type:** Python custom components (hybrid manifest + Python)

**Analysis status:** Streams are Python-defined via custom components. Full stream-by-stream analysis requires Python code review.

### Future incremental stream candidates

- **All streams deferred for Python code review:** This connector defines its streams in Python code rather than declarative manifest YAML. A full stream-by-stream incremental analysis table (per the standard CONTRIBUTING.md schema) should be added by a future agent after reviewing the Python stream definitions, their `cursor_field` properties, and the API endpoints they call.
