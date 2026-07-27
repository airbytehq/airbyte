# Discord

<HideInUI>

This page contains the setup guide and reference information for the [Discord](https://discord.com) source connector.

</HideInUI>

## Prerequisites

- A Discord account with access to the [Developer Portal](https://discord.com/developers/applications)
- A Discord bot token (created in Step 1 below)
- The bot must be invited to each guild (server) you want to sync

## Setup guide

### Step 1: Create a Discord application and bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click **New Application** and give it a name.
3. Navigate to the **Bot** section in the left sidebar.
4. Click **Reset Token** to generate a bot token. Copy and save this token securely — you need it to configure the connector.

:::caution
Discord only shows the token once. If you lose it, you must reset it to generate a new one.
:::

### Step 2: Enable privileged intents

Some streams require [privileged intents](https://discord.com/developers/docs/events/gateway#privileged-intents) to be enabled:

1. In the **Bot** section of the Developer Portal, scroll down to **Privileged Gateway Intents**.
2. Enable **Message Content Intent** if you need full message content, embeds, attachments, and components. Without this intent, the `messages` stream returns empty `content`, `embeds`, `attachments`, and `components` fields for most messages.
3. Enable **Server Members Intent** if you want to sync the `members` stream. Without this intent, the List Guild Members endpoint returns a 403 error.

:::note
If your bot is in 100 or more guilds, Discord requires your application to be [verified](https://support.discord.com/hc/en-us/articles/360040720412-Bot-Verification-and-Data-Allowlisting). Verified bots must apply for privileged intent approval through the Developer Portal before these intents take effect.
:::

### Step 3: Invite the bot to your guild

1. Navigate to the **OAuth2** section in the left sidebar.
2. Under **OAuth2 URL Generator**, select the `bot` scope.
3. Under **Bot Permissions**, select:
   - **View Channels** — required for reading channels and messages
   - **Read Message History** — required for accessing historical messages and archived threads
   - **Manage Threads** — required only if you need private archived thread messages
4. Copy the generated URL and open it in your browser.
5. Select the guild you want to add the bot to and click **Authorize**.

Repeat this process for each guild you want to sync.

### Step 4: Set up the Discord connector in Airbyte

<!-- env:cloud -->

**For Airbyte Cloud:**

1. Navigate to **Sources** and click **New source**.
2. Find and select **Discord**.
3. Enter a name for your source.
4. Paste the **Bot Token** you copied from the Developer Portal.
5. Click **Set up source**.

<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

1. Navigate to **Sources** and click **New source**.
2. Find and select **Discord**.
3. Enter a name for your source.
4. Paste the **Bot Token** you copied from the Developer Portal.
5. Click **Set up source**.

<!-- /env:oss -->

## Supported sync modes

The Discord source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                   | Supported? |
| :------------------------ | :--------- |
| Full Refresh Sync         | Yes        |
| Incremental - Append Sync | No         |
| Namespaces                | No         |

## Supported streams

The connector syncs data from the following Discord API endpoints:

| Stream             | Description                                                                                   |
| :----------------- | :-------------------------------------------------------------------------------------------- |
| `guilds`           | Guilds (servers) the bot has joined. Parent stream for all other streams.                      |
| `channels`         | All channels in each guild, including text, voice, category, forum, and announcement channels. |
| `messages`         | Messages from text channels, announcement channels, active threads, and archived threads. Paginated newest-to-oldest. |
| `members`          | Guild member list with roles, join dates, and nicknames. Requires Server Members Intent.       |
| `roles`            | All roles in each guild with permissions and metadata.                                         |
| `threads`          | Active threads across all channels in each guild.                                              |
| `scheduled_events` | Scheduled events in each guild.                                                                |

## Rate limiting

Discord applies both global and per-route rate limits:

- **Global limit**: 50 requests per second
- **Per-route limits**: Vary by endpoint, communicated via `X-RateLimit-*` response headers

The connector automatically handles rate limiting by reading the `Retry-After` header and waiting before retrying.

## Limitations and notes

- **Message channel coverage**: The `messages` stream reads from text channels (type 0) and announcement channels (type 5), plus their active and archived threads. Messages in forum channels, media channels, and voice channels are not directly fetched. However, active threads — including active forum posts — are included because the active threads endpoint returns threads from all channel types.
- **Archived forum and media threads**: Archived threads are only fetched from text and announcement channels. Archived forum posts and archived media channel threads are not included.
- **Message Content Intent**: Without the `MESSAGE_CONTENT` privileged intent enabled in the Developer Portal, the `messages` stream returns empty `content`, `embeds`, `attachments`, and `components` fields for most messages. Messages that mention the bot or are sent in DMs with the bot still include content.
- **Server Members Intent**: The `members` stream requires the `GUILD_MEMBERS` privileged intent. Without it, the List Guild Members endpoint returns a 403 error. The connector surfaces this error so you know to enable the intent.
- **Messages pagination**: The `messages` stream performs a full refresh, walking newest-to-oldest using the `before` cursor parameter. For channels with large message histories, the initial sync may take a long time. Incremental sync is not yet supported.
- **Thread messages**: Messages from active threads and archived threads are automatically included in the `messages` stream alongside regular channel messages. Private archived threads require the bot to have **Manage Threads** and **Read Message History** permissions. Without those permissions, the connector fails with an actionable error instead of silently skipping records.
- **Channel permissions**: The connector skips channels where the bot lacks access (403 errors are ignored for per-channel streams). Streams that require guild-level permissions (`members`) fail with an actionable error if permissions are missing.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject                         |
| :------ | :--------- | :----------- | :------------------------------ |
| 0.1.6 | 2026-07-21 | [82364](https://github.com/airbytehq/airbyte/pull/82364) | Update dependencies |
| 0.1.5 | 2026-07-14 | [81769](https://github.com/airbytehq/airbyte/pull/81769) | Update dependencies |
| 0.1.4 | 2026-06-30 | [81015](https://github.com/airbytehq/airbyte/pull/81015) | Update dependencies |
| 0.1.3 | 2026-06-23 | [80400](https://github.com/airbytehq/airbyte/pull/80400) | Update dependencies |
| 0.1.2 | 2026-06-16 | [79820](https://github.com/airbytehq/airbyte/pull/79820) | Update dependencies |
| 0.1.1 | 2026-06-09 | [79241](https://github.com/airbytehq/airbyte/pull/79241) | Update dependencies |
| 0.1.0 | 2026-06-08 | [76376](https://github.com/airbytehq/airbyte/pull/76376) | Initial release of source-discord connector with 7 streams: guilds, channels, messages, members, roles, threads, and scheduled_events. |

</details>
