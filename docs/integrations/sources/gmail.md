# Gmail

<HideInUI>

This page contains the setup guide and reference information for the [Gmail](https://developers.google.com/workspace/gmail/api) source connector.

</HideInUI>

## Prerequisites

- A [Google Cloud project](https://console.cloud.google.com/)
- The [Gmail API](https://console.cloud.google.com/apis/library/gmail.googleapis.com) enabled in your Google Cloud project
- OAuth 2.0 credentials (Client ID, Client Secret, and refresh token) with the `https://www.googleapis.com/auth/gmail.readonly` scope

<HideInUI>

## Setup guide

### Create OAuth 2.0 credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/) and select your project.
2. Navigate to **APIs & Services > [Credentials](https://console.cloud.google.com/apis/credentials)**.
3. Click **+ Create Credentials** and select **OAuth client ID**.
4. If you haven't configured the [OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent) yet, complete the configuration first. Add the `https://www.googleapis.com/auth/gmail.readonly` scope.
5. For **Application type**, select **Web application**.
6. Note the **Client ID** and **Client Secret** values.

For more information, see [Create access credentials](https://developers.google.com/workspace/guides/create-credentials) in Google's documentation.

### Obtain a refresh token

Follow [Google's OAuth 2.0 guide for server-side web applications](https://developers.google.com/identity/protocols/oauth2/web-server) to complete the OAuth flow and obtain a refresh token. Use the `https://www.googleapis.com/auth/gmail.readonly` scope when requesting authorization.

### Set up the Gmail source connector in Airbyte

1. In Airbyte, go to **Sources** and select **Gmail**.
2. Enter your **OAuth Client ID**.
3. Enter your **OAuth Client Secret**.
4. Enter your **Refresh Token**.
5. Optionally, enable **Include Spam & Trash** to include messages, drafts, and threads from spam and trash folders.
6. Click **Set up source**.

</HideInUI>

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | OAuth Client ID. The Client ID from your Google Cloud OAuth 2.0 credentials. |  |
| `client_secret` | `string` | OAuth Client Secret. The Client Secret from your Google Cloud OAuth 2.0 credentials. |  |
| `client_refresh_token` | `string` | Refresh Token. A refresh token obtained through the Google OAuth 2.0 authorization flow. |  |
| `include_spam_and_trash` | `boolean` | Include Spam & Trash. Include drafts, messages, and threads from SPAM and TRASH in the results. | false |

## Supported sync modes

The Gmail source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)

## Supported streams

| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| [profile](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users/getProfile) |  | No pagination | ✅ |  ❌  |
| [drafts](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.drafts/list) | id | DefaultPaginator | ✅ |  ❌  |
| [labels](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.labels/list) | id | No pagination | ✅ |  ❌  |
| [labels_details](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.labels/get) | id | No pagination | ✅ |  ❌  |
| [messages](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/list) | id | DefaultPaginator | ✅ |  ❌  |
| [messages_details](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/get) | id | No pagination | ✅ |  ❌  |
| [threads](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.threads/list) | id | DefaultPaginator | ✅ |  ❌  |
| [threads_details](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.threads/get) | id | No pagination | ✅ |  ❌  |

<HideInUI>

### Stream details

- **profile**: The authenticated user's Gmail profile, including email address, total message count, and total thread count.
- **drafts**: Draft message IDs and their associated thread IDs.
- **labels**: All labels in the user's mailbox, including system labels such as INBOX and SENT.
- **labels_details**: Detailed information for each label, including the total and unread counts of messages and threads.
- **messages**: Message IDs and thread IDs in the user's mailbox.
- **messages_details**: Full content of each message, including headers, body, snippet, labels, and attachment metadata. This stream makes one API request per message returned by the `messages` stream.
- **threads**: Thread IDs and snippets in the user's mailbox.
- **threads_details**: Full thread content, including all messages in each thread. This stream makes one API request per thread returned by the `threads` stream.

## Performance considerations

The Gmail API enforces [usage limits](https://developers.google.com/workspace/gmail/api/reference/quota) based on quota units:

- **Per project**: 1,200,000 quota units per minute
- **Per user**: 15,000 quota units per minute

The `messages_details` and `threads_details` streams make one API request per record returned by their parent streams. For mailboxes with large volumes of messages or threads, these streams may take longer to sync and consume more API quota.

</HideInUI>

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
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
