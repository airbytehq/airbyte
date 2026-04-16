# Microsoft Teams Migration Guide

## Upgrading to 2.0.0

Version 2.0.0 is a major overhaul of the Microsoft Teams connector. It replaces legacy Outlook group conversation APIs with modern Microsoft Graph Teams APIs and adds comprehensive coverage for agent search use cases.

### Removed streams

The following streams have been removed:

| Removed Stream | Replacement |
| :--- | :--- |
| `conversations` | `channel_messages` |
| `conversation_threads` | `channel_messages` |
| `conversation_posts` | `channel_message_replies` |
| `channel_tabs` | _(no replacement — low search value)_ |
| `team_device_usage_report` | _(no replacement — admin analytics, low search value)_ |

### New streams added

- `teams`, `channel_messages`, `channel_message_replies`, `chats`, `chat_messages`, `team_members`, `channel_members` (restructured), `chat_members`, `online_meetings`, `meeting_transcripts`, `meeting_attendance_reports`, `tags`, `tag_members`

### Required permissions

New API permissions are required for the new streams. See the [setup guide](microsoft-teams.md) for the full list. Key additions include:

- `Team.ReadBasic.All` — for the teams stream
- `Chat.Read.All` / `ChatMessage.Read.All` — for chats and chat messages
- `ChannelMessage.Read.All` — for channel messages and replies
- `OnlineMeetings.Read.All` — for online meetings
- `TeamworkTag.Read.All` — for tags

### Migration steps

1. Select **Connections** in the main navbar.
2. From the list of your existing connections, select the connection(s) affected by the update.
3. Select the **Replication** tab, then select **Refresh source schema**.

:::note
Any detected schema changes will be listed for your review. Select **OK** when you are ready to proceed.
:::

4. Remove any of the deleted streams (`conversations`, `conversation_threads`, `conversation_posts`, `channel_tabs`, `team_device_usage_report`) from your configured catalog.
5. Enable the new replacement streams (`channel_messages`, `channel_message_replies`, etc.) as needed.
6. Ensure your Azure AD app registration has the new required permissions listed above.
7. At the bottom of the page, select **Save changes**.

:::caution
Depending on your destination, you may be prompted to **Reset all streams**. This is recommended to ensure clean data with the new schema.
:::

8. Select **Save connection**. This will reset the data in your destination (if selected) and initiate a fresh sync.

For more information on resetting your data in Airbyte, see [this page](/platform/operator-guides/clear).

---

## Upgrading to 1.0.0

Version 1.0.0 of the Microsoft Teams source connector introduces breaking changes to the schemas of all streams. A full schema refresh is required to ensure a seamless upgrade to this version.

### Refresh schemas and reset data

1. Select **Connections** in the main navbar.
2. From the list of your existing connections, select the connection(s) affected by the update.
3. Select the **Replication** tab, then select **Refresh source schema**.

:::note
Any detected schema changes will be listed for your review. Select **OK** when you are ready to proceed.
:::

4. At the bottom of the page, select **Save changes**.

:::caution
Depending on your destination, you may be prompted to **Reset all streams**. Although this step is not required to proceed, it is highly recommended for users who have selected `Full Refresh | Append` sync mode, as the updated schema may lead to inconsistencies in the data structure within the destination.
:::

5. Select **Save connection**. This will reset the data in your destination (if selected) and initiate a fresh sync.

For more information on resetting your data in Airbyte, see [this page](/platform/operator-guides/clear).

### Changes in 1.0.0

- The naming convention for field names in previous versions used "snake_case", which is not aligned with the "camelCase" convention used by the Microsoft Graph API. For example:

`user_id` -> `userId`
`created_date` -> `createdDate`

With the update to "camelCase", fields that may have been unrecognized or omitted in earlier versions will now be properly mapped and included in the data synchronization process, enhancing the accuracy and completeness of your data.

- The `team_device_usage_report` stream contained a fatal bug that could lead to crashes during syncs. You should now be able to reliably use this stream during syncs.

- `Date` and `date-time` fields have been typed as airbyte_type `date` and `timestamp_without_timezone`, respectively.
