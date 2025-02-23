# Sonar Cloud API

## Sync overview

This source can sync data from the [Sonar cloud API](https://sonarcloud.io/web_api). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

- components
- issues
- metrics

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |

## Getting started

### Requirements

- Sonar cloud User Token

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date                                                                  | Pull Request                                              | Subject                                                                         |
| :------ | :-------------------------------------------------------------------- | :-------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.2.12 | 2025-02-22 | [54540](https://github.com/airbytehq/airbyte/pull/54540) | Update dependencies |
| 0.2.11 | 2025-02-15 | [54097](https://github.com/airbytehq/airbyte/pull/54097) | Update dependencies |
| 0.2.10 | 2025-02-08 | [53539](https://github.com/airbytehq/airbyte/pull/53539) | Update dependencies |
| 0.2.9 | 2025-02-01 | [53052](https://github.com/airbytehq/airbyte/pull/53052) | Update dependencies |
| 0.2.8 | 2025-01-25 | [52437](https://github.com/airbytehq/airbyte/pull/52437) | Update dependencies |
| 0.2.7 | 2025-01-18 | [52004](https://github.com/airbytehq/airbyte/pull/52004) | Update dependencies |
| 0.2.6 | 2025-01-11 | [51448](https://github.com/airbytehq/airbyte/pull/51448) | Update dependencies |
| 0.2.5 | 2024-12-28 | [50381](https://github.com/airbytehq/airbyte/pull/50381) | Update dependencies |
| 0.2.4 | 2024-12-14 | [49746](https://github.com/airbytehq/airbyte/pull/49746) | Update dependencies |
| 0.2.3 | 2024-12-12 | [48338](https://github.com/airbytehq/airbyte/pull/48338) | Update dependencies |
| 0.2.2 | 2024-10-28 | [47673](https://github.com/airbytehq/airbyte/pull/47673) | Update dependencies |
| 0.2.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.2.0 | 2024-08-14 | [44063](https://github.com/airbytehq/airbyte/pull/44063) | Refactor connector to manifest-only format |
| 0.1.17 | 2024-08-10 | [43569](https://github.com/airbytehq/airbyte/pull/43569) | Update dependencies |
| 0.1.16 | 2024-08-03 | [43249](https://github.com/airbytehq/airbyte/pull/43249) | Update dependencies |
| 0.1.15 | 2024-07-27 | [42651](https://github.com/airbytehq/airbyte/pull/42651) | Update dependencies |
| 0.1.14 | 2024-07-20 | [42311](https://github.com/airbytehq/airbyte/pull/42311) | Update dependencies |
| 0.1.13 | 2024-07-13 | [41773](https://github.com/airbytehq/airbyte/pull/41773) | Update dependencies |
| 0.1.12 | 2024-07-10 | [41479](https://github.com/airbytehq/airbyte/pull/41479) | Update dependencies |
| 0.1.11 | 2024-07-09 | [41178](https://github.com/airbytehq/airbyte/pull/41178) | Update dependencies |
| 0.1.10 | 2024-07-06 | [40829](https://github.com/airbytehq/airbyte/pull/40829) | Update dependencies |
| 0.1.9 | 2024-06-25 | [40310](https://github.com/airbytehq/airbyte/pull/40310) | Update dependencies |
| 0.1.8 | 2024-06-22 | [40071](https://github.com/airbytehq/airbyte/pull/40071) | Update dependencies |
| 0.1.7 | 2024-06-06 | [39267](https://github.com/airbytehq/airbyte/pull/39267) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.6 | 2024-05-25 | [38597](https://github.com/airbytehq/airbyte/pull/38597) | Make connector compatible with builder |
| 0.1.5 | 2024-04-19 | [37262](https://github.com/airbytehq/airbyte/pull/37262) | Updating to 0.80.0 CDK |
| 0.1.4 | 2024-04-18 | [37262](https://github.com/airbytehq/airbyte/pull/37262) | Manage dependencies with Poetry. |
| 0.1.3 | 2024-04-15 | [37262](https://github.com/airbytehq/airbyte/pull/37262) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.2 | 2024-04-12 | [37262](https://github.com/airbytehq/airbyte/pull/37262) | schema descriptions |
| 0.1.1   | 2023-02-11 l [22868](https://github.com/airbytehq/airbyte/pull/22868) | Specified date formatting in specification                |
| 0.1.0   | 2022-10-26                                                            | [#18475](https://github.com/airbytehq/airbyte/pull/18475) | 🎉 New Source: Sonar Cloud API [low-code CDK]                                   |

</details>
