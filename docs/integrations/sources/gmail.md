# Gmail

<HideInUI>

This page contains the setup guide and reference information for the [Gmail](https://mail.google.com/) source connector.

</HideInUI>

Gmail is the email service provided by Google. The Gmail source connector replicates messages, drafts, threads, labels, and the authenticated user's profile from Gmail's [REST API](https://developers.google.com/gmail/api/reference/rest).

## Prerequisites

- A Google account with access to the mailbox you want to replicate.
- The OAuth scope `https://www.googleapis.com/auth/gmail.readonly`. The connector reads from Gmail and never modifies messages, labels, or settings.
<!-- env:oss -->
- For **Airbyte Open Source**: a Google Cloud project with the [Gmail API enabled](https://console.cloud.google.com/apis/library/gmail.googleapis.com), plus either an OAuth 2.0 client and refresh token, or a service account key.
<!-- /env:oss -->

## Setup guide

### Step 1: Set up authentication

The Gmail source connector supports two authentication methods: **OAuth** and **Service Account Key**. Both methods require the `https://www.googleapis.com/auth/gmail.readonly` scope.

<!-- env:cloud -->

#### OAuth (recommended for Airbyte Cloud)

In **Airbyte Cloud**, sign in with the Google account whose mailbox you want to replicate. Airbyte Cloud handles the OAuth flow for you — you only need to authorize Airbyte through the standard Google consent screen when configuring the source.

<!-- /env:cloud -->

<!-- env:oss -->

#### OAuth for Airbyte Open Source

To authenticate with OAuth in **Airbyte Open Source**, create your own OAuth client in your Google Cloud project and complete the authorization code flow yourself to obtain a refresh token. You will need the resulting **Client ID**, **Client Secret**, and **Refresh Token** to configure the connector.

1. In the Google Cloud console, [enable the Gmail API](https://console.cloud.google.com/apis/library/gmail.googleapis.com) for your project.
2. Configure your OAuth consent screen and add the `https://www.googleapis.com/auth/gmail.readonly` scope. See [Choose Gmail API scopes](https://developers.google.com/workspace/gmail/api/auth/scopes).
3. Follow [Google's web server OAuth 2.0 guide](https://developers.google.com/identity/protocols/oauth2/web-server) to create a **Web application** OAuth client and exchange the authorization code for a refresh token.

#### Service Account Key for Airbyte Open Source

You can also authenticate with a Google service account key. Because Gmail mailboxes are owned by individual users, the service account must use [domain-wide delegation](https://developers.google.com/identity/protocols/oauth2/service-account#delegatingauthority) to access mailboxes in a Google Workspace domain.

1. Open the [Service Accounts page](https://console.cloud.google.com/iam-admin/serviceaccounts) in your Google Cloud console and create a new service account, or select an existing one.
2. In the **Keys** tab, click **Add Key** > **Create new key**, select **JSON**, and download the key file. Store it securely — Google does not let you re-download it.
3. In your Google Workspace [admin console](https://admin.google.com/), enable [domain-wide delegation](https://support.google.com/a/answer/162106) for the service account's client ID and authorize the `https://www.googleapis.com/auth/gmail.readonly` scope.

:::note
Only a Google Workspace super administrator can configure domain-wide delegation. Domain-wide delegation lets the service account impersonate users in your Workspace organization to read their mailboxes.
:::

<!-- /env:oss -->

### Step 2: Set up the Gmail connector in Airbyte

1. Log into your Airbyte instance, click **Sources**, and click **+ New source**.
2. Select **Gmail** from the source type dropdown.
3. Choose your authentication method:
   - **Authenticate via Google (OAuth)** — Click **Authenticate your account** and complete the Google sign-in flow. **Airbyte Cloud** users authenticate against Airbyte's pre-registered OAuth app. **Airbyte Open Source** users provide their own **Client ID**, **Client Secret**, and **Refresh Token**.
   - **Service Account Key Authentication** — Paste the contents of your service account JSON key file into the **Service Account Information** field.
4. (Optional) Set **Start date** in `YYYY-MM-DDTHH:MM:SSZ` format. Only messages, drafts, and threads received on or after this date are replicated. If you leave it blank, the connector replicates the full mailbox history.
5. (Optional) Toggle **Include Spam & Trash** to include drafts and messages from the Spam and Trash folders. Defaults to off.
6. (Optional) Adjust **Number of concurrent workers** (between `2` and `10`, default `5`) to control how many requests the connector issues in parallel. Lower this value if you see frequent rate-limit errors.
7. Click **Set up source** to test the connection and save the configuration.

## Supported sync modes

The Gmail source connector supports the following [sync modes](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/):

| Sync mode                       | Supported |
|---------------------------------|:---------:|
| Full Refresh \| Overwrite       | Yes       |
| Full Refresh \| Append          | Yes       |
| Incremental \| Append           | Yes       |
| Incremental \| Append + Deduped | Yes       |

Only the `messages_details` stream supports incremental sync. All other streams run in full refresh mode on every sync.

## Streams

| Stream             | Primary Key | Sync Mode                   | Description                                                                              |
|--------------------|:-----------:|-----------------------------|------------------------------------------------------------------------------------------|
| `profile`          | _(none)_    | Full Refresh                | The authenticated user's Gmail profile, including email address and history ID.          |
| `drafts`           | `id`        | Full Refresh                | Stub records (`id`, `message.id`, `message.threadId`) returned by `users.drafts.list`.   |
| `labels`           | `id`        | Full Refresh                | All Gmail labels, including system labels (e.g. `INBOX`, `SENT`) and user-created labels.|
| `labels_details`   | `id`        | Full Refresh                | Per-label metadata such as message and thread counts. Substream of `labels`.             |
| `messages`         | `id`        | Full Refresh                | Stub records (`id`, `threadId`) returned by `users.messages.list`.                       |
| `messages_details` | `id`        | Incremental on `internalDate` | Full message payloads, headers, snippet, and labels. Substream of `messages`.          |
| `threads`          | `id`        | Full Refresh                | Stub records (`id`, `historyId`) returned by `users.threads.list`.                       |
| `threads_details`  | `id`        | Full Refresh                | Per-thread details and the messages in each thread. Substream of `threads`.              |

The `messages_details` cursor is the message's `internalDate` field — the Unix epoch in milliseconds when Gmail received the message. Other streams expose only `id` and `threadId` from the upstream `list` calls and have no record-level cursor field, so they run as full refresh.

When **Start date** is set, the connector applies the Gmail `after:<epoch_seconds>` [search operator](https://support.google.com/mail/answer/7190) to the `messages`, `drafts`, and `threads` `list` requests so the API skips records older than that date.

## Performance considerations

The Gmail API enforces two simultaneous quota limits, measured in [quota units](https://developers.google.com/gmail/api/reference/quota):

| Limit type              | Limit                                  | Error code              |
|-------------------------|----------------------------------------|-------------------------|
| Per project rate limit  | 1,200,000 quota units per minute       | `rateLimitExceeded`     |
| Per user rate limit     | 15,000 quota units per minute per user | `userRateLimitExceeded` |

Each `messages.list` and `messages.get` call costs 5 units, and each `threads.list` and `threads.get` call costs 10 units. The `messages_details` and `threads_details` substreams issue one `get` call per parent record, so high-volume mailboxes consume quota quickly.

The connector retries `429 Too Many Requests` and `403` quota-saturation errors with exponential backoff. If you see frequent rate-limit warnings in sync logs, lower the **Number of concurrent workers** setting.

## Limitations & troubleshooting

- **`messages` and `threads` are stub-only.** The Gmail API's `users.messages.list` and `users.threads.list` endpoints return only `{id, threadId}` (or `{id, historyId}`) per record. To replicate the full message body, headers, or labels, sync the `messages_details` or `threads_details` substream alongside its parent.
- **Service account mailbox access requires domain-wide delegation.** A service account without domain-wide delegation has no Gmail mailbox of its own to read. Configure domain-wide delegation in your Workspace admin console so the service account can impersonate Workspace users.
- **Read-only scope.** This connector reads from Gmail only. The required scope is `https://www.googleapis.com/auth/gmail.readonly`. Granting broader Gmail scopes is not necessary and not recommended.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `credentials` | `object` | Authentication. Credentials for connecting to the Gmail API. |  |
| `credentials.client_id` | `string` | Client ID. Enter your Google application's Client ID. See Google's documentation for more information. |  |
| `credentials.client_secret` | `string` | Client Secret. Enter your Google application's Client Secret. See Google's documentation for more information. |  |
| `credentials.client_refresh_token` | `string` | Refresh Token. Enter your Google application's refresh token. See Google's documentation for more information. |  |
| `credentials.service_account_info` | `string` | Service Account Information. The JSON key of the service account to use for authorization. |  |
| `include_spam_and_trash` | `boolean` | Include Spam &amp; Trash. Include drafts/messages from SPAM and TRASH in the results. Defaults to false. | false |
| `num_workers` | `integer` | Number of concurrent workers. Higher values result in faster syncs but may trigger rate limiting on lower-tier Gmail API quotas. Reduce this value if you see frequent rate-limit errors in sync logs. | 5 |
| `start_date` | `string` | UTC date and time in the format YYYY-MM-DDTHH:MM:SSZ. Only messages, threads, and drafts received on or after this date will be replicated. If unset, the full history is replicated. |  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.1.1 | 2026-05-04 | [76065](https://github.com/airbytehq/airbyte/pull/76065) | Add OAuth flow with credentials wrapper, config migration, and Service Account auth |
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
