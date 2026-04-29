# Gmail

<HideInUI>

This page contains the setup guide and reference information for the [Gmail](https://developers.google.com/gmail/api) source connector.

</HideInUI>

The Gmail source connector syncs data from a single Gmail account using the [Gmail API](https://developers.google.com/gmail/api/reference/rest). It extracts messages, threads, drafts, and labels in read-only mode.

## Prerequisites

- A Google Cloud project with the [Gmail API enabled](https://console.cloud.google.com/apis/library/gmail.googleapis.com)
- OAuth 2.0 credentials (Client ID, Client Secret, and Refresh Token) with the `https://www.googleapis.com/auth/gmail.readonly` scope

## Setup guide

### Step 1: Create a Google Cloud project and enable the Gmail API

1. Go to the [Google Cloud Console](https://console.cloud.google.com/) and create a new project, or select an existing one.
2. Navigate to **APIs & Services > Library**.
3. Search for **Gmail API** and click **Enable**.

### Step 2: Create OAuth 2.0 credentials

1. In the Google Cloud Console, go to **APIs & Services > Credentials**.
2. Click **+ Create Credentials** and select **OAuth client ID**.
3. If prompted, configure the [OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent) first. Add the scope `https://www.googleapis.com/auth/gmail.readonly`.
4. For **Application type**, select **Web application**.
5. Under **Authorized redirect URIs**, add the redirect URI for your Airbyte instance.
6. Click **Create** and note the **Client ID** and **Client Secret**.

For a detailed walkthrough, see [Google's guide to creating OAuth credentials](https://developers.google.com/gmail/api/auth/web-server#create_a_client_id_and_client_secret).

### Step 3: Obtain a refresh token

Follow [Google's OAuth 2.0 for Web Server Applications guide](https://developers.google.com/identity/protocols/oauth2/web-server) to complete the OAuth flow and obtain a refresh token.

### Step 4: Configure the connector in Airbyte

1. Enter your **Client ID**, **Client Secret**, and **Refresh Token**.

<FieldAnchor field="start_date">

2. Optionally, set a **Start date** to limit replication to messages, threads, and drafts received on or after that date. If left blank, the connector replicates the full history.

</FieldAnchor>

<FieldAnchor field="num_workers">

3. Optionally, adjust the **Number of concurrent workers** to control sync speed. The default of 5 works well for most accounts. If you encounter frequent rate-limit errors, reduce this value. Valid range: 2--10.

</FieldAnchor>

<FieldAnchor field="include_spam_and_trash">

4. Optionally, enable **Include Spam & Trash** to include messages and drafts from the SPAM and TRASH folders.

</FieldAnchor>

## Supported streams

| Stream | Primary key | Pagination | Full Refresh | Incremental |
|---|---|---|---|---|
| [profile](https://developers.google.com/gmail/api/reference/rest/v1/users/getProfile) | | No pagination | Yes | No |
| [drafts](https://developers.google.com/gmail/api/reference/rest/v1/users.drafts/list) | `id` | Yes | Yes | No |
| [labels](https://developers.google.com/gmail/api/reference/rest/v1/users.labels/list) | `id` | No pagination | Yes | No |
| [labels_details](https://developers.google.com/gmail/api/reference/rest/v1/users.labels/get) | `id` | No pagination | Yes | No |
| [messages](https://developers.google.com/gmail/api/reference/rest/v1/users.messages/list) | `id` | Yes | Yes | No |
| [messages_details](https://developers.google.com/gmail/api/reference/rest/v1/users.messages/get) | `id` | No pagination | Yes | Yes |
| [threads](https://developers.google.com/gmail/api/reference/rest/v1/users.threads/list) | `id` | Yes | Yes | No |
| [threads_details](https://developers.google.com/gmail/api/reference/rest/v1/users.threads/get) | `id` | No pagination | Yes | No |

### Stream details

- **profile**: Returns the authenticated user's email address, total messages count, total threads count, and current history ID.
- **drafts**: Lists draft message stubs (ID and message metadata). Use `messages_details` for full message content.
- **labels**: Lists all labels in the mailbox, including system labels such as `INBOX`, `SENT`, and `TRASH`.
- **labels_details**: Retrieves full details for each label, including message and thread counts.
- **messages**: Lists message stubs (ID and thread ID) without message content. If `start_date` is configured, only messages received after that date are returned.
- **messages_details**: Retrieves the full content of each message, including headers, body, and labels. This is the only stream that supports incremental sync, using the message's `internalDate` as the cursor. On incremental syncs, previously synced messages are filtered out based on the stored cursor value.
- **threads**: Lists thread stubs (ID and snippet). If `start_date` is configured, only threads with messages after that date are returned.
- **threads_details**: Retrieves the full content of each thread, including all messages in the thread.

### Parent-child stream relationships

Several streams use a parent-child pattern where a "list" stream provides IDs and a "details" stream fetches the full record for each ID:

- `labels` &rarr; `labels_details`
- `messages` &rarr; `messages_details`
- `threads` &rarr; `threads_details`

When you select a details stream, Airbyte automatically syncs the corresponding parent stream to obtain the IDs.

## Rate limiting

The Gmail API enforces two simultaneous quota limits:

| Limit | Quota |
|---|---|
| Per-project | 1,200,000 quota units per minute |
| Per-user | 15,000 quota units per minute |

Each API method consumes a different number of quota units. For example, `messages.list` costs 5 units and `messages.get` costs 5 units per call. See [Gmail API usage limits](https://developers.google.com/gmail/api/reference/quota) for the full table.

The connector handles rate limiting automatically by retrying when Gmail returns HTTP 429 or quota-saturation 403 responses. If you consistently hit rate limits, reduce the **Number of concurrent workers** in the connector configuration.

## Limitations and known issues

- **Incremental sync is only available on `messages_details`.** All other streams use full refresh. On each sync, the parent `messages` list call fetches all message IDs (subject to `start_date` filtering) even during incremental syncs. The incremental cursor filters records on the `messages_details` side, reducing the volume of data written to the destination, but it does not reduce the number of Gmail API calls made.
- **The `start_date` filter uses server-side query filtering** via Gmail's `q=after:` parameter. Gmail interprets this filter using Unix timestamps, so filtering is precise to the second.
- **The connector requires the `gmail.readonly` scope.** It does not modify, send, or delete any data in the Gmail account.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.1.0 | 2026-04-29 | [76431](https://github.com/airbytehq/airbyte/pull/76431) | Add `messages_details` incremental sync, optional `start_date` server-side filtering on `messages`/`drafts`/`threads`, configurable concurrency via `num_workers`, and Gmail-aware rate-limit handling (429 + 403 quota-saturation) |
| 0.0.52 | 2026-04-28 | [77264](https://github.com/airbytehq/airbyte/pull/77264) | Update dependencies |
| 0.0.51 | 2026-04-21 | [76616](https://github.com/airbytehq/airbyte/pull/76616) | Update dependencies |
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
