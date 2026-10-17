# PostHog

This page contains the setup guide and reference information for the [PostHog](https://posthog.com/) source connector.

## Prerequisites

- A PostHog account on PostHog Cloud (US or EU) or a self-hosted PostHog instance.
- A [personal API key](https://posthog.com/docs/api/personal-api-keys) with the following read scopes:

  | Scope | Used by stream |
  | :---- | :------------- |
  | `project:read` | `projects`, and to list the projects that every other stream reads from |
  | `annotation:read` | `annotations` |
  | `cohort:read` | `cohorts` |
  | `feature_flag:read` | `feature_flags` |
  | `insight:read` | `insights` |
  | `person:read` | `persons` |
  | `query:read` | `events` |

  If you only plan to sync some streams, you can omit the scopes for the streams you don't use, but `project:read` is always required. The connector uses the `projects` stream to check the connection.

## Setup guide

### Step 1: Create a PostHog personal API key

1. In PostHog, go to the **Personal API keys** section of your account settings.
2. Click **+ Create a personal API key** and give the key a label.
3. Select the read scopes listed in [Prerequisites](#prerequisites).
4. Copy the key value immediately. PostHog doesn't show it again after you refresh the page.

For more details, see PostHog's [personal API keys documentation](https://posthog.com/docs/api/personal-api-keys).

### Step 2: Set up the PostHog connector in Airbyte

1. In Airbyte, go to **Sources** and click **+ New source**.
2. Select **PostHog** from the list of sources.
3. Enter a name for the source.
4. For **API Key**, enter the personal API key you created in Step 1.
5. For **Start Date**, enter the UTC date and time in the format `YYYY-MM-DDTHH:mm:ssZ`, for example `2021-01-01T00:00:00Z`. The connector only uses this value for the `events` stream. It doesn't sync events with a timestamp earlier than this date. Other streams always sync all records.
6. (Optional) For **Base URL**, enter the URL of your PostHog instance. The default is `https://app.posthog.com`. If your project is on PostHog EU Cloud, enter `https://eu.posthog.com`. If you self-host PostHog, enter your instance's domain, for example `https://posthog.example.com`. Don't include the `/api` path, because the connector adds it.
7. (Optional) For **Events stream slice step size (in days)**, enter the number of days of events the connector requests in each time window. The default is `30`, and the allowed range is `1` to `91`. Lower this value if syncs of the `events` stream fail or run for a long time. See [Limitations](#limitations).
8. Click **Set up source**.

## Supported sync modes

| Feature | Supported |
| :------ | :-------- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes, `events` stream only |

## Supported streams

The `projects` stream lists your PostHog projects. Every other stream reads its data separately for each of those projects.

| Stream | PostHog API endpoint | Sync modes |
| :----- | :------------------- | :--------- |
| `projects` | [Projects](https://posthog.com/docs/api/projects) | Full Refresh |
| `annotations` | [Annotations](https://posthog.com/docs/api/annotations) | Full Refresh |
| `cohorts` | [Cohorts](https://posthog.com/docs/api/cohorts) | Full Refresh |
| `events` | [Events](https://posthog.com/docs/api/events) | Full Refresh, Incremental |
| `feature_flags` | [Feature flags](https://posthog.com/docs/api/feature-flags) | Full Refresh |
| `insights` | [Insights](https://posthog.com/docs/api/insights) | Full Refresh |
| `persons` | [Persons](https://posthog.com/docs/api/persons) | Full Refresh |

### Incremental sync for the events stream

The `events` stream uses the event `timestamp` field as its cursor. The connector stores a separate cursor value for each project, so a project added after your last sync starts from the configured start date while existing projects continue from where they left off. Within each project, the connector requests events in time windows sized by the **Events stream slice step size** setting.

## Limitations

### The PostHog events API is deprecated

PostHog has [deprecated the events API](https://posthog.com/docs/api/events) that the `events` stream uses and plans to remove it at a future date. PostHog currently applies these restrictions to that API:

- Pagination offsets larger than 50,000 are disabled. The connector pages through each time window using offsets, so a single project and time window that contains more events than this allows can cause the sync to fail. If this happens, lower the **Events stream slice step size** setting so each window contains fewer events.
- The range between the `after` and `before` parameters must be less than one year. The connector's maximum step size of 91 days stays within this limit.

For large or recurring event exports, PostHog recommends [batch exports](https://posthog.com/docs/cdp/batch-exports) instead of the events API.

### Rate limiting

PostHog rate limits its private API endpoints, which are the endpoints this connector reads from. At the time of writing, PostHog documents these limits:

- Analytics endpoints, such as retrieving persons: 240 requests per minute and 1,200 requests per hour.
- Other read endpoints: 480 requests per minute and 4,800 requests per hour.

For current limits and details on how PostHog counts requests, see PostHog's [rate limiting documentation](https://posthog.com/docs/api#rate-limiting).

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                 |
| :------ | :--------- | :------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------- |
| 1.1.26 | 2026-10-16 | [88960](https://github.com/airbytehq/airbyte/pull/88960) | Update to CDK v7 and base image 4.1.1 |
| 1.1.25 | 2025-02-01 | [53032](https://github.com/airbytehq/airbyte/pull/53032) | Update dependencies |
| 1.1.24 | 2025-01-25 | [52536](https://github.com/airbytehq/airbyte/pull/52536) | Update dependencies |
| 1.1.23 | 2025-01-18 | [51856](https://github.com/airbytehq/airbyte/pull/51856) | Update dependencies |
| 1.1.22 | 2025-01-11 | [51313](https://github.com/airbytehq/airbyte/pull/51313) | Update dependencies |
| 1.1.21 | 2024-12-28 | [50685](https://github.com/airbytehq/airbyte/pull/50685) | Update dependencies |
| 1.1.20 | 2024-12-21 | [50280](https://github.com/airbytehq/airbyte/pull/50280) | Update dependencies |
| 1.1.19 | 2024-12-14 | [49716](https://github.com/airbytehq/airbyte/pull/49716) | Update dependencies |
| 1.1.18 | 2024-12-12 | [49066](https://github.com/airbytehq/airbyte/pull/49066) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 1.1.17 | 2024-10-29 | [47724](https://github.com/airbytehq/airbyte/pull/47724) | Update dependencies |
| 1.1.16 | 2024-10-28 | [47033](https://github.com/airbytehq/airbyte/pull/47033) | Update dependencies |
| 1.1.15 | 2024-10-12 | [46769](https://github.com/airbytehq/airbyte/pull/46769) | Update dependencies |
| 1.1.14 | 2024-10-05 | [46421](https://github.com/airbytehq/airbyte/pull/46421) | Update dependencies |
| 1.1.13 | 2024-09-28 | [46108](https://github.com/airbytehq/airbyte/pull/46108) | Update dependencies |
| 1.1.12 | 2024-09-21 | [45796](https://github.com/airbytehq/airbyte/pull/45796) | Update dependencies |
| 1.1.11 | 2024-09-14 | [45570](https://github.com/airbytehq/airbyte/pull/45570) | Update dependencies |
| 1.1.10 | 2024-09-07 | [45241](https://github.com/airbytehq/airbyte/pull/45241) | Update dependencies |
| 1.1.9 | 2024-08-31 | [44996](https://github.com/airbytehq/airbyte/pull/44996) | Update dependencies |
| 1.1.8 | 2024-08-24 | [44658](https://github.com/airbytehq/airbyte/pull/44658) | Update dependencies |
| 1.1.7 | 2024-08-17 | [44350](https://github.com/airbytehq/airbyte/pull/44350) | Update dependencies |
| 1.1.6 | 2024-08-13 | [44016](https://github.com/airbytehq/airbyte/pull/44016) | Fix `events` stream pagniator to workaround PostHog API issue [#13508](https://github.com/PostHog/posthog/issues/13508) |
| 1.1.5 | 2024-08-10 | [43488](https://github.com/airbytehq/airbyte/pull/43488) | Update dependencies |
| 1.1.4 | 2024-08-03 | [43232](https://github.com/airbytehq/airbyte/pull/43232) | Update dependencies |
| 1.1.3 | 2024-07-27 | [42769](https://github.com/airbytehq/airbyte/pull/42769) | Update dependencies |
| 1.1.2 | 2024-07-20 | [42151](https://github.com/airbytehq/airbyte/pull/42151) | Update dependencies |
| 1.1.1 | 2024-07-13 | [41823](https://github.com/airbytehq/airbyte/pull/41823) | Update dependencies |
| 1.1.0 | 2024-06-20 | [39763](https://github.com/airbytehq/airbyte/pull/39763) | Add `properties` and `uuid` attributes to persons stream |
| 1.0.0 | 2023-12-04 | [28593](https://github.com/airbytehq/airbyte/pull/28593) | Fix events.event type |
| 0.1.15 | 2023-10-28 | [31265](https://github.com/airbytehq/airbyte/pull/31265) | Fix Events stream datetime format |
| 0.1.14 | 2023-08-29 | [29947](https://github.com/airbytehq/airbyte/pull/29947) | Add optional field to spec: `events_time_step` |
| 0.1.13 | 2023-07-19 | [28461](https://github.com/airbytehq/airbyte/pull/28461) | Fixed EventsSimpleRetriever declaration |
| 0.1.12 | 2023-06-28 | [27764](https://github.com/airbytehq/airbyte/pull/27764) | Update following state breaking changes |
| 0.1.11 | 2023-06-09 | [27135](https://github.com/airbytehq/airbyte/pull/27135) | Fix custom EventsSimpleRetriever |
| 0.1.10 | 2023-04-15 | [24084](https://github.com/airbytehq/airbyte/pull/24084) | Increase `events` streams batch size |
| 0.1.9 | 2023-02-13 | [22906](https://github.com/airbytehq/airbyte/pull/22906) | Specified date formatting in specification |
| 0.1.8 | 2022-11-11 | [18993](https://github.com/airbytehq/airbyte/pull/18993) | connector migrated to low-code, added projects,insights streams, added project based slicing for all other streams |
| 0.1.7 | 2022-07-26 | [14585](https://github.com/airbytehq/airbyte/pull/14585) | Add missing 'properties' field to event attributes |
| 0.1.6 | 2022-01-20 | [8617](https://github.com/airbytehq/airbyte/pull/8617) | Update connector fields title/description |
| 0.1.5 | 2021-12-24 | [9082](https://github.com/airbytehq/airbyte/pull/9082) | Remove obsolete session_events and insights streams |
| 0.1.4 | 2021-09-14 | [6058](https://github.com/airbytehq/airbyte/pull/6058) | Support self-hosted posthog instances |
| 0.1.3 | 2021-07-20 | [4001](https://github.com/airbytehq/airbyte/pull/4001) | Incremental streams read only relevant pages |
| 0.1.2 | 2021-07-15 | [4692](https://github.com/airbytehq/airbyte/pull/4692) | Use account information for checking the connection |
| 0.1.1 | 2021-07-05 | [4539](https://github.com/airbytehq/airbyte/pull/4539) | Add `AIRBYTE_ENTRYPOINT` env variable for kubernetes support |
| 0.1.0 | 2021-06-08 | [3768](https://github.com/airbytehq/airbyte/pull/3768) | Initial Release |

</details>
