# PostHog

## Sync overview

This source can sync data for the [PostHog API](https://posthog.com/docs/api/overview). It supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Output schema

This Source is capable of syncing the following core Streams:

* [Annotations](https://posthog.com/docs/api/annotations) \(Incremental\)
* [Cohorts](https://posthog.com/docs/api/cohorts)
* [Events](https://posthog.com/docs/api/events) \(Incremental\)
* [FeatureFlags](https://posthog.com/docs/api/feature-flags)
* [Insights](https://posthog.com/docs/api/insights)
* [InsightsPath](https://posthog.com/docs/api/insights)
* [InsightsSessions](https://posthog.com/docs/api/insights)
* [Persons](https://posthog.com/docs/api/people)
* [Trends](https://posthog.com/docs/api/insights)

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| `string` | `string` |  |
| `number` | `number` |  |
| `array` | `array` |  |
| `object` | `object` |  |

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | Yes |  |
| Namespaces | No |  |

### Performance considerations

The PostHog API doesn't have any known request limitation.

Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* PostHog Personal API Key

### Setup guide

Please follow these [steps](https://posthog.com/docs/api/overview#how-to-obtain-a-personal-api-key) to obtain Private API Key for your account.

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.7 | 2022-07-26 | [14585](https://github.com/airbytehq/airbyte/pull/14585) | Add missing 'properties' field to event attributes |
| 0.1.6 | 2022-01-20 | [8617](https://github.com/airbytehq/airbyte/pull/8617) | Update connector fields title/description |
| 0.1.5 | 2021-12-24 | [9082](https://github.com/airbytehq/airbyte/pull/9082) | Remove obsolete session_events and insights streams |
| 0.1.4 | 2021-09-14 | [6058](https://github.com/airbytehq/airbyte/pull/6058) | Support self-hosted posthog instances |
| 0.1.3 | 2021-07-20 | [4001](https://github.com/airbytehq/airbyte/pull/4001) | Incremental streams read only relevant pages |
| 0.1.2 | 2021-07-15 | [4692](https://github.com/airbytehq/airbyte/pull/4692) | Use account information for checking the connection |
| 0.1.1 | 2021-07-05 | [4539](https://github.com/airbytehq/airbyte/pull/4539) | Add `AIRBYTE_ENTRYPOINT` env variable for kubernetes support |
| 0.1.0 | 2021-06-08 | [3768](https://github.com/airbytehq/airbyte/pull/3768) | Initial Release |
