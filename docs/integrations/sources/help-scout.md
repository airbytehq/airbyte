# Help Scout

This connector syncs data from the [Help Scout Inbox API 2.0](https://developer.helpscout.com/mailbox-api/), including conversations, threads, customers, inboxes, users, teams, tags, and workflows.

## Prerequisites

- A Help Scout account with an active, invited user. Help Scout ties API credentials to the user who creates them and returns a `401` error if that user isn't active.
- A Help Scout OAuth2 application. The connector authenticates with the [Client Credentials flow](https://developer.helpscout.com/mailbox-api/overview/authentication/#client-credentials-flow), so you only need the application's ID and secret.

## Setup guide

### Step 1: Create a Help Scout OAuth2 application

1. Sign in to Help Scout as the user whose access the connector should use.
2. Go to **Your Profile** > **My Apps** and click **Create My App**.
3. Enter a name for the app. Help Scout requires a redirection URL, but the Client Credentials flow doesn't use it, so you can enter a placeholder such as `https://www.example.com`.
4. Save the app, then copy its application ID and application secret.

The connector requests an access token with these credentials and refreshes it automatically when it expires.

### Step 2: Set up the connector in Airbyte

1. In Airbyte, create a new source and select **Help Scout**.
2. Enter the following values:
   - **Application ID**: The application ID from Step 1.
   - **Application Secret**: The application secret from Step 1.
   - **Start date**: The earliest date to sync data from, in UTC, using the format `YYYY-MM-DDTHH:MM:SSZ`. For example, `2024-01-01T00:00:00Z`. This value only applies to the `conversations`, `conversation_threads`, and `customers` streams.
3. Click **Set up source**.

## Supported sync modes

| Stream | Primary key | Full Refresh | Incremental | Cursor field |
|--------|-------------|--------------|-------------|--------------|
| `conversations` | `id` | Yes | Yes | `userUpdatedAt` |
| `conversation_threads` | `id` | Yes | Yes | `createdAt` |
| `customers` | `id` | Yes | Yes | `updatedAt` |
| `inboxes` | `id` | Yes | No | None |
| `inbox_custom_fields` | `id` | Yes | No | None |
| `inbox_folders` | `id` | Yes | No | None |
| `users` | `id` | Yes | No | None |
| `workflows` | `id` | Yes | No | None |
| `tags` | `id` | Yes | No | None |
| `teams` | `id` | Yes | No | None |
| `team_members` | `id` | Yes | No | None |

## Supported streams

| Stream | Help Scout endpoint | Notes |
|--------|---------------------|-------|
| `conversations` | [List Conversations](https://developer.helpscout.com/mailbox-api/endpoints/conversations/list/) | Includes conversations in every status (`status=all`), not only active ones. Records include embedded threads. Incremental syncs request conversations modified since the last sync. |
| `conversation_threads` | [List Threads](https://developer.helpscout.com/mailbox-api/endpoints/conversations/threads/list/) | Child stream of `conversations`. On incremental syncs, the connector reads threads only for conversations modified since the last sync and emits threads created after the saved cursor. |
| `customers` | [List Customers](https://developer.helpscout.com/mailbox-api/endpoints/customers/list/) | Incremental syncs request customers modified since the last sync. |
| `inboxes` | [List Inboxes](https://developer.helpscout.com/mailbox-api/endpoints/inboxes/list/) | Help Scout's API calls inboxes "mailboxes." |
| `inbox_custom_fields` | [List Inbox Custom Fields](https://developer.helpscout.com/mailbox-api/endpoints/inboxes/inbox-fields/) | Child stream of `inboxes`. |
| `inbox_folders` | [List Inbox Folders](https://developer.helpscout.com/mailbox-api/endpoints/inboxes/inbox-folders/) | Child stream of `inboxes`. |
| `users` | [List Users](https://developer.helpscout.com/mailbox-api/endpoints/users/list/) | |
| `workflows` | [List Workflows](https://developer.helpscout.com/mailbox-api/endpoints/workflows/list/) | |
| `tags` | [List Tags](https://developer.helpscout.com/mailbox-api/endpoints/tags/list/) | |
| `teams` | [List Teams](https://developer.helpscout.com/mailbox-api/endpoints/teams/list-teams/) | |
| `team_members` | [List Team Members](https://developer.helpscout.com/mailbox-api/endpoints/teams/list-team-members/) | Child stream of `teams`. |

Child streams make one request per parent record. For example, `conversation_threads` makes at least one request for every conversation it reads.

## Limitations and troubleshooting

### Rate limits

Help Scout [rate limits](https://developer.helpscout.com/mailbox-api/overview/rate-limiting/) the Inbox API per account, and the limit depends on your Help Scout plan. All users and integrations on the same account share that limit. When the limit is reached, Help Scout returns HTTP `429` and the connector waits and retries.

Because `conversation_threads` makes a request for each conversation, the first sync of an account with many conversations can take a long time. To reduce the number of requests, set a recent **Start date** or deselect streams you don't need.

### `401 Unauthorized` errors

Help Scout returns `401` if the application ID or secret is incorrect, or if the user who created the app is no longer an active user in the Help Scout account. Check the credentials, or create a new app as an active user.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request                                         | Subject        |
|------------------|-------------------|------------------------------------------------------|----------------|
| 0.0.57 | 2026-10-13 | [88647](https://github.com/airbytehq/airbyte/pull/88647) | Update dependencies |
| 0.0.56 | 2026-10-06 | [87909](https://github.com/airbytehq/airbyte/pull/87909) | Update dependencies |
| 0.0.55 | 2026-09-29 | [87231](https://github.com/airbytehq/airbyte/pull/87231) | Update dependencies |
| 0.0.54 | 2026-09-22 | [86669](https://github.com/airbytehq/airbyte/pull/86669) | Update dependencies |
| 0.0.53 | 2026-09-15 | [86077](https://github.com/airbytehq/airbyte/pull/86077) | Update dependencies |
| 0.0.52 | 2026-09-08 | [85515](https://github.com/airbytehq/airbyte/pull/85515) | Update dependencies |
| 0.0.51 | 2026-08-18 | [84642](https://github.com/airbytehq/airbyte/pull/84642) | Update dependencies |
| 0.0.50 | 2026-08-11 | [83981](https://github.com/airbytehq/airbyte/pull/83981) | Update dependencies |
| 0.0.49 | 2026-08-04 | [83505](https://github.com/airbytehq/airbyte/pull/83505) | Update dependencies |
| 0.0.48 | 2026-07-28 | [82462](https://github.com/airbytehq/airbyte/pull/82462) | Update dependencies |
| 0.0.47 | 2026-07-14 | [81867](https://github.com/airbytehq/airbyte/pull/81867) | Update dependencies |
| 0.0.46 | 2026-06-30 | [80494](https://github.com/airbytehq/airbyte/pull/80494) | Update dependencies |
| 0.0.45 | 2026-06-16 | [79901](https://github.com/airbytehq/airbyte/pull/79901) | Update dependencies |
| 0.0.44 | 2026-06-09 | [79350](https://github.com/airbytehq/airbyte/pull/79350) | Update dependencies |
| 0.0.43 | 2026-06-02 | [78767](https://github.com/airbytehq/airbyte/pull/78767) | Update dependencies |
| 0.0.42 | 2026-04-28 | [77284](https://github.com/airbytehq/airbyte/pull/77284) | Update dependencies |
| 0.0.41 | 2026-04-21 | [76635](https://github.com/airbytehq/airbyte/pull/76635) | Update dependencies |
| 0.0.40 | 2026-03-31 | [75736](https://github.com/airbytehq/airbyte/pull/75736) | Update dependencies |
| 0.0.39 | 2026-03-24 | [74927](https://github.com/airbytehq/airbyte/pull/74927) | Update dependencies |
| 0.0.38 | 2026-03-10 | [74681](https://github.com/airbytehq/airbyte/pull/74681) | Update dependencies |
| 0.0.37 | 2026-02-24 | [73934](https://github.com/airbytehq/airbyte/pull/73934) | Update dependencies |
| 0.0.36 | 2026-01-20 | [71899](https://github.com/airbytehq/airbyte/pull/71899) | Update dependencies |
| 0.0.35 | 2026-01-14 | [71694](https://github.com/airbytehq/airbyte/pull/71694) | Update dependencies |
| 0.0.34 | 2025-12-18 | [70489](https://github.com/airbytehq/airbyte/pull/70489) | Update dependencies |
| 0.0.33 | 2025-11-25 | [70020](https://github.com/airbytehq/airbyte/pull/70020) | Update dependencies |
| 0.0.32 | 2025-11-18 | [69407](https://github.com/airbytehq/airbyte/pull/69407) | Update dependencies |
| 0.0.31 | 2025-10-29 | [68833](https://github.com/airbytehq/airbyte/pull/68833) | Update dependencies |
| 0.0.30 | 2025-10-21 | [68275](https://github.com/airbytehq/airbyte/pull/68275) | Update dependencies |
| 0.0.29 | 2025-10-14 | [67864](https://github.com/airbytehq/airbyte/pull/67864) | Update dependencies |
| 0.0.28 | 2025-10-07 | [67411](https://github.com/airbytehq/airbyte/pull/67411) | Update dependencies |
| 0.0.27 | 2025-09-30 | [66405](https://github.com/airbytehq/airbyte/pull/66405) | Update dependencies |
| 0.0.26 | 2025-09-09 | [66051](https://github.com/airbytehq/airbyte/pull/66051) | Update dependencies |
| 0.0.25 | 2025-08-23 | [65325](https://github.com/airbytehq/airbyte/pull/65325) | Update dependencies |
| 0.0.24 | 2025-08-09 | [64638](https://github.com/airbytehq/airbyte/pull/64638) | Update dependencies |
| 0.0.23 | 2025-08-02 | [64208](https://github.com/airbytehq/airbyte/pull/64208) | Update dependencies |
| 0.0.22 | 2025-07-19 | [63507](https://github.com/airbytehq/airbyte/pull/63507) | Update dependencies |
| 0.0.21 | 2025-07-12 | [63130](https://github.com/airbytehq/airbyte/pull/63130) | Update dependencies |
| 0.0.20 | 2025-07-05 | [62629](https://github.com/airbytehq/airbyte/pull/62629) | Update dependencies |
| 0.0.19 | 2025-06-28 | [62176](https://github.com/airbytehq/airbyte/pull/62176) | Update dependencies |
| 0.0.18 | 2025-06-21 | [61785](https://github.com/airbytehq/airbyte/pull/61785) | Update dependencies |
| 0.0.17 | 2025-06-14 | [61112](https://github.com/airbytehq/airbyte/pull/61112) | Update dependencies |
| 0.0.16 | 2025-05-24 | [60715](https://github.com/airbytehq/airbyte/pull/60715) | Update dependencies |
| 0.0.15 | 2025-05-10 | [59823](https://github.com/airbytehq/airbyte/pull/59823) | Update dependencies |
| 0.0.14 | 2025-05-03 | [59228](https://github.com/airbytehq/airbyte/pull/59228) | Update dependencies |
| 0.0.13 | 2025-04-26 | [58797](https://github.com/airbytehq/airbyte/pull/58797) | Update dependencies |
| 0.0.12 | 2025-04-19 | [58214](https://github.com/airbytehq/airbyte/pull/58214) | Update dependencies |
| 0.0.11 | 2025-04-12 | [57681](https://github.com/airbytehq/airbyte/pull/57681) | Update dependencies |
| 0.0.10 | 2025-04-05 | [57031](https://github.com/airbytehq/airbyte/pull/57031) | Update dependencies |
| 0.0.9 | 2025-03-29 | [56669](https://github.com/airbytehq/airbyte/pull/56669) | Update dependencies |
| 0.0.8 | 2025-03-22 | [56000](https://github.com/airbytehq/airbyte/pull/56000) | Update dependencies |
| 0.0.7 | 2025-03-08 | [55474](https://github.com/airbytehq/airbyte/pull/55474) | Update dependencies |
| 0.0.6 | 2025-03-01 | [54798](https://github.com/airbytehq/airbyte/pull/54798) | Update dependencies |
| 0.0.5 | 2025-02-22 | [54330](https://github.com/airbytehq/airbyte/pull/54330) | Update dependencies |
| 0.0.4 | 2025-02-15 | [53833](https://github.com/airbytehq/airbyte/pull/53833) | Update dependencies |
| 0.0.3 | 2025-02-08 | [53281](https://github.com/airbytehq/airbyte/pull/53281) | Update dependencies |
| 0.0.2 | 2025-02-01 | [52784](https://github.com/airbytehq/airbyte/pull/52784) | Update dependencies |
| 0.0.1 | 2025-01-28 | [52614](https://github.com/airbytehq/airbyte/pull/52614) | Initial release by [@pabloescoder](https://github.com/pabloescoder) via Connector Builder |

</details>
