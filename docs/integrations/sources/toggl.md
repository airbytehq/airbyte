# Toggl API

## Sync overview

This source can sync data from the [Toggl API](https://developers.track.toggl.com/docs/). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

- time_entries
- organizations
- organizations_users
- organizations_groups
- workspace
- workspace_clients
- workspace_tasks

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |

### Performance considerations

Toggl APIs are under rate limits for the number of API calls allowed per API keys per second. If you reach a rate limit, API will return a 429 HTTP error code. See [here](https://developers.track.toggl.com/docs/#the-api-format)

## Getting started

### Requirements

- API token

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                                 |
|:--------|:-----------| :-------------------------------------------------------- | :-------------------------------------- |
| 0.2.10 | 2025-02-01 | [53090](https://github.com/airbytehq/airbyte/pull/53090) | Update dependencies |
| 0.2.9 | 2025-01-25 | [52429](https://github.com/airbytehq/airbyte/pull/52429) | Update dependencies |
| 0.2.8 | 2025-01-18 | [52026](https://github.com/airbytehq/airbyte/pull/52026) | Update dependencies |
| 0.2.7 | 2025-01-11 | [51383](https://github.com/airbytehq/airbyte/pull/51383) | Update dependencies |
| 0.2.6 | 2024-12-28 | [50775](https://github.com/airbytehq/airbyte/pull/50775) | Update dependencies |
| 0.2.5 | 2024-12-21 | [50305](https://github.com/airbytehq/airbyte/pull/50305) | Update dependencies |
| 0.2.4 | 2024-12-14 | [49738](https://github.com/airbytehq/airbyte/pull/49738) | Update dependencies |
| 0.2.3 | 2024-12-12 | [49434](https://github.com/airbytehq/airbyte/pull/49434) | Update dependencies |
| 0.2.2 | 2024-10-29 | [47883](https://github.com/airbytehq/airbyte/pull/47883) | Update dependencies |
| 0.2.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.2.0 | 2024-08-14 | [44056](https://github.com/airbytehq/airbyte/pull/44056) | Refactor connector to manifest-only format |
| 0.1.14 | 2024-08-12 | [43860](https://github.com/airbytehq/airbyte/pull/43860) | Update dependencies |
| 0.1.13 | 2024-08-10 | [43485](https://github.com/airbytehq/airbyte/pull/43485) | Update dependencies |
| 0.1.12 | 2024-08-03 | [43064](https://github.com/airbytehq/airbyte/pull/43064) | Update dependencies |
| 0.1.11 | 2024-07-27 | [42755](https://github.com/airbytehq/airbyte/pull/42755) | Update dependencies |
| 0.1.10 | 2024-07-20 | [42244](https://github.com/airbytehq/airbyte/pull/42244) | Update dependencies |
| 0.1.9 | 2024-07-13 | [41736](https://github.com/airbytehq/airbyte/pull/41736) | Update dependencies |
| 0.1.8 | 2024-07-10 | [41510](https://github.com/airbytehq/airbyte/pull/41510) | Update dependencies |
| 0.1.7 | 2024-07-09 | [41227](https://github.com/airbytehq/airbyte/pull/41227) | Update dependencies |
| 0.1.6 | 2024-07-06 | [40968](https://github.com/airbytehq/airbyte/pull/40968) | Update dependencies |
| 0.1.5   | 2024-06-28 | [#38740](https://github.com/airbytehq/airbyte/pull/38740) | Make connector compatible with Builder  |
| 0.1.4   | 2024-06-25 | [40493](https://github.com/airbytehq/airbyte/pull/40493) | Update dependencies |
| 0.1.3   | 2024-06-22 | [40096](https://github.com/airbytehq/airbyte/pull/40096) | Update dependencies |
| 0.1.2   | 2024-06-04 | [38985](https://github.com/airbytehq/airbyte/pull/38985) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.1   | 2024-05-20 | [38376](https://github.com/airbytehq/airbyte/pull/38376) | [autopull] base image + poetry + up_to_date |
| 0.1.0   | 2022-10-28 | [#18507](https://github.com/airbytehq/airbyte/pull/18507) | 🎉 New Source: Toggl API [low-code CDK] |

</details>
