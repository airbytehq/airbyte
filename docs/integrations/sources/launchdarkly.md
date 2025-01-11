# Launchdarkly API

## Sync overview

This source can sync data from the [Launchdarkly API](https://apidocs.launchdarkly.com/#section/Overview). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

- projects
- environments
- metrics
- members
- audit_log
- flags

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |

### Performance considerations

Launchdarkly APIs are under rate limits for the number of API calls allowed per API keys per second. If you reach a rate limit, API will return a 429 HTTP error code. See [here](https://apidocs.launchdarkly.com/#section/Overview/Rate-limiting)

## Getting started

### Requirements

- Access Token

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                                        |
| :------ | :--------- | :-------------------------------------------------------- | :--------------------------------------------- |
| 0.2.8 | 2025-01-11 | [51181](https://github.com/airbytehq/airbyte/pull/51181) | Update dependencies |
| 0.2.7 | 2024-12-28 | [50604](https://github.com/airbytehq/airbyte/pull/50604) | Update dependencies |
| 0.2.6 | 2024-12-21 | [50104](https://github.com/airbytehq/airbyte/pull/50104) | Update dependencies |
| 0.2.5 | 2024-12-14 | [49642](https://github.com/airbytehq/airbyte/pull/49642) | Update dependencies |
| 0.2.4 | 2024-12-12 | [49257](https://github.com/airbytehq/airbyte/pull/49257) | Update dependencies |
| 0.2.3 | 2024-12-11 | [47856](https://github.com/airbytehq/airbyte/pull/47856) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.2.2 | 2024-10-28 | [47620](https://github.com/airbytehq/airbyte/pull/47620) | Update dependencies |
| 0.2.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.2.0 | 2024-08-15 | [44135](https://github.com/airbytehq/airbyte/pull/44135) | Refactor connector to manifest-only format |
| 0.1.13 | 2024-08-12 | [43791](https://github.com/airbytehq/airbyte/pull/43791) | Update dependencies |
| 0.1.12 | 2024-08-10 | [43587](https://github.com/airbytehq/airbyte/pull/43587) | Update dependencies |
| 0.1.11 | 2024-08-03 | [43270](https://github.com/airbytehq/airbyte/pull/43270) | Update dependencies |
| 0.1.10 | 2024-07-27 | [42600](https://github.com/airbytehq/airbyte/pull/42600) | Update dependencies |
| 0.1.9 | 2024-07-20 | [42369](https://github.com/airbytehq/airbyte/pull/42369) | Update dependencies |
| 0.1.8 | 2024-07-13 | [41700](https://github.com/airbytehq/airbyte/pull/41700) | Update dependencies |
| 0.1.7 | 2024-07-10 | [41425](https://github.com/airbytehq/airbyte/pull/41425) | Update dependencies |
| 0.1.6 | 2024-07-09 | [41284](https://github.com/airbytehq/airbyte/pull/41284) | Update dependencies |
| 0.1.5 | 2024-07-06 | [40891](https://github.com/airbytehq/airbyte/pull/40891) | Update dependencies |
| 0.1.4 | 2024-06-25 | [40395](https://github.com/airbytehq/airbyte/pull/40395) | Update dependencies |
| 0.1.3 | 2024-06-22 | [40131](https://github.com/airbytehq/airbyte/pull/40131) | Update dependencies |
| 0.1.2 | 2024-06-06 | [39245](https://github.com/airbytehq/airbyte/pull/39245) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.1 | 2024-05-28 | [38694](https://github.com/airbytehq/airbyte/pull/38694) | Make compatible with builder |
| 0.1.0   | 2022-10-30 | [#18660](https://github.com/airbytehq/airbyte/pull/18660) | 🎉 New Source: Launchdarkly API [low-code CDK] |

</details>
