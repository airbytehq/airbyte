# Asyntai

[Asyntai](https://asyntai.com) is an AI chat agent for websites. It answers visitor questions from your own content, collects email addresses and phone numbers, and raises support tickets.

This source copies that work into your warehouse: every conversation, every message inside it, the visitors who left their details, and the tickets.

## Prerequisites

- An Asyntai account on the Starter plan or higher. The API is part of those plans.
- Your Asyntai API key.

## Setup guide

### Step 1: Get your API key

1. Sign in at [asyntai.com](https://asyntai.com).
2. Open **Settings**, then **API**.
3. Copy the API key.

### Step 2: Set up the source in Airbyte

1. In Airbyte, click **Sources**, then **New source**, and pick **Asyntai**.
2. Paste the API key into **API key**.
3. Set **Start date** if you only want recent data. Leave it as it is to copy the whole history.
4. Click **Set up source**.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API key. Your Asyntai API key. Sign in to Asyntai, open Settings, then API, and copy the key. The API needs the Starter plan or higher. |  |
| `start_date` | `string` | Start date. Only read chats, leads and tickets from this moment on. Leave it as it is to read the whole history. | 2020-01-01T00:00:00Z |

## Streams

| Stream Name | Primary Key | Cursor | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|--------|------------|---------------------|----------------------|
| sessions | session_id | last_message_at | DefaultPaginator | ✅ |  ✅  |
| messages | session_id.timestamp.role | | No pagination | ✅ |  ❌  |
| leads | session_id | started_at | DefaultPaginator | ✅ |  ✅  |
| tickets | ticket_number | created_at | DefaultPaginator | ✅ |  ✅  |

Every field is described in the [Asyntai API reference](https://asyntai.com/documentation/api-reference/). `messages` is a child stream of `sessions`. Each record carries the `session_id` of its parent, so all four tables join on that column.

### Reply times

Every chat carries its measured reply latency. Use `first_response_time_ms` on `sessions` for the first answer, and `response_time_ms` on an assistant message for that answer.

## Performance considerations

Every endpoint answers newest first and returns at most 100 records per call. The connector pages backward with the `before` parameter, which is exclusive, so a full history sync makes one call for every 100 records. The `messages` stream makes one call per conversation.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-09-19 | | Initial release by [@asyntai](https://github.com/asyntai) via Connector Builder |

</details>
