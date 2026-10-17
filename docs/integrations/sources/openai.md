# OpenAI
OpenAI organization and ChatGPT Enterprise compliance source. Syncs organization members and pending invites from the OpenAI Admin API, daily completion usage aggregated by project, user, and model, and ChatGPT workspace user rosters (current and historical). For Enterprise workspaces, also syncs compliance conversation log metadata and message-level events from JSONL export files. Requires an OpenAI organization API key with admin access, a ChatGPT compliance API token, and a workspace ID. Supports incremental sync on usage and compliance log streams using a configurable start and end date (YYYY-MM-DD).

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `end_time` | `string` | End Time. The end time for querying the API in YYYY-MM-DD (defaults to today if omitted) |  |
| `start_time` | `string` | Start time. The start time for querying the API in YYYY-MM-DD |  |
| `openai_token` | `string` | OpenAI-token. The API key token used for authorizing API requests |  |
| `workspace_id` | `string` | Workspace ID. The ID of the workspace. |  |
| `openai_organization` | `string` | OpenAI-Organization. The organization (organization_id) associated with the request |  |
| `openai_compliance_token` | `string` | OpenAI-compliance-token. The API key token used for authorizing compliance API endpoint requests |  |

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

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-10-08 | | Initial release by [@Ella6882](https://github.com/Ella6882) via Connector Builder |

</details>
