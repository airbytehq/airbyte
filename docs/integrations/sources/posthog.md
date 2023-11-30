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
5. Enter your `start_date`.
6. Change default `base_url` if self-hosted posthog instances is used
7. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your `api_key`.
4. Enter your `start_date`.
5. Change default `base_url` if self-hosted posthog instances is used
6. Click **Set up source**.

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

| Version | Date       | Pull Request                                             | Subject                                                                                                            |
|:--------|:-----------|:---------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------|
| 0.1.15  | 2023-10-28 | [31265](https://github.com/airbytehq/airbyte/pull/31265) | Fix Events stream datetime format                                                                     |
| 0.1.14  | 2023-08-29 | [29947](https://github.com/airbytehq/airbyte/pull/29947) | Add optional field to spec: `events_time_step`                                                                     |
| 0.1.13  | 2023-07-19 | [28461](https://github.com/airbytehq/airbyte/pull/28461) | Fixed EventsSimpleRetriever declaration                                                                            |
| 0.1.12  | 2023-06-28 | [27764](https://github.com/airbytehq/airbyte/pull/27764) | Update following state breaking changes                                                                            |
| 0.1.11  | 2023-06-09 | [27135](https://github.com/airbytehq/airbyte/pull/27135) | Fix custom EventsSimpleRetriever                                                                                   |
| 0.1.10  | 2023-04-15 | [24084](https://github.com/airbytehq/airbyte/pull/24084) | Increase `events` streams batch size                                                                               |
| 0.1.9   | 2023-02-13 | [22906](https://github.com/airbytehq/airbyte/pull/22906) | Specified date formatting in specification                                                                         |
| 0.1.8   | 2022-11-11 | [18993](https://github.com/airbytehq/airbyte/pull/18993) | connector migrated to low-code, added projects,insights streams, added project based slicing for all other streams |
| 0.1.7   | 2022-07-26 | [14585](https://github.com/airbytehq/airbyte/pull/14585) | Add missing 'properties' field to event attributes                                                                 |
| 0.1.6   | 2022-01-20 | [8617](https://github.com/airbytehq/airbyte/pull/8617)   | Update connector fields title/description                                                                          |
| 0.1.5   | 2021-12-24 | [9082](https://github.com/airbytehq/airbyte/pull/9082)   | Remove obsolete session_events and insights streams                                                                |
| 0.1.4   | 2021-09-14 | [6058](https://github.com/airbytehq/airbyte/pull/6058)   | Support self-hosted posthog instances                                                                              |
| 0.1.3   | 2021-07-20 | [4001](https://github.com/airbytehq/airbyte/pull/4001)   | Incremental streams read only relevant pages                                                                       |
| 0.1.2   | 2021-07-15 | [4692](https://github.com/airbytehq/airbyte/pull/4692)   | Use account information for checking the connection                                                                |
| 0.1.1   | 2021-07-05 | [4539](https://github.com/airbytehq/airbyte/pull/4539)   | Add `AIRBYTE_ENTRYPOINT` env variable for kubernetes support                                                       |
| 0.1.0   | 2021-06-08 | [3768](https://github.com/airbytehq/airbyte/pull/3768)   | Initial Release                                                                                                    |
