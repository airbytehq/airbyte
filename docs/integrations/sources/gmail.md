# Gmail

<HideInUI>

This page contains the setup guide and reference information for the [Gmail](https://developers.google.com/gmail/api) source connector.

</HideInUI>

Gmail is Google's email service. This connector reads data from a single Gmail account using the [Gmail API](https://developers.google.com/gmail/api/reference/rest).

## Prerequisites

- A Google Account with Gmail enabled
<!-- env:oss -->
- For Airbyte Open Source: A Google Cloud project with the Gmail API enabled, and OAuth 2.0 credentials (Client ID, Client Secret, and Refresh Token)
<!-- /env:oss -->

## Setup guide

<!-- env:cloud -->

### For Airbyte Cloud

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click **Sources**, then click **+ New source**.
3. Search for and select **Gmail**.
4. Click **Authenticate via Google (OAuth)**, then click **Sign in with Google** and complete the authentication flow.

<FieldAnchor field="include_spam_and_trash">

1. (Optional) Enable **Include Spam & Trash** to include messages and drafts from your Spam and Trash folders. This is disabled by default.

</FieldAnchor>

1. Click **Set up source** and wait for the tests to complete.

<!-- /env:cloud -->

<!-- env:oss -->

### For Airbyte Open Source

To use this connector with Airbyte Open Source, you need OAuth 2.0 credentials from a Google Cloud project.

#### Create OAuth credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Go to **APIs & Services > Library**, search for **Gmail API**, and enable it.
4. Go to **APIs & Services > Credentials** and click **+ Create Credentials > OAuth client ID**.
5. If prompted, configure the OAuth consent screen. Add `https://www.googleapis.com/auth/gmail.readonly` as a scope.
6. Select **Web application** as the app type.
7. Note the **Client ID** and **Client Secret**.
8. Obtain a **Refresh Token** by following [Google's OAuth 2.0 guide for web server applications](https://developers.google.com/identity/protocols/oauth2/web-server). The required scope is `https://www.googleapis.com/auth/gmail.readonly`.

#### Set up the connector

1. Navigate to the Airbyte Open Source dashboard.
2. Click **Sources**, then click **+ New source**.
3. Search for and select **Gmail**.

<FieldAnchor field="credentials">

1. Choose your authentication method:
   - **Authenticate via Google (OAuth)**: Enter your **Client ID**, **Client Secret**, and **Refresh Token**.
   - **Enter credentials manually**: Enter the same credentials directly.

</FieldAnchor>

<FieldAnchor field="include_spam_and_trash">

1. (Optional) Enable **Include Spam & Trash** to include messages and drafts from your Spam and Trash folders. This is disabled by default.

</FieldAnchor>

1. Click **Set up source** and wait for the tests to complete.

<!-- /env:oss -->

<HideInUI>

## Supported sync modes

The Gmail source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)

## Supported streams

The Gmail source connector supports the following streams:

| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
| ----------- | ----------- | ---------- | ------------------- | -------------------- |
| [profile](https://developers.google.com/gmail/api/reference/rest/v1/users/getProfile) | | No pagination | ✅ | ❌ |
| [drafts](https://developers.google.com/gmail/api/reference/rest/v1/users.drafts/list) | id | DefaultPaginator | ✅ | ❌ |
| [labels](https://developers.google.com/gmail/api/reference/rest/v1/users.labels/list) | id | No pagination | ✅ | ❌ |
| [labels_details](https://developers.google.com/gmail/api/reference/rest/v1/users.labels/get) | id | No pagination | ✅ | ❌ |
| [messages](https://developers.google.com/gmail/api/reference/rest/v1/users.messages/list) | id | DefaultPaginator | ✅ | ❌ |
| [messages_details](https://developers.google.com/gmail/api/reference/rest/v1/users.messages/get) | id | No pagination | ✅ | ❌ |
| [threads](https://developers.google.com/gmail/api/reference/rest/v1/users.threads/list) | id | DefaultPaginator | ✅ | ❌ |
| [threads_details](https://developers.google.com/gmail/api/reference/rest/v1/users.threads/get) | id | No pagination | ✅ | ❌ |

### Stream details

- **profile**: Returns the authenticated user's Gmail profile, including their email address, total message count, and total thread count.
- **drafts**: Lists all drafts in the account. Each record contains the draft ID and a reference to its underlying message.
- **labels**: Lists all labels in the account, including both system labels and user-created labels.
- **labels_details**: Returns detailed information about each label, including message and thread counts. This is a substream of `labels`.
- **messages**: Lists all message IDs and thread IDs in the account. Use this with `messages_details` to get full message content.
- **messages_details**: Returns the full content of each message, including headers, body, labels, and attachments metadata. This is a substream of `messages`.
- **threads**: Lists all thread IDs in the account. Use this with `threads_details` to get full thread content.
- **threads_details**: Returns the full content of each thread, including all messages in the thread. This is a substream of `threads`.

:::note
The `messages_details` and `threads_details` streams make one API request per message or thread. For accounts with large volumes of email, these streams may take a long time to sync and consume significant API quota.
:::

## Performance considerations

The Gmail API enforces [usage limits](https://developers.google.com/gmail/api/reference/quota):

- **Per-project rate limit**: 1,200,000 quota units per minute
- **Per-user rate limit**: 15,000 quota units per user per minute

Each API method consumes a different number of quota units. For example, `messages.list` costs 5 units per request, while `messages.get` costs 5 units per request. If you encounter rate limit errors, consider syncing less frequently or reducing the number of enabled streams.

</HideInUI>

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.50 | 2026-03-24 | [75387](https://github.com/airbytehq/airbyte/pull/75387) | Update dependencies |
| 0.0.49 | 2026-03-10 | [74532](https://github.com/airbytehq/airbyte/pull/74532) | Update dependencies |
| 0.0.48 | 2026-03-03 | [74205](https://github.com/airbytehq/airbyte/pull/74205) | Update dependencies |
| 0.0.47 | 2026-02-11 | [73300](https://github.com/airbytehq/airbyte/pull/73300) | Revert OAuth authentication support |
| 0.0.45 | 2026-02-10 | [72593](https://github.com/airbytehq/airbyte/pull/72593) | Update dependencies |
| 0.0.44 | 2026-01-20 | [71967](https://github.com/airbytehq/airbyte/pull/71967) | Update dependencies |
| 0.0.43 | 2026-01-14 | [71388](https://github.com/airbytehq/airbyte/pull/71388) | Update dependencies |
| 0.0.42 | 2025-12-18 | [70726](https://github.com/airbytehq/airbyte/pull/70726) | Update dependencies |
| 0.0.41 | 2025-11-25 | [69871](https://github.com/airbytehq/airbyte/pull/69871) | Update dependencies |
| 0.0.40 | 2025-11-18 | [69412](https://github.com/airbytehq/airbyte/pull/69412) | Update dependencies |
| 0.0.39 | 2025-10-29 | [69004](https://github.com/airbytehq/airbyte/pull/69004) | Update dependencies |
| 0.0.38 | 2025-10-21 | [68299](https://github.com/airbytehq/airbyte/pull/68299) | Update dependencies |
| 0.0.37 | 2025-10-14 | [67999](https://github.com/airbytehq/airbyte/pull/67999) | Update dependencies |
| 0.0.36 | 2025-10-07 | [67258](https://github.com/airbytehq/airbyte/pull/67258) | Update dependencies |
| 0.0.35 | 2025-09-30 | [66299](https://github.com/airbytehq/airbyte/pull/66299) | Update dependencies |
| 0.0.34 | 2025-09-09 | [66063](https://github.com/airbytehq/airbyte/pull/66063) | Update dependencies |
| 0.0.33 | 2025-08-23 | [65371](https://github.com/airbytehq/airbyte/pull/65371) | Update dependencies |
| 0.0.32 | 2025-08-09 | [64626](https://github.com/airbytehq/airbyte/pull/64626) | Update dependencies |
| 0.0.31 | 2025-08-02 | [64194](https://github.com/airbytehq/airbyte/pull/64194) | Update dependencies |
| 0.0.30 | 2025-07-26 | [63861](https://github.com/airbytehq/airbyte/pull/63861) | Update dependencies |
| 0.0.29 | 2025-07-19 | [63463](https://github.com/airbytehq/airbyte/pull/63463) | Update dependencies |
| 0.0.28 | 2025-07-12 | [63123](https://github.com/airbytehq/airbyte/pull/63123) | Update dependencies |
| 0.0.27 | 2025-07-05 | [62624](https://github.com/airbytehq/airbyte/pull/62624) | Update dependencies |
| 0.0.26 | 2025-06-28 | [62169](https://github.com/airbytehq/airbyte/pull/62169) | Update dependencies |
| 0.0.25 | 2025-06-21 | [61834](https://github.com/airbytehq/airbyte/pull/61834) | Update dependencies |
| 0.0.24 | 2025-06-14 | [61134](https://github.com/airbytehq/airbyte/pull/61134) | Update dependencies |
| 0.0.23 | 2025-05-24 | [60608](https://github.com/airbytehq/airbyte/pull/60608) | Update dependencies |
| 0.0.22 | 2025-05-10 | [59895](https://github.com/airbytehq/airbyte/pull/59895) | Update dependencies |
| 0.0.21 | 2025-05-03 | [59276](https://github.com/airbytehq/airbyte/pull/59276) | Update dependencies |
| 0.0.20 | 2025-04-26 | [58813](https://github.com/airbytehq/airbyte/pull/58813) | Update dependencies |
| 0.0.19 | 2025-04-19 | [58184](https://github.com/airbytehq/airbyte/pull/58184) | Update dependencies |
| 0.0.18 | 2025-04-12 | [57732](https://github.com/airbytehq/airbyte/pull/57732) | Update dependencies |
| 0.0.17 | 2025-04-05 | [57214](https://github.com/airbytehq/airbyte/pull/57214) | Update dependencies |
| 0.0.16 | 2025-03-29 | [55947](https://github.com/airbytehq/airbyte/pull/55947) | Update dependencies |
| 0.0.15 | 2025-03-08 | [55265](https://github.com/airbytehq/airbyte/pull/55265) | Update dependencies |
| 0.0.14 | 2025-03-01 | [54937](https://github.com/airbytehq/airbyte/pull/54937) | Update dependencies |
| 0.0.13 | 2025-02-22 | [54417](https://github.com/airbytehq/airbyte/pull/54417) | Update dependencies |
| 0.0.12 | 2025-02-15 | [53369](https://github.com/airbytehq/airbyte/pull/53369) | Update dependencies |
| 0.0.11 | 2025-02-01 | [52831](https://github.com/airbytehq/airbyte/pull/52831) | Update dependencies |
| 0.0.10 | 2025-01-25 | [52329](https://github.com/airbytehq/airbyte/pull/52329) | Update dependencies |
| 0.0.9 | 2025-01-18 | [51700](https://github.com/airbytehq/airbyte/pull/51700) | Update dependencies |
| 0.0.8 | 2025-01-11 | [51110](https://github.com/airbytehq/airbyte/pull/51110) | Update dependencies |
| 0.0.7 | 2024-12-28 | [50536](https://github.com/airbytehq/airbyte/pull/50536) | Update dependencies |
| 0.0.6 | 2024-12-21 | [50008](https://github.com/airbytehq/airbyte/pull/50008) | Update dependencies |
| 0.0.5 | 2024-12-14 | [49474](https://github.com/airbytehq/airbyte/pull/49474) | Update dependencies |
| 0.0.4 | 2024-12-12 | [49185](https://github.com/airbytehq/airbyte/pull/49185) | Update dependencies |
| 0.0.3 | 2024-10-29 | [47852](https://github.com/airbytehq/airbyte/pull/47852) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47570](https://github.com/airbytehq/airbyte/pull/47570) | Update dependencies |
| 0.0.1 | 2024-10-09 | | Initial release by [@topefolorunso](https://github.com/topefolorunso) via Connector Builder |

</details>
