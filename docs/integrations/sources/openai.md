# OpenAI

This connector syncs administrative and compliance data from two OpenAI products:

- **OpenAI API Platform**: organization members, pending invites, and daily completions usage from the [Admin API](https://developers.openai.com/api/docs/guides/admin-apis) at `api.openai.com`.
- **ChatGPT Enterprise and Edu**: workspace user rosters and conversation message compliance logs from the [Compliance Platform](https://help.openai.com/en/articles/9261474-openai-compliance-platform-for-enterprise-and-edu-customers) at `api.chatgpt.com`.

You can use the API Platform streams without a ChatGPT workspace. The ChatGPT streams need extra credentials.

## Prerequisites

- An OpenAI API Platform organization, and the **Owner** role in that organization so you can create an Admin API key.
- For the ChatGPT streams (`current_users`, `historical_users`, `conversation_messages`, and `conversation_messages_log`): a ChatGPT Enterprise or Edu workspace, and the **Owner** or **Admin** role in that workspace so you can create a workspace Admin key. Only workspace owners can grant the **Conversation messages** permission and broad compliance access.

## Setup guide

### Step 1: Get your API Platform organization ID and Admin API key

1. In [OpenAI Platform](https://platform.openai.com/), open your organization settings and copy your organization ID. It starts with `org-`.
2. As an organization owner, go to **Organization settings** > **Admin keys**, select **Create new admin key**, and choose the permissions the connector needs. The connector reads organization users, invites, and completions usage. See [Admin and Audit Logs API for the API Platform](https://help.openai.com/en/articles/9687866-admin-and-audit-logs-api-for-the-api-platform).
3. Copy the key. You can't view it again after you close the dialog.

Admin API keys only work with administration endpoints. A standard project API key doesn't work.

### Step 2 (optional): Get a ChatGPT workspace Admin key and workspace ID

Skip this step if you only need the `users`, `invites`, and `completions` streams.

ChatGPT workspace Admin keys are separate from API Platform Admin keys. An API Platform key can't read ChatGPT workspace data, and a workspace key can't read API Platform data.

1. Sign in to [Admin Console](https://chatgpt.com/admin) and select the ChatGPT workspace you want to sync.
2. Go to **Credentials** > **Admin keys** and select **Create new admin key**.
3. Choose the permissions for the streams you plan to sync. For example, `current_users` needs read access to **Users**, and `conversation_messages` and `conversation_messages_log` need the **Conversation messages** compliance permission. For details, see [Managing Admin keys in Admin Console](https://help.openai.com/en/articles/20001407-managing-admin-keys-in-admin-console).
4. Choose an expiration. When the key expires, the ChatGPT streams start failing until you create a new key and update the connector.
5. Copy the key, and copy the workspace ID of the selected workspace.

### Step 3: Set up the connector in Airbyte

1. In Airbyte, create a new OpenAI source.
2. Enter the following values:
   - **OpenAI-Organization**: your API Platform organization ID.
   - **OpenAI-token**: your API Platform Admin API key.
   - **Start time**: the first date to sync, in `YYYY-MM-DD` format.
   - **End Time** (optional): the date to stop syncing, in `YYYY-MM-DD` format. If you leave it blank, the connector syncs up to the current date.
   - **OpenAI-compliance-token** (optional): your ChatGPT workspace Admin key.
   - **Workspace ID** (optional): your ChatGPT workspace ID.
3. Select **Set up source**.

The connection test only reads the `users` stream. It doesn't validate **OpenAI-compliance-token** or **Workspace ID**. If either value is missing or wrong, the ChatGPT streams fail during the sync instead. If you didn't provide these values, deselect the ChatGPT streams in your connection.

## Supported sync modes

| Stream | Full Refresh | Incremental |
| --- | --- | --- |
| `users` | Yes | No |
| `invites` | Yes | No |
| `completions` | Yes | Yes |
| `current_users` | Yes | No |
| `historical_users` | Yes | No |
| `conversation_messages` | Yes | Yes |
| `conversation_messages_log` | Yes | Yes |

## Supported streams

### API Platform streams

These streams use **OpenAI-Organization** and **OpenAI-token**.

| Stream | Primary key | Description |
| --- | --- | --- |
| `users` | `id` | Members of the API Platform organization, from [`GET /v1/organization/users`](https://developers.openai.com/api/reference/resources/organization/subresources/users/). |
| `invites` | `id` | Invitations to the API Platform organization, from [`GET /v1/organization/invites`](https://developers.openai.com/api/reference/resources/organization/subresources/invites/). |
| `completions` | `snapshot_date`, `project_id`, `user_id`, `model` | Daily completions usage, such as request counts and input and output token counts, grouped by project, user, and model. Data comes from [`GET /v1/organization/usage/completions`](https://developers.openai.com/api/reference/resources/admin/subresources/organization/subresources/usage/methods/completions/). The cursor is `start_time`, the start of each daily bucket. Days with no usage don't produce records. |

### ChatGPT workspace streams

These streams use **OpenAI-compliance-token** and **Workspace ID**.

| Stream | Primary key | Description |
| --- | --- | --- |
| `current_users` | `id` | Current members of the ChatGPT workspace, including role and seat type, from `GET /v1/manage/workspaces/{workspace_id}/users`. |
| `historical_users` | `id` | ChatGPT workspace users from the Compliance API endpoint `GET /v1/compliance/workspaces/{workspace_id}/users`, including each user's status and creation time. |
| `conversation_messages` | `id` | Metadata for `CONVERSATION_MESSAGE` compliance log files, such as file name, size, and SHA-256 hash. It doesn't contain message content. The cursor is `snapshot_date`, the start of the one-day window in which the connector listed the file. |
| `conversation_messages_log` | `event_id`, `snapshot_date` | One record per conversation message event, read from each log file listed by `conversation_messages`. |

`conversation_messages_log` downloads each JSONL log file that `conversation_messages` lists, and flattens each event into top-level columns:

- `actor` and `principal` become `actor_*` and `principal_*` columns.
- Message text is in `message_content_value`.
- Conversation metadata becomes `conversation_*` columns, such as `conversation_title` and `conversation_mode`.
- `message.author` becomes `author_type`, `author_client_type`, `author_skills_used`, and `author_tools_used`.

The connector converts skills, tools, and non-text message content to strings. It doesn't emit the original nested `message`, `conversation`, `actor`, and `principal` objects, or any field not listed in the stream schema.

`conversation_messages_log` contains the text of user conversations. Restrict access to the destination tables that hold this data.

## Date range behavior

The `completions`, `conversation_messages`, and `conversation_messages_log` streams read data between **Start time** and **End Time**. The connector reads `completions` in 31-day windows and the compliance log files in one-day windows.

**End Time** is exclusive and refers to midnight UTC at the start of that day. If you leave **End Time** blank, the connector uses midnight UTC at the start of the current day, so it doesn't sync the current day's data until a sync runs after that day ends in UTC. If you set **End Time** to a fixed date, incremental syncs stop picking up new data after that date.

The `users`, `invites`, `current_users`, and `historical_users` streams always return the full current list and ignore the date range.

## Limitations and troubleshooting

- **Rate limits**: The connector retries requests that return HTTP 429, 500, 502, 503, or 504 up to five times with exponential backoff.
- **ChatGPT streams fail but the connection test passes**: The connection test only checks the API Platform credentials. Check that **OpenAI-compliance-token** and **Workspace ID** are set, that the key hasn't expired or been revoked, and that it has the permissions the failing stream needs.
- **Authentication errors on API Platform streams**: Make sure **OpenAI-token** is an API Platform organization Admin key, not a project API key or a ChatGPT workspace Admin key, and that **OpenAI-Organization** matches the organization that owns the key.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| :------ | :--- | :----------- | :------ |
| 0.0.1 | 2026-10-26 | [88374](https://github.com/airbytehq/airbyte/pull/88374) | Initial release by [@Ella6882](https://github.com/Ella6882) via Connector Builder |

</details>
