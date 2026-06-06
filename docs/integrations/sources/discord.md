# Discord

<HideInUI>

This page contains the setup guide and reference information for the [Discord](https://discord.com) source connector.

</HideInUI>

## Prerequisites

Before you begin, have the following ready:

- A Discord account with access to the [Developer Portal](https://discord.com/developers/applications)
- A Discord Bot Token
- The bot must be added to the guilds (servers) you want to sync data from

## Setup guide

### Step 1: Create a Discord application and bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click **New Application** and give it a name.
3. Navigate to the **Bot** section in the left sidebar.
4. Click **Reset Token** to generate a new bot token. Copy and save this token securely --- you will need it to configure the connector.

### Step 2: Enable privileged intents

Some streams require privileged intents to be enabled in the Developer Portal:

1. In the **Bot** section, scroll down to **Privileged Gateway Intents**.
2. Enable **Message Content Intent** to read full message content, embeds, attachments, and components. Without this, the `messages` stream will only return message metadata with empty content.
3. Enable **Server Members Intent** to access the full member list via the `members` stream.

### Step 3: Invite the bot to your guild

1. Navigate to the **OAuth2** section in the left sidebar.
2. Under **OAuth2 URL Generator**, select the `bot` scope.
3. Under **Bot Permissions**, select:
   - **View Channels** --- required for reading channels and messages
   - **Read Message History** --- required for accessing historical messages and archived threads
   - **Manage Threads** --- required for reading private archived threads
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
| `guilds`           | All guilds (servers) the bot has joined. Entry point for all other streams.                    |
| `channels`         | All channels in each guild, including text, voice, category, forum, and announcement channels. |
| `messages`         | Messages from all text-capable channels, active threads, and archived threads. Paginated newest-to-oldest. |
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

- **Message Content Intent**: Without the `MESSAGE_CONTENT` privileged intent enabled in the Developer Portal, the `messages` stream will return empty `content` fields for most messages. Only messages that mention the bot or are DMs will have content populated.
- **Server Members Intent**: The `members` stream requires the `GUILD_MEMBERS` privileged intent. Without it, requests to list guild members will return a 403 error. The connector surfaces this error clearly so users know to enable the intent.
- **Messages pagination**: The `messages` stream performs a full refresh walking newest-to-oldest using the `before` cursor parameter. For channels with very large message histories, the initial sync may take a long time. Incremental sync is not yet supported.
- **Thread messages**: Messages from active threads and archived threads are automatically included in the `messages` stream alongside regular channel messages. Private archived threads require the bot to have **Manage Threads** and **Read Message History**; without those permissions, the connector fails with an actionable permission error instead of silently skipping those records.
- **Channel permissions**: The connector gracefully handles channels where the bot lacks access by skipping those channels (403 errors are ignored for per-channel streams). Streams that require guild-level permissions (`members`) will fail with an actionable error if permissions are missing.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject                         |
| :------ | :--------- | :----------- | :------------------------------ |
| 0.1.0   | 2026-04-16 | [76376](https://github.com/airbytehq/airbyte/pull/76376) | Initial release of source-discord connector with 7 streams: guilds, channels, messages, members, roles, threads, and scheduled_events. |

</details>
