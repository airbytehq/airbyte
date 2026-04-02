# source-slack: Unique Behaviors

## 1. Auto-Joining Channels During Sync

The `ChannelsRetriever` can automatically join Slack channels by making POST requests to `conversations.join` during the channels stream read. This behavior is controlled by two separate config fields: `join_all_non_archived_channels` (for active channels) and `join_all_archived_channels` (for archived channels). For each channel where the bot's `is_member` property is false and the corresponding join setting is enabled, the connector fires a side-effect API call to join that channel before yielding the record. This means reading the channels stream can modify the Slack workspace state.

**Why this matters:** The channels stream is not read-only when either join setting is enabled. It actively modifies the workspace by joining channels, which is a side effect that no other connector stream produces. The Slack API only returns messages from channels the bot has joined, so this behavior exists to ensure the messages and threads streams can actually retrieve data. If the bot lacks permission to join a channel, it logs a warning but does not fail the sync. A config migration automatically converts the legacy `join_channels` boolean into the two new fields.

## 2. Dynamic Rate Limit Policy Switching on First 429

The `MessagesAndThreadsApiBudget` starts with an `UnlimitedCallRatePolicy` (no rate limiting) and dynamically switches to a `MovingWindowCallRatePolicy` of 1 request per 60 seconds after the first 429 response. This switch is permanent for the duration of the sync and only applies to OAuth connections (API token connections do not use this budget).

**Why this matters:** The connector starts fast with no rate limiting and then abruptly drops to 1 request per minute after hitting its first 429. This dramatic slowdown is intentional but can make syncs appear to stall. The rate limit policy is not reset between stream reads within the same sync, so hitting a 429 on the messages stream will also throttle the threads stream.
