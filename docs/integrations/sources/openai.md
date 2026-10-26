# OpenAI
OpenAI organization and ChatGPT Enterprise compliance source. Syncs organization members and pending invites from the OpenAI Admin API, daily completion usage aggregated by project, user, and model, and ChatGPT workspace user rosters (current and historical). For Enterprise workspaces, also syncs compliance conversation log metadata and message-level events from JSONL export files. Requires an OpenAI organization API key with admin access. ChatGPT Enterprise compliance streams additionally require a compliance API token and workspace ID. Supports incremental sync on usage and compliance log streams using a configurable start and end date (YYYY-MM-DD).

The connection **check** only runs the `users` stream (OpenAI Admin API). A valid organization API key can pass the check even if the compliance token or workspace ID is missing or invalid; those errors appear when compliance-related streams run during a sync.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `end_time` | `string` (date, `YYYY-MM-DD`) | End Time. The end time for querying the API in YYYY-MM-DD (defaults to today if omitted). Because the end date is treated as midnight UTC on that day, **today’s data is not included until a sync runs after that calendar day ends** (typically the next day). |  |
| `start_time` | `string` (date, `YYYY-MM-DD`) | Start time. The start time for querying the API in YYYY-MM-DD |  |
| `openai_token` | `string` | OpenAI-token. The API key token used for authorizing API requests |  |
| `workspace_id` | `string` | Workspace ID. Required for compliance streams; not validated during connection check. |  |
| `openai_organization` | `string` | OpenAI-Organization. The organization (organization_id) associated with the request |  |
| `openai_compliance_token` | `string` | OpenAI-compliance-token. Required for compliance streams; not validated during connection check (only `users` is checked). |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| users | id | DefaultPaginator | ✅ |  ❌  |
| conversation_messages | id | DefaultPaginator | ✅ |  ✅  |
| conversation_messages_log | event_id.snapshot_date | No pagination | ✅ |  ✅  |
| invites | id | DefaultPaginator | ✅ |  ❌  |
| completions | snapshot_date.project_id.user_id.model | DefaultPaginator | ✅ |  ✅  |
| current_users | id | DefaultPaginator | ✅ |  ❌  |
| historical_users | id | DefaultPaginator | ✅ |  ❌  |

### `conversation_messages_log`

Each JSONL line is flattened for analytics: message text is available as `message_content_value`, conversation metadata includes `conversation_title`, and `message.author` is split into `author_type`, `author_client_type`, `author_skills_used`, and `author_tools_used`. The raw nested `message` and `conversation` objects are not emitted.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-10-08 | | Initial release by [@Ella6882](https://github.com/Ella6882) via Connector Builder |

</details>
