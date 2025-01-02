# PostHog

This page contains the setup guide and reference information for the PostHog source connector.

## Prerequisites

- api_key - obtain Private API Key for your account following these [steps](https://posthog.com/docs/api/overview#how-to-obtain-a-personal-api-key)
- base_url - 'https://app.posthog.com' by default, but it can be different if self-hosted posthog instances is used

## Setup guide

### Step 1: Set up PostHog

- PostHog Account

## Step 2: Set up the PostHog connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the PostHog connector and select **PostHog** from the Source type dropdown.
4. Enter your `apikey`.
5. Enter your `project_id`.
6. Enter your `start_date`.
7. Change default `base_url` if self-hosted posthog instances is used
8. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your `api_key`.
4. Enter your `project_id`.
5. Enter your `start_date`.
6. Change default `base_url` if self-hosted posthog instances is used
7. Click **Set up source**.

## Supported streams and sync modes

- [Projects](https://posthog.com/docs/api/projects)
- [Annotations](https://posthog.com/docs/api/annotations)
- [Cohorts](https://posthog.com/docs/api/cohorts)
- [Events](https://posthog.com/docs/api/events) \(Incremental\)
- [FeatureFlags](https://posthog.com/docs/api/feature-flags)
- [Insights](https://posthog.com/docs/api/insights)
- [Persons](https://posthog.com/docs/api/people)

### Rate limiting

Private `GET`, `POST`, `PATCH`, `DELETE` endpoints are rate limited. Public POST-only endpoints are **not** rate limited. A rule of thumb for whether rate limits apply is if the personal API key is used for authentication.

There are separate limits for different kinds of resources.

- For all analytics endpoints (such as calculating insights, retrieving persons, or retrieving session recordings), the rate limits are `240/minute` and `1200/hour`.

- The [HogQL query](https://posthog.com/docs/hogql#api-access) endpoint (`/api/project/:id/query`) has a rate limit of `120/hour`.

- For the rest of the create, read, update, and delete endpoints, the rate limits are `480/minute` and `4800/hour`.

- For Public POST-only endpoints like event capture (`/capture`) and feature flag evaluation (`/decide`), there are no rate limits.

These limits apply to **the entire team** (i.e. all users within your PostHog organization). For example, if a script requesting feature flag metadata hits the rate limit, and another user, using a different personal API key, makes a single request to the persons API, this gets rate limited as well.

For large or regular exports of events, use [batch exports](https://posthog.com/docs/cdp).

Want to use the PostHog API beyond these limits? Email Posthog at `customers@posthog.com`.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                 |
| :------ | :--------- | :------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------- |
| 2.0.0 | 2024-01-29 | [?](https://github.com/airbytehq/airbyte/pull/?) | Require a single `project_id` to be specified in the source |
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
