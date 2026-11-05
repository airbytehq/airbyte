# Zendesk Chat

This page contains the setup guide and reference information for the Zendesk Chat source connector.

:::warning Zendesk ends incremental exports for third-party integrations (notice dated 2026-11-03)
Zendesk [stops serving its Incremental Exports API to third-party integrations](https://support.zendesk.com/hc/en-us/articles/11275429993498) such as Airbyte between December 2, 2026 and January 19, 2027. Blocked requests return HTTP 403.

- The `chats` stream no longer uses incremental exports as of connector version 2.0.0 and keeps working. See the [migration guide](zendesk-chat-migrations.md#upgrading-to-200).
- The `agent_timeline` stream has no replacement endpoint and still reads the incremental export. Zendesk has not said whether agent timeline exports are included in the shutdown. If the stream fails with a 403 error, request the 60-day partner extension in Zendesk Admin Center under **Apps and integrations > APIs > API configuration**, or deselect the stream.
:::

## Prerequisites

- A Zendesk account with the [Chat module](https://www.zendesk.com/chat/) enabled.
- Your Zendesk [subdomain](https://support.zendesk.com/hc/en-us/articles/4409381383578-Where-can-I-find-my-Zendesk-subdomain-).
<!-- env:oss -->
- (Airbyte Open Source) An access token. See [OAuth Authentication](https://developer.zendesk.com/documentation/live-chat/getting-started/auth/) for details. We recommend creating a restricted, read-only token specifically for Airbyte access.
<!-- /env:oss -->

## Setup guide

<!-- env:cloud -->

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Zendesk Chat** from the Source type dropdown.
4. Enter the name for the Zendesk Chat connector.
5. For **Subdomain**, enter your [Zendesk subdomain](https://support.zendesk.com/hc/en-us/articles/4409381383578-Where-can-I-find-my-Zendesk-subdomain-) (for example, if your Zendesk URL is `https://mycompany.zendesk.com`, enter `mycompany`).
6. For **Start Date**, enter the date in `YYYY-MM-DDTHH:mm:ssZ` format. The data added on and after this date will be replicated.
7. Click **Authenticate your Zendesk Chat account**. Log in and authorize your Zendesk Chat account. The OAuth flow requests `read` and `chat` scopes.
8. Click **Set up source**.
<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

1. Navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Zendesk Chat** from the Source type dropdown.
4. Enter the name for the Zendesk Chat connector.
5. For **Subdomain**, enter your [Zendesk subdomain](https://support.zendesk.com/hc/en-us/articles/4409381383578-Where-can-I-find-my-Zendesk-subdomain-) (for example, if your Zendesk URL is `https://mycompany.zendesk.com`, enter `mycompany`).
6. For **Start Date**, enter the date in `YYYY-MM-DDTHH:mm:ssZ` format. The data added on and after this date will be replicated.
7. For **Authorization Method**, select **Access Token** from the dropdown and enter your Zendesk [access token](https://developer.zendesk.com/documentation/live-chat/getting-started/auth/). The token must have the `read` and `chat` scopes.
8. Click **Set up source**.
<!-- /env:oss -->

## Supported sync modes

The Zendesk Chat source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Supported Streams

- [Accounts](https://developer.zendesk.com/api-reference/live-chat/chat-api/accounts/#show-account)
- [Agents](https://developer.zendesk.com/api-reference/live-chat/chat-api/agents/#list-agents) \(Incremental\)
- [Agent Timelines](https://developer.zendesk.com/api-reference/live-chat/chat-api/incremental_export/#incremental-agent-timeline-export) \(Incremental\). Still read from the incremental export; see the notice at the top of this page.
- [Chats](https://developer.zendesk.com/api-reference/live-chat/chat-api/chats/#list-chats) \(Incremental\). Chats are found with [Search Chats](https://developer.zendesk.com/api-reference/live-chat/chat-api/chats/#search-chats) in one-day windows of their last update time, then fetched in full 50 chats per request. The cursor field is `timestamp`. The fields `deleted`, `update_timestamp` and `engagements` are not available from these endpoints, and deleted chats are not reported.
- [Shortcuts](https://developer.zendesk.com/api-reference/live-chat/chat-api/shortcuts/#list-shortcuts)
- [Triggers](https://developer.zendesk.com/api-reference/live-chat/chat-api/triggers/#list-triggers)
- [Bans](https://developer.zendesk.com/api-reference/live-chat/chat-api/bans/#list-bans) \(Incremental\)
- [Departments](https://developer.zendesk.com/api-reference/live-chat/chat-api/departments/#list-departments)
- [Goals](https://developer.zendesk.com/api-reference/live-chat/chat-api/goals/#list-goals)
- [Skills](https://developer.zendesk.com/api-reference/live-chat/chat-api/skills/#list-skills)
- [Roles](https://developer.zendesk.com/api-reference/live-chat/chat-api/roles/#list-roles)
- [Routing Settings](https://developer.zendesk.com/api-reference/live-chat/chat-api/routing_settings/#show-account-routing-settings)

## Performance considerations

The Zendesk Chat API enforces a rate limit of [200 requests per minute](https://developer.zendesk.com/api-reference/live-chat/introduction/) per endpoint. The connector handles rate limiting automatically by respecting the `Retry-After` header when a 429 response is returned.

Each sync of the `chats` stream sends one search request per 30-day window between the stream's cursor (minus a one-day lookback) or the configured start date and now, plus one extra request per 40 results in a window, plus one request per 50 chats found. The first sync of an account with a start date several years back therefore sends a few dozen search requests (about 75 for six years) before the chats themselves, with records arriving in batches of 50 as chats are found, and an account without new chats repeats one search per 30 days of range since its newest chat on every sync. Because of the one-day lookback, every sync also sends again the chats that were updated during the day before the stream's cursor; these repeats are deduplicated by the primary key in destinations that deduplicate, and arrive as additional rows in destinations that append. The rate limit applies to each endpoint and is shared with every other integration that calls the same endpoints, so these searches can slow down other integrations while the sync runs. Zendesk returns at most 10,000 results per search; when a window holds more updated chats than that, the connector splits it into shorter windows until each one fits.

## Troubleshooting

### Zendesk Chat access token is invalid, expired, or missing the required read and chat scopes

Zendesk Chat returned a `401 Unauthorized` response, so the connector stops the sync and reports a configuration error. To resolve it:

- **Airbyte Cloud**: Edit the source and click **Authenticate your Zendesk Chat account** to re-authorize the connection.
- **Airbyte Open Source**: Generate a new [access token](https://developer.zendesk.com/documentation/live-chat/getting-started/auth/) with the `read` and `chat` scopes and update the **Access Token** field.

### Requests that return 404

When Zendesk Chat returns a `404 Not Found` response to any request, the connector ignores that response and continues the sync instead of failing. No records from that request are emitted. This most often happens when a record has been deleted, but it applies to every stream and every request, so a 404 on a list request drops that page of results.

### Zendesk rejected the incremental export request for stream agent_timeline with HTTP 403

Zendesk [is withdrawing incremental exports from third-party integrations](https://support.zendesk.com/hc/en-us/articles/11275429993498) such as Airbyte, and the `agent_timeline` stream has no other endpoint to read from. The export also requires the authorizing user to have the Owner or Administrator role, so a 403 can also mean that the user who authorized Airbyte lost that role. Request the 60-day partner extension in Zendesk Admin Center under **Apps and integrations > APIs > API configuration**, check the role of the authorizing user, or deselect the `agent_timeline` stream in the connection.

### Zendesk returns at most 10,000 chats per search

The `chats` stream finds chats with the Search Chats endpoint 30 days at a time, and Zendesk returns at most 10,000 results per search. When a window holds 10,000 or more updated chats, the connector splits it into shorter windows (down to about 42 minutes) until each one fits, so the sync continues. The sync only fails with this message when 10,000 or more chats were updated within one such short window, which cannot be read completely. Contact Airbyte support if you hit this limit.

## Data type map

| Integration Type | Airbyte Type |
| :--------------- | :----------- |
| `string`         | `string`     |
| `number`         | `number`     |
| `array`          | `array`      |
| `object`         | `object`     |

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                                                                |
|:--------|:-----------|:---------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 2.0.0 | 2026-11-03 | [90874](https://github.com/airbytehq/airbyte/pull/90874) | Breaking: read `chats` through Search Chats and List Chats instead of the incremental export Zendesk ends for third-party integrations on 2026-12-02; cursor becomes `timestamp` with state migration; drop `deleted`, `update_timestamp` and `engagements` from the `chats` schema; report a configuration error when the incremental export behind `agent_timeline` returns 403 |
| 1.3.33 | 2026-11-03 | [90807](https://github.com/airbytehq/airbyte/pull/90807) | Update dependencies |
| 1.3.32 | 2026-10-27 | [90082](https://github.com/airbytehq/airbyte/pull/90082) | Update dependencies |
| 1.3.31 | 2026-10-20 | [89485](https://github.com/airbytehq/airbyte/pull/89485) | Update dependencies |
| 1.3.30 | 2026-10-13 | [88886](https://github.com/airbytehq/airbyte/pull/88886) | Update dependencies |
| 1.3.29 | 2026-10-06 | [88112](https://github.com/airbytehq/airbyte/pull/88112) | Update dependencies |
| 1.3.28 | 2026-09-29 | [87433](https://github.com/airbytehq/airbyte/pull/87433) | Update dependencies |
| 1.3.27 | 2026-09-22 | [86888](https://github.com/airbytehq/airbyte/pull/86888) | Update dependencies |
| 1.3.26 | 2026-09-16 | [83336](https://github.com/airbytehq/airbyte/pull/83336) | Show a clearer error when Zendesk Chat rejects the access token |
| 1.3.25 | 2026-09-15 | [86312](https://github.com/airbytehq/airbyte/pull/86312) | Update dependencies |
| 1.3.24 | 2026-09-08 | [85714](https://github.com/airbytehq/airbyte/pull/85714) | Update dependencies |
| 1.3.23 | 2026-08-18 | [84835](https://github.com/airbytehq/airbyte/pull/84835) | Update dependencies |
| 1.3.22 | 2026-08-11 | [84170](https://github.com/airbytehq/airbyte/pull/84170) | Update dependencies |
| 1.3.21 | 2026-07-28 | [83194](https://github.com/airbytehq/airbyte/pull/83194) | Update to CDK 7.23.8 (fixes AirbyteCustomCodeNotPermittedError for bundled custom components) and remove the temporary Cloud version override |
| 1.3.20 | 2026-07-28 | [1082](https://github.com/airbytehq/airbyte-python-cdk/issues/1082) | Roll Cloud back to 1.3.18 — 1.3.19 is built on SDM 7.23.7, which breaks bundled custom components |
| 1.3.19 | 2026-07-28 | [83161](https://github.com/airbytehq/airbyte/pull/83161) | Update dependencies |
| 1.3.18 | 2026-07-21 | [82671](https://github.com/airbytehq/airbyte/pull/82671) | Update dependencies |
| 1.3.17 | 2026-07-14 | [82082](https://github.com/airbytehq/airbyte/pull/82082) | Update dependencies |
| 1.3.16 | 2026-06-30 | [81327](https://github.com/airbytehq/airbyte/pull/81327) | Update dependencies |
| 1.3.15 | 2026-06-23 | [80709](https://github.com/airbytehq/airbyte/pull/80709) | Update dependencies |
| 1.3.14 | 2026-06-16 | [80102](https://github.com/airbytehq/airbyte/pull/80102) | Update dependencies |
| 1.3.13 | 2026-06-09 | [79569](https://github.com/airbytehq/airbyte/pull/79569) | Update dependencies |
| 1.3.12 | 2026-06-02 | [79069](https://github.com/airbytehq/airbyte/pull/79069) | Update dependencies |
| 1.3.11 | 2026-04-28 | [77490](https://github.com/airbytehq/airbyte/pull/77490) | Update dependencies |
| 1.3.10 | 2026-04-21 | [76846](https://github.com/airbytehq/airbyte/pull/76846) | Bump SDM base image to stable 7.17.2 |
| 1.3.9 | 2026-03-31 | [75942](https://github.com/airbytehq/airbyte/pull/75942) | Bump SDM base image for memory monitor (CDK PR #962) |
| 1.3.8 | 2026-03-31 | [75858](https://github.com/airbytehq/airbyte/pull/75858) | Update dependencies |
| 1.3.7 | 2026-03-17 | [74324](https://github.com/airbytehq/airbyte/pull/74324) | Migrate to scopes object array format |
| 1.3.6 | 2026-03-17 | [75116](https://github.com/airbytehq/airbyte/pull/75116) | Update dependencies |
| 1.3.5 | 2026-03-10 | [74671](https://github.com/airbytehq/airbyte/pull/74671) | Update dependencies |
| 1.3.4 | 2026-03-03 | [74156](https://github.com/airbytehq/airbyte/pull/74156) | Update dependencies |
| 1.3.3 | 2026-02-17 | [73534](https://github.com/airbytehq/airbyte/pull/73534) | Update dependencies |
| 1.3.2 | 2026-02-10 | [73151](https://github.com/airbytehq/airbyte/pull/73151) | Update dependencies |
| 1.3.1 | 2026-02-03 | [72611](https://github.com/airbytehq/airbyte/pull/72611) | Update dependencies |
| 1.3.0 | 2026-01-28 | [71829](https://github.com/airbytehq/airbyte/pull/71829) | Add OAuth2.0 support for Airbyte Cloud |
| 1.2.31 | 2026-01-20 | [72091](https://github.com/airbytehq/airbyte/pull/72091) | Update dependencies |
| 1.2.30 | 2026-01-14 | [71701](https://github.com/airbytehq/airbyte/pull/71701) | Update dependencies |
| 1.2.29 | 2025-12-18 | [70681](https://github.com/airbytehq/airbyte/pull/70681) | Update dependencies |
| 1.2.28 | 2025-11-25 | [70128](https://github.com/airbytehq/airbyte/pull/70128) | Update dependencies |
| 1.2.27 | 2025-11-18 | [69513](https://github.com/airbytehq/airbyte/pull/69513) | Update dependencies |
| 1.2.26 | 2025-10-29 | [68958](https://github.com/airbytehq/airbyte/pull/68958) | Update dependencies |
| 1.2.25 | 2025-10-27 | [68629](https://github.com/airbytehq/airbyte/pull/68629) | Fix Pagination for `chats` and `agent_timeline` streams |
| 1.2.24 | 2025-10-22 | [68591](https://github.com/airbytehq/airbyte/pull/68591) | Add `suggestedStreams` |
| 1.2.23 | 2025-10-22 | [67607](https://github.com/airbytehq/airbyte/pull/67607) | Handle 404 errors for deleted records in all streams |
| 1.2.22 | 2025-10-21 | [68440](https://github.com/airbytehq/airbyte/pull/68440) | Update dependencies |
| 1.2.21 | 2025-10-14 | [68020](https://github.com/airbytehq/airbyte/pull/68020) | Update dependencies |
| 1.2.20 | 2025-10-07 | [67238](https://github.com/airbytehq/airbyte/pull/67238) | Update dependencies |
| 1.2.19 | 2025-09-30 | [66845](https://github.com/airbytehq/airbyte/pull/66845) | Update dependencies |
| 1.2.18 | 2025-09-24 | [66459](https://github.com/airbytehq/airbyte/pull/66459) | Update dependencies |
| 1.2.17 | 2025-09-09 | [65491](https://github.com/airbytehq/airbyte/pull/65491) | Update dependencies |
| 1.2.16 | 2025-08-10 | [64864](https://github.com/airbytehq/airbyte/pull/64864) | Update dependencies |
| 1.2.15 | 2025-08-02 | [64305](https://github.com/airbytehq/airbyte/pull/64305) | Update dependencies |
| 1.2.14 | 2025-07-26 | [64053](https://github.com/airbytehq/airbyte/pull/64053) | Update dependencies |
| 1.2.13 | 2025-07-20 | [63650](https://github.com/airbytehq/airbyte/pull/63650) | Update dependencies |
| 1.2.12 | 2025-07-12 | [63177](https://github.com/airbytehq/airbyte/pull/63177) | Update dependencies |
| 1.2.11 | 2025-07-05 | [62677](https://github.com/airbytehq/airbyte/pull/62677) | Update dependencies |
| 1.2.10 | 2025-06-28 | [62247](https://github.com/airbytehq/airbyte/pull/62247) | Update dependencies |
| 1.2.9 | 2025-06-21 | [61751](https://github.com/airbytehq/airbyte/pull/61751) | Update dependencies |
| 1.2.8 | 2025-06-15 | [61248](https://github.com/airbytehq/airbyte/pull/61248) | Update dependencies |
| 1.2.7 | 2025-05-24 | [60782](https://github.com/airbytehq/airbyte/pull/60782) | Update dependencies |
| 1.2.6 | 2025-05-10 | [59993](https://github.com/airbytehq/airbyte/pull/59993) | Update dependencies |
| 1.2.5 | 2025-05-04 | [58949](https://github.com/airbytehq/airbyte/pull/58949) | Update dependencies |
| 1.2.4 | 2025-04-19 | [58028](https://github.com/airbytehq/airbyte/pull/58028) | Update dependencies |
| 1.2.3 | 2025-04-05 | [57404](https://github.com/airbytehq/airbyte/pull/57404) | Update dependencies |
| 1.2.2 | 2025-03-29 | [56850](https://github.com/airbytehq/airbyte/pull/56850) | Update dependencies |
| 1.2.1 | 2025-03-22 | [56345](https://github.com/airbytehq/airbyte/pull/56345) | Update dependencies |
| 1.2.0 | 2025-03-10 | [47319](https://github.com/airbytehq/airbyte/pull/47319) | Migrate to Manifest-only |
| 1.1.1 | 2025-03-09 | [54110](https://github.com/airbytehq/airbyte/pull/54110) | Update dependencies |
| 1.1.0 | 2025-03-03 | [54151](https://github.com/airbytehq/airbyte/pull/54151) | Migrate to incrementalcursors |
| 1.0.4 | 2025-02-01 | [53081](https://github.com/airbytehq/airbyte/pull/53081) | Update dependencies |
| 1.0.3 | 2025-01-25 | [51942](https://github.com/airbytehq/airbyte/pull/51942) | Update dependencies |
| 1.0.2 | 2025-01-22 | [52065](https://github.com/airbytehq/airbyte/pull/52065) | Pinned `airbyte-cdk` version to `0.72.2` |
| 1.0.1 | 2025-01-11 | [43728](https://github.com/airbytehq/airbyte/pull/43728) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 1.0.0 | 2024-11-04 | [44898](https://github.com/airbytehq/airbyte/pull/44898) | Migrate to [new base url](https://developer.zendesk.com/api-reference/live-chat/introduction/) |
| 0.3.1 | 2024-06-06 | [39260](https://github.com/airbytehq/airbyte/pull/39260) | [autopull] Upgrade base image to v1.2.2 |
| 0.3.0 | 2024-03-07 | [35867](https://github.com/airbytehq/airbyte/pull/35867) | Migrated to `YamlDeclarativeSource (Low-code)` Airbyte CDK |
| 0.2.2 | 2024-02-12 | [35185](https://github.com/airbytehq/airbyte/pull/35185) | Manage dependencies with Poetry. |
| 0.2.1 | 2023-10-20 | [31643](https://github.com/airbytehq/airbyte/pull/31643) | Upgrade base image to airbyte/python-connector-base:1.1.0 |
| 0.2.0 | 2023-10-11 | [30526](https://github.com/airbytehq/airbyte/pull/30526) | Use the python connector base image, remove dockerfile and implement build_customization.py |
| 0.1.14 | 2023-02-10 | [24190](https://github.com/airbytehq/airbyte/pull/24190) | Fix remove too high min/max from account stream |
| 0.1.13 | 2023-02-10 | [22819](https://github.com/airbytehq/airbyte/pull/22819) | Specified date formatting in specification |
| 0.1.12 | 2023-01-27 | [22026](https://github.com/airbytehq/airbyte/pull/22026) | Set `AvailabilityStrategy` for streams explicitly to `None` |
| 0.1.11 | 2022-10-18 | [17745](https://github.com/airbytehq/airbyte/pull/17745) | Add Engagements Stream and fix infity looping |
| 0.1.10 | 2022-09-28 | [17326](https://github.com/airbytehq/airbyte/pull/17326) | Migrate to per-stream states. |
| 0.1.9 | 2022-08-23 | [15879](https://github.com/airbytehq/airbyte/pull/15879) | Corrected specification and stream schemas to support backward capability |
| 0.1.8 | 2022-06-28 | [13387](https://github.com/airbytehq/airbyte/pull/13387) | Add state checkpoint to allow long runs |
| 0.1.7 | 2022-05-25 | [12883](https://github.com/airbytehq/airbyte/pull/12883) | Pass timeout in request to prevent a stuck connection |
| 0.1.6 | 2021-12-15 | [7313](https://github.com/airbytehq/airbyte/pull/7313) | Add support of `OAuth 2.0` authentication. Fixed the issue with `created_at` can now be `null` for `bans` stream |
| 0.1.5 | 2021-12-06 | [8425](https://github.com/airbytehq/airbyte/pull/8425) | Update title, description fields in spec |
| 0.1.4 | 2021-11-22 | [8166](https://github.com/airbytehq/airbyte/pull/8166) | Make `Chats` stream incremental + add tests for all streams |
| 0.1.3 | 2021-10-21 | [7210](https://github.com/airbytehq/airbyte/pull/7210) | Chats stream is only getting data from first page |
| 0.1.2 | 2021-08-17 | [5476](https://github.com/airbytehq/airbyte/pull/5476) | Correct field unread to boolean type |
| 0.1.1 | 2021-06-09 | [3973](https://github.com/airbytehq/airbyte/pull/3973) | Add `AIRBYTE_ENTRYPOINT` for Kubernetes support |
| 0.1.0 | 2021-05-03 | [3088](https://github.com/airbytehq/airbyte/pull/3088) | Initial release |

</details>
