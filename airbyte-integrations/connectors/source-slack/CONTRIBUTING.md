# source-slack: Unique Behaviors

## 1. Auto-Joining Channels During Sync

When `join_channels` is enabled in the config, the `ChannelsRetriever` automatically joins Slack channels by making POST requests to `conversations.join` during the channels stream read. For each non-archived channel where the bot's `is_member` property is false, the connector fires a side-effect API call to join that channel before yielding the record. Archived channels are always skipped because the Slack API rejects `conversations.join` for archived channels. This means reading the channels stream can modify the Slack workspace state.

**Why this matters:** The channels stream is not read-only when `join_channels` is enabled. It actively modifies the workspace by joining channels, which is a side effect that no other connector stream produces. The Slack API only returns messages from channels the bot has joined, so this behavior exists to ensure the messages and threads streams can actually retrieve data. If the bot lacks permission to join a channel, it logs a warning but does not fail the sync.

## 2. Dynamic Rate Limit Policy Switching on First 429

The `MessagesAndThreadsApiBudget` starts with an `UnlimitedCallRatePolicy` (no rate limiting) and dynamically switches to a `MovingWindowCallRatePolicy` of 1 request per 60 seconds after the first 429 response. This switch is permanent for the duration of the sync and only applies to OAuth connections (API token connections do not use this budget).

**Why this matters:** The connector starts fast with no rate limiting and then abruptly drops to 1 request per minute after hitting its first 429. This dramatic slowdown is intentional but can make syncs appear to stall. The rate limit policy is not reset between stream reads within the same sync, so hitting a 429 on the messages stream will also throttle the threads stream.

## 3. Threads Resume From the Parent `channel_messages` State

The `threads` stream has no usable cursor of its own for deciding which messages to revisit, so `ThreadsStateMigration` runs on every sync and prepares `parent_state.channel_messages`, which is what decides the `oldest` sent to `conversations.history` for each channel. When that parent state already holds per-channel cursors, each channel resumes from its own cursor, moved forward to the point up to which all channels were last read completely (the parent's global `state` cursor) and capped at the newest thread cursor minus `lookback_window`. A single cursor for all channels is only synthesized for state that has no parent cursors (state saved before `threads` recorded a parent state).

Message and thread partitions are only built for channels the bot can read: channels it is a member of, plus, when `join_channels` is enabled, non-archived channels (which it joins). Archived channels the bot is not in are skipped because they cannot be joined.

**Why this matters:** Replacing the per-channel cursors with one value makes an interrupted sync start every channel over (from `start_date` when `threads` has not saved a cursor yet, which is also the shape of its state once it passes 10,000 thread partitions and switches to a global cursor) and can skip messages in channels that had not been read yet.

## Incremental Stream Considerations

The Slack API supports `oldest`/`latest` timestamp filtering on conversations.history and related endpoints. The connector uses Python custom components (`JoinChannelsStream`) referenced from the manifest.

**Connector type:** Python custom components (hybrid manifest + Python)

**Analysis status:** Streams are Python-defined via custom components. Full stream-by-stream analysis requires Python code review.

### Future incremental stream candidates

- **All streams deferred for Python code review:** This connector defines its streams in Python code rather than declarative manifest YAML. A full stream-by-stream incremental analysis table (per the standard CONTRIBUTING.md schema) should be added by a future agent after reviewing the Python stream definitions, their `cursor_field` properties, and the API endpoints they call.
