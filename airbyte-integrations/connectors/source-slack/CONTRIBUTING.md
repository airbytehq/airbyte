# source-slack: Unique Behaviors

## 1. Auto-Joining Channels During Sync

When `join_channels` is enabled in the config, the `ChannelsRetriever` automatically joins Slack channels by making POST requests to `conversations.join` during the channels stream read. For each non-archived channel where the bot's `is_member` property is false, the connector fires a side-effect API call to join that channel before yielding the record. Archived channels are always skipped because the Slack API rejects `conversations.join` for archived channels. This means reading the channels stream can modify the Slack workspace state.

**Why this matters:** The channels stream is not read-only when `join_channels` is enabled. It actively modifies the workspace by joining channels, which is a side effect that no other connector stream produces. The Slack API only returns messages from channels the bot has joined, so this behavior exists to ensure the messages and threads streams can actually retrieve data. If the bot lacks permission to join a channel, it logs a warning but does not fail the sync.

## 2. Dynamic Rate Limit Policy Switching on First 429

The `MessagesAndThreadsApiBudget` starts with an `UnlimitedCallRatePolicy` (no rate limiting) and dynamically switches to a `MovingWindowCallRatePolicy` of 1 request per 60 seconds after the first 429 response. This switch is permanent for the duration of the sync and only applies to OAuth connections (API token connections do not use this budget).

**Why this matters:** The connector starts fast with no rate limiting and then abruptly drops to 1 request per minute after hitting its first 429. This dramatic slowdown is intentional but can make syncs appear to stall. The rate limit policy is not reset between stream reads within the same sync, so hitting a 429 on the messages stream will also throttle the threads stream.
