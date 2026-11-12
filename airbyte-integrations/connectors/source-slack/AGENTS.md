> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-slack: Unique Behaviors

## 1. Auto-Joining Channels During Sync

When `join_channels` is enabled in the config, the `ChannelsRetriever` automatically joins Slack channels by making POST requests to `conversations.join` during the channels stream read. For each non-archived channel where the bot's `is_member` property is false, the connector fires a side-effect API call to join that channel before yielding the record. Archived channels are always skipped because the Slack API rejects `conversations.join` for archived channels. This means reading the channels stream can modify the Slack workspace state.

**Why this matters:** The channels stream is not read-only when `join_channels` is enabled. It actively modifies the workspace by joining channels, which is a side effect that no other connector stream produces. The Slack API only returns messages from channels the bot has joined, so this behavior exists to ensure the messages and threads streams can actually retrieve data. If the bot lacks permission to join a channel, it logs a warning but does not fail the sync.

## 2. Dynamic Rate Limit Policy Switching on First 429

The `MessagesAndThreadsApiBudget` starts with an `UnlimitedCallRatePolicy` (no rate limiting) and dynamically switches to a `MovingWindowCallRatePolicy` of 1 request per 60 seconds after the first 429 response. This switch is permanent for the duration of the sync and only applies to OAuth connections (API token connections do not use this budget).

**Why this matters:** The connector starts fast with no rate limiting and then abruptly drops to 1 request per minute after hitting its first 429. This dramatic slowdown is intentional but can make syncs appear to stall. The rate limit policy is not reset between stream reads within the same sync, so hitting a 429 on the messages stream will also throttle the threads stream.

## 3. Threads Parent State Is Only Rebuilt For Legacy State

`ThreadsStateMigration` builds `parent_state.channel_messages` for the `threads` stream from the newest thread cursor (or `start_date`) minus the lookback window, as a single timestamp shared by every channel. It only runs when the incoming state has no `parent_state.channel_messages`, i.e. legacy state. State written by the current connector already holds one `channel_messages` cursor per channel and is passed through untouched.

**Why this matters:** Rebuilding the parent state on every sync discards the per-channel cursors. After an interrupted sync that makes every channel restart from `start_date` (when no thread cursor was saved) or jump to another channel's newer timestamp and skip messages. Do not make the migration unconditional again.

## 4. Message And Thread Partitions Skip Channels The Bot Cannot Read

The `channel_messages` and `threads` streams only create partitions for channels where `is_member` is true, or where `join_channels` is enabled and the channel is not archived. Archived channels cannot be joined, so archived channels the bot is not already a member of are never requested from `conversations.history`, even with `include_archived_channels` enabled. The `channels` and `channel_members` streams still return every channel.

## Incremental Stream Considerations

The Slack API supports `oldest`/`latest` timestamp filtering on conversations.history and related endpoints. The connector uses Python custom components (`JoinChannelsStream`) referenced from the manifest.

**Connector type:** Python custom components (hybrid manifest + Python)

**Analysis status:** Streams are Python-defined via custom components. Full stream-by-stream analysis requires Python code review.

### Future incremental stream candidates

- **All streams deferred for Python code review:** This connector defines its streams in Python code rather than declarative manifest YAML. A full stream-by-stream incremental analysis table (per the standard CONTRIBUTING.md schema) should be added by a future agent after reviewing the Python stream definitions, their `cursor_field` properties, and the API endpoints they call.
