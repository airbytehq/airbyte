# source-slack: Unique Behaviors

## 1. Auto-Joining Channels During Sync

When `join_channels` is enabled in the config, the `ChannelsRetriever` automatically joins Slack channels by making POST requests to `conversations.join` during the channels stream read. For each channel where the bot's `is_member` property is false, the connector fires a side-effect API call to join that channel before yielding the record. This means reading the channels stream can modify the Slack workspace state.

**Why this matters:** The channels stream is not read-only when `join_channels` is enabled. It actively modifies the workspace by joining channels, which is a side effect that no other connector stream produces. The Slack API only returns messages from channels the bot has joined, so this behavior exists to ensure the messages and threads streams can actually retrieve data. If the bot lacks permission to join a channel, it logs a warning but does not fail the sync.

## 2. Rate Limit Handling via CDK Built-in RATE_LIMITED Action

HTTP 429 responses are handled by the CDK's built-in `RATE_LIMITED` error action with `WaitTimeFromHeader` backoff strategies that read the `Retry-After` header from the Slack API. This retries indefinitely with proper backoff rather than failing after a fixed number of retries.

**Why this matters:** The `RATE_LIMITED` action raises `RateLimitBackoffException` which retries indefinitely with exponential backoff respecting the Slack API's `Retry-After` header. This is distinct from the `RETRY` action which raises `DefaultBackoffException` and permanently fails after a limited number of retries. The channel_messages and threads streams use the shared base requester definition rather than a custom requester class.
