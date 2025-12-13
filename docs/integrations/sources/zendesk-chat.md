# Zendesk Chat

This page contains the setup guide and reference information for the Zendesk Chat source connector.

## Prerequisites

- A Zendesk Account with permission to access data from accounts you want to sync.
<!-- env:oss -->
- (Airbyte Open Source) An Access Token (https://developer.zendesk.com/rest_api/docs/chat/auth). We recommend creating a restricted, read-only key specifically for Airbyte access to allow you to control which resources Airbyte should be able to access.
<!-- /env:oss -->

## Setup guide

<!-- env:cloud -->

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Zendesk Chat** from the Source type dropdown.
4. Enter the name for the Zendesk Chat connector.
5. If you access Zendesk Chat from a [Zendesk subdomain](https://support.zendesk.com/hc/en-us/articles/4409381383578-Where-can-I-find-my-Zendesk-subdomain-), enter the **Subdomain**.
6. For **Start Date**, enter the date in `YYYY-MM-DDTHH:mm:ssZ` format. The data added on and after this date will be replicated.
7. Click **Authenticate your Zendesk Chat account**. Log in and authorize your Zendesk Chat account.
8. Click **Set up source**.
<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

1. Navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Zendesk Chat** from the Source type dropdown.
4. Enter the name for the Zendesk Chat connector.
5. If you access Zendesk Chat from a [Zendesk subdomain](https://support.zendesk.com/hc/en-us/articles/4409381383578-Where-can-I-find-my-Zendesk-subdomain-), enter the **Subdomain**.
6. For **Start Date**, enter the date in `YYYY-MM-DDTHH:mm:ssZ` format. The data added on and after this date will be replicated.
7. For Authorization Method, select **Access Token** from the dropdown and enter your Zendesk [access token](https://developer.zendesk.com/rest_api/docs/chat/auth).
8. Click **Set up source**.
<!-- /env:oss -->

## Supported sync modes

The Zendesk Chat source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Supported Streams

- [Accounts](https://developer.zendesk.com/rest_api/docs/chat/accounts#show-account)
- [Agents](https://developer.zendesk.com/rest_api/docs/chat/agents#list-agents) \(Incremental\)
- [Agent Timelines](https://developer.zendesk.com/rest_api/docs/chat/incremental_export#incremental-agent-timeline-export) \(Incremental\)
- [Chats](https://developer.zendesk.com/rest_api/docs/chat/chats#list-chats)
- [Shortcuts](https://developer.zendesk.com/rest_api/docs/chat/shortcuts#list-shortcuts)
- [Triggers](https://developer.zendesk.com/rest_api/docs/chat/triggers#list-triggers)
- [Bans](https://developer.zendesk.com/rest_api/docs/chat/bans#list-bans) \(Incremental\)
- [Departments](https://developer.zendesk.com/rest_api/docs/chat/departments#list-departments)
- [Goals](https://developer.zendesk.com/rest_api/docs/chat/goals#list-goals)
- [Skills](https://developer.zendesk.com/rest_api/docs/chat/skills#list-skills)
- [Roles](https://developer.zendesk.com/rest_api/docs/chat/roles#list-roles)
- [Routing Settings](https://developer.zendesk.com/rest_api/docs/chat/routing_settings#show-account-routing-settings)

## Performance considerations

The connector is restricted by Zendesk's [requests limitation](https://developer.zendesk.com/rest_api/docs/voice-api/introduction#rate-limits).

## Data type map

| Integration Type | Airbyte Type |
| :--------------- | :----------- |
| `string`         | `string`     |
| `number`         | `number`     |
| `array`          | `array`      |
| `object`         | `object`     |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                                                                |
|:--------|:-----------|:---------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1.2.29 | 2025-12-09 | [70681](https://github.com/airbytehq/airbyte/pull/70681) | Update dependencies |
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
| 1.2.16 | 2025-08-09 | [64864](https://github.com/airbytehq/airbyte/pull/64864) | Update dependencies |
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
