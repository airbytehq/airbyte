# Asyntai
Asyntai is an AI chat agent for websites. This source copies the chats it handles into your warehouse: every conversation, every message in it, the visitors who left an email address or a phone number, and the support tickets the agent raised.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API key. Your Asyntai API key. Sign in to Asyntai, open Settings, then API, and copy the key. The API needs the Starter plan or higher. |  |
| `start_date` | `string` | Start date. Only read chats, leads and tickets from this moment on. Leave it as it is to read the whole history. | 2020-01-01T00:00:00Z |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| sessions | session_id | DefaultPaginator | ✅ |  ✅  |
| messages | session_id.timestamp.role | No pagination | ✅ |  ❌  |
| leads | session_id | DefaultPaginator | ✅ |  ✅  |
| tickets | ticket_number | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-09-19 | | Initial release by [@asyntai](https://github.com/asyntai) via Connector Builder |

</details>
