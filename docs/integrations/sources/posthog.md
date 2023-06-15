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

### Performance considerations

The PostHog API doesn't have any known request limitation.
Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                                                               |
|:--------|:-----------| :------------------------------------------------------- |:--------------------------------------------------------------------------------------------------------------------------------------|
| 0.1.11  | 2023-06-09 | [27135](https://github.com/airbytehq/airbyte/pull/27135) | Fix custom EventsSimpleRetriever                                                                                                      |
| 0.1.10  | 2023-04-15 | [24084](https://github.com/airbytehq/airbyte/pull/24084) | Increase `events` streams batch size                                                                                                  |
| 0.1.9   | 2023-02-13 | [22906](https://github.com/airbytehq/airbyte/pull/22906) | Specified date formatting in specification                                                                                            |
| 0.1.8   | 2022-11-11 | [18993](https://github.com/airbytehq/airbyte/pull/18993) | connector migrated to low-code, added projects,insights streams, added project based slicing for all other streams                    |
| 0.1.7   | 2022-07-26 | [14585](https://github.com/airbytehq/airbyte/pull/14585) | Add missing 'properties' field to event attributes                                                                                    |
| 0.1.6   | 2022-01-20 | [8617](https://github.com/airbytehq/airbyte/pull/8617)   | Update connector fields title/description                                                                                             |
| 0.1.5   | 2021-12-24 | [9082](https://github.com/airbytehq/airbyte/pull/9082)   | Remove obsolete session_events and insights streams                                                                                   |
| 0.1.4   | 2021-09-14 | [6058](https://github.com/airbytehq/airbyte/pull/6058)   | Support self-hosted posthog instances                                                                                                 |
| 0.1.3   | 2021-07-20 | [4001](https://github.com/airbytehq/airbyte/pull/4001)   | Incremental streams read only relevant pages                                                                                          |
| 0.1.2   | 2021-07-15 | [4692](https://github.com/airbytehq/airbyte/pull/4692)   | Use account information for checking the connection                                                                                   |
| 0.1.1   | 2021-07-05 | [4539](https://github.com/airbytehq/airbyte/pull/4539)   | Add `AIRBYTE_ENTRYPOINT` env variable for kubernetes support                                                                          |
| 0.1.0   | 2021-06-08 | [3768](https://github.com/airbytehq/airbyte/pull/3768)   | Initial Release                                                                                                                       |
