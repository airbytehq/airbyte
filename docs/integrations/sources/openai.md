# OpenAI
OpenAI organization and ChatGPT Enterprise compliance source. Syncs organization members and pending invites from the OpenAI Admin API, daily completion usage aggregated by project, user, and model, and ChatGPT workspace user rosters (current and historical). For Enterprise workspaces, also syncs compliance conversation log metadata and message-level events from JSONL export files. Requires an OpenAI organization API key with admin access. ChatGPT Enterprise compliance streams additionally require a compliance API token and workspace ID. Supports incremental sync on usage and compliance log streams using a configurable start and end date (YYYY-MM-DD).

The connection **check** only runs the `users` stream (OpenAI Admin API). A valid organization API key can pass the check even if the compliance token or workspace ID is missing or invalid; those errors appear when compliance-related streams run during a sync.

## Setup

### API Platform (Admin API) — required for `users`, `invites`, and `completions`

1. **Organization ID** — In [OpenAI Platform](https://platform.openai.com/) organization settings, copy your organization ID (for example `org-…`). Enter it as **OpenAI-Organization** (`openai_organization`).
2. **Admin API key** — An organization owner creates an [Admin API key](https://help.openai.com/en/articles/9687866-admin-and-audit-logs-api-for-the-api-platform) under **Organization settings → Admin keys**. Use a key with the scopes needed for members, invites, and usage (see the [Admin APIs guide](https://developers.openai.com/api/docs/guides/admin-apis)). Enter the secret as **OpenAI-token** (`openai_token`).

These credentials call `api.openai.com` (organization users, invites, and completion usage). They are separate from ChatGPT workspace Admin keys.

### ChatGPT Enterprise compliance — required for compliance streams only

Compliance-related streams (`conversation_messages`, `conversation_messages_log`, `current_users`, `historical_users`) require a **[ChatGPT Enterprise or Edu](https://help.openai.com/en/articles/9261474-openai-compliance-platform-for-enterprise-and-edu-customers)** workspace. Standard API Platform access alone is not enough.

1. **Compliance API token** — In [Admin Console](https://chatgpt.com/admin), a workspace owner or admin creates a **workspace-scoped Admin key** with the compliance permissions your integration needs (for example conversation messages and workspace user read access). See [Managing Admin keys in Admin Console](https://help.openai.com/en/articles/20001407-managing-admin-keys-in-admin-console). Enter the key as **OpenAI-compliance-token** (`openai_compliance_token`). Only workspace owners can grant broad compliance or conversation-message access.
2. **Workspace ID** — In Admin Console, open the target workspace and copy its workspace ID from the URL or workspace settings. Enter it as **Workspace ID** (`workspace_id`). Compliance API requests use `https://api.chatgpt.com/v1` with this ID in the path.

If you only need organization admin data, you can leave the compliance token and workspace ID blank and disable the compliance streams in the connection schema.

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

Each JSONL line is flattened for analytics: `actor` and `principal` become `actor_*` and `principal_*` columns, message text is in `message_content_value`, conversation metadata includes `conversation_title`, and `message.author` is split into `author_type`, `author_client_type`, `author_skills_used`, and `author_tools_used` (skills, tools, and non-text content are stringified so nested or tuple-shaped API values type cleanly). The raw nested `message`, `conversation`, `actor`, and `principal` objects are not emitted.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.2 | 2026-10-27 | [90015](https://github.com/airbytehq/airbyte/pull/90015) | Update dependencies |
| 0.0.1 | 2026-10-08 | [88374](https://github.com/airbytehq/airbyte/pull/88374) | Initial release by [@Ella6882](https://github.com/Ella6882) via Connector Builder |

</details>
