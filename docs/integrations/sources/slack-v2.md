# Slack (v2, Bulk CDK)

<HideInUI>

This page contains the setup guide and reference information for the Slack v2 source connector, a
Kotlin rewrite of the [Slack](slack.md) connector on Airbyte's Bulk CDK.

</HideInUI>

The connector reads the same five streams as the Slack connector it replaces, with the same
configuration, catalog, records and state, and needs far fewer Slack API calls to do so: a one-month
history that took the previous connector most of a day now costs one `conversations.replies` call
per thread instead of one per message, and the streams are read concurrently within Slack's
per-method rate limits.

## Prerequisites

- A Slack workspace and either
  - **Sign in via Slack (OAuth)** on Airbyte Cloud, or
  - a **bot token** (`xoxb-`) of a Slack app installed in the workspace with the scopes
    `channels:history`, `channels:join`, `channels:read`, `groups:read`, `groups:history` and
    `users:read`.
- For private channels, add the bot to each channel: Slack does not let apps join private channels.

## Setup guide

1. **Start Date**: messages before this UTC instant (`2017-01-25T00:00:00Z`) are not replicated.
2. **Threads Lookback window (Days)**: how far before the saved cursor the `channel_messages` and
   `threads` streams look again on every sync. Replies to a thread whose parent message is older
   than the lookback window are not detected, so set it to the age of the threads that are still
   active in your workspace (7 to 30 days is typical). Default 0.
3. **Join all channels**: when enabled (default), the bot joins every public channel it is not a
   member of, so that their messages can be read. Disable it to sync only the channels the bot
   was added to.
4. **Include private channels** / **Include archived channels**: off by default.
5. **Channel name filter**: channel names (without `#`) to sync; empty means all channels.
6. **Ignore messages with no replies in threads stream**: see the `threads` stream below.
7. **Authentication mechanism**: OAuth (Airbyte Cloud) or bot token.
8. **Number of concurrent threads** (`num_workers`) / **Concurrency**: how many streams are read at
   the same time; see "Performance". Default 2.
9. **Channel messages date window size (in days)**: the size of the date windows a channel's
   history is read in. Default 100 days.
10. **Checkpoint Target Time Interval**: how often the long streams save their progress. Default
    300 seconds.

## Supported sync modes

| Feature | Supported |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes (`channel_messages`, `threads`) |
| Replicate Incremental Deletes | No |
| SSL connection | Yes |
| Namespaces | No |

## Supported streams

| Stream | Slack method | Sync modes | Primary key | Cursor |
| :--- | :--- | :--- | :--- | :--- |
| `users` | `users.list` | Full refresh | `id` | |
| `channels` | `conversations.list` | Full refresh | `id` | |
| `channel_members` | `conversations.members` | Full refresh | `member_id`, `channel_id` | |
| `channel_messages` | `conversations.history` | Full refresh, incremental | `channel_id`, `ts` | `float_ts` |
| `threads` | `conversations.replies` | Full refresh, incremental | `channel_id`, `ts` | `float_ts` |

Records are the JSON objects Slack returns (every field, not only the ones in the schema), plus
`channel_id` and `float_ts` (the message `ts` as a number) on `channel_messages` and `threads`.

### `channel_messages`

Every top-level message of every selected channel (members of the bot, or every public channel
when "Join all channels" is on) from the start date, in date windows. Each incremental sync reads,
per channel, from the saved cursor minus the lookback window up to the instant the sync started.

### `threads`

For every message of `channel_messages`, the messages of its thread: the parent first, then the
replies. This is what the previous connector produced with one `conversations.replies` call per
message. The v2 connector:

- emits a message without replies as is, without a call (Slack would return just that message);
- fetches a thread once per sync, even when it appears several times in the history (broadcast
  replies);
- on incremental syncs, skips threads whose `latest_reply` predates the last completed sync (minus
  the lookback window), because their replies were all emitted already.

With **Ignore messages with no replies in threads stream** on, messages without replies are left
out of the stream (as with the previous connector).

## Performance and rate limits

Slack limits every Web API method separately, per app and workspace (`conversations.history` and
`conversations.replies`: 50+ requests per minute; `conversations.list` and `users.list`: 20+;
`conversations.members`: 100+), and answers HTTP 429 with a `Retry-After` header when a budget is
exhausted. The connector paces each method at its documented rate, halves the rate and waits for
`Retry-After` on a 429, and restores it after a run of successful requests. Because the budgets are
per method, the streams are read concurrently (`concurrency`, default 2): with 5 the five streams
run side by side without competing for the same budget. Reading one stream on several threads
would not help, so the connector never does.

**Non-Marketplace apps.** Since May 2025, Slack limits `conversations.history` and
`conversations.replies` to 1 request per minute and 15 messages per request for apps that are
distributed outside the Slack Marketplace (internal apps of your own workspace and Marketplace apps
such as Airbyte's keep the standard limits). The connector detects the 15-message pages, logs a
warning and keeps going, but such a sync is slow by construction; authenticate with the Airbyte
OAuth app or with a bot token of an app created in your own workspace.

**What a sync costs**, for C selected channels, M top-level messages and T threads in the window:
`channel_messages` is about `C + M / 999` calls, `threads` is about `C + M / 999 + T` calls (the
history pages are shared between the two streams within a sync), `channel_members` is about `C`,
`users` and `channels` a handful.

## Limitations

- Direct messages and group direct messages are not synced (no `im:history`/`mpim:history` scopes).
- Edited or deleted replies do not update `latest_reply`; use the lookback window to re-read
  recent threads.
- Replies to a thread whose parent is older than `start_date` or the lookback window are not
  detected.
- The `users`, `channels` and `channel_members` streams are not resumable: an interrupted sync
  reads them again from the start.

## Migrating from the Slack connector

The v2 connector accepts the configuration and the state of the Slack (3.x) connector unchanged;
no reset is needed. The first sync after the switch reads every thread in the lookback window once
(the previous connector's cursors say nothing about which threads changed); the following syncs
skip the unchanged ones.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| :------ | :--------- | :--------------------------------------------------------- | :---------------------------------------------- |
| 0.1.0 | 2026-09-25 | TBD | New Bulk CDK (Kotlin) implementation of the Slack source |

</details>
