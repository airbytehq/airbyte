# Telegram Bot API

## Features

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental - Append Sync     | No         |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

This source connector uses the [Telegram Bot API](https://core.telegram.org/bots/api) to extract data from Telegram bots, chats, and channels. It requires a Telegram Bot token obtained from [@BotFather](https://t.me/botfather).

## Supported Streams

| Stream               | Sync Mode    | Description                                       |
| :------------------- | :----------- | :------------------------------------------------ |
| get_me               | Full Refresh | Bot identity and capabilities                     |
| updates              | Full Refresh | Recent updates received by the bot (24h retention)|
| chats                | Full Refresh | Chat details for configured chat IDs              |
| chat_administrators  | Full Refresh | Administrators for configured chats               |
| webhook_info         | Full Refresh | Current webhook configuration and status          |

## Prerequisites

1. A Telegram Bot token, obtained by creating a bot through [@BotFather](https://t.me/botfather).
2. For chat-related streams (`chats`, `chat_administrators`), the bot must be added as a member of the target chats, and you need the chat IDs.

## Setup Guide

1. **Create a Telegram Bot**: Message [@BotFather](https://t.me/botfather) on Telegram and follow the prompts to create a new bot. Copy the bot token provided.
2. **Get Chat IDs** (optional): To sync chat-related streams, you need the numeric chat IDs. For groups and channels, these are typically negative numbers (e.g., `-1001234567890`).
3. **Add Bot to Chats**: Ensure the bot is a member of any chats you want to sync data from.
4. **Configure the Connector**: Enter your bot token and optionally provide chat IDs and allowed update types.

## Configuration

| Parameter         | Type     | Required | Description                                                                                                  |
| :---------------- | :------- | :------- | :----------------------------------------------------------------------------------------------------------- |
| bot_token         | string   | Yes      | Telegram Bot API token from @BotFather. Format: `{bot_id}:{secret_token}`                                    |
| chat_ids          | array    | No       | List of chat IDs to retrieve data from. Required for chats, chat_administrators streams.                      |
| allowed_updates   | array    | No       | Filter which update types to receive. If empty, all types are received.                                       |

## Rate Limiting

The Telegram Bot API has rate limits. The connector includes automatic retry with backoff for HTTP 429 (rate limit) responses.

## Limitations

- The `updates` stream uses `getUpdates`, which only retains data for 24 hours. For historical message access, consider using the Telegram MTProto API (not supported by this connector).
- Chat-related streams require the bot to be a member of the target chats.
- The `getUpdates` method cannot be used simultaneously with webhooks; if a webhook is set, `getUpdates` will not return results.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                              |
| :------ | :--------- | :------------------------------------------------------- | :----------------------------------- |
| 0.1.0   | 2026-04-16 | TBD                                                      | Initial release of Telegram Bot API source connector |

</details>
