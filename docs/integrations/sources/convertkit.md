# ConvertKit

## Sync overview

This source can sync data from the [ConvertKit API](https://developers.convertkit.com/#getting-started). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

- sequences
- subscribers
- broadcasts
- tags
- forms

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |

### Performance considerations

The connector has a rate limit of no more than 120 requests over a rolling 60 second period, for a given api secret.

## Getting started

### Requirements

- ConvertKit API Secret

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject        |
| :------ | :--------- | :------------------------------------------------------- | :------------- |
| 0.2.10 | 2025-01-18 | [51673](https://github.com/airbytehq/airbyte/pull/51673) | Update dependencies |
| 0.2.9 | 2025-01-11 | [51107](https://github.com/airbytehq/airbyte/pull/51107) | Update dependencies |
| 0.2.8 | 2024-12-28 | [50522](https://github.com/airbytehq/airbyte/pull/50522) | Update dependencies |
| 0.2.7 | 2024-12-21 | [50066](https://github.com/airbytehq/airbyte/pull/50066) | Update dependencies |
| 0.2.6 | 2024-12-14 | [49510](https://github.com/airbytehq/airbyte/pull/49510) | Update dependencies |
| 0.2.5 | 2024-12-12 | [48958](https://github.com/airbytehq/airbyte/pull/48958) | Update dependencies |
| 0.2.4 | 2024-11-04 | [48217](https://github.com/airbytehq/airbyte/pull/48217) | Update dependencies |
| 0.2.3 | 2024-10-29 | [47764](https://github.com/airbytehq/airbyte/pull/47764) | Update dependencies |
| 0.2.2 | 2024-10-28 | [47619](https://github.com/airbytehq/airbyte/pull/47619) | Update dependencies |
| 0.2.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.2.0 | 2024-08-15 | [44161](https://github.com/airbytehq/airbyte/pull/44161) | Refactor connector to manifest-only format |
| 0.1.14 | 2024-08-12 | [43803](https://github.com/airbytehq/airbyte/pull/43803) | Update dependencies |
| 0.1.13 | 2024-08-10 | [43503](https://github.com/airbytehq/airbyte/pull/43503) | Update dependencies |
| 0.1.12 | 2024-08-03 | [43237](https://github.com/airbytehq/airbyte/pull/43237) | Update dependencies |
| 0.1.11 | 2024-07-27 | [42643](https://github.com/airbytehq/airbyte/pull/42643) | Update dependencies |
| 0.1.10 | 2024-07-20 | [42363](https://github.com/airbytehq/airbyte/pull/42363) | Update dependencies |
| 0.1.9 | 2024-07-13 | [41742](https://github.com/airbytehq/airbyte/pull/41742) | Update dependencies |
| 0.1.8 | 2024-07-10 | [41405](https://github.com/airbytehq/airbyte/pull/41405) | Update dependencies |
| 0.1.7 | 2024-07-09 | [41272](https://github.com/airbytehq/airbyte/pull/41272) | Update dependencies |
| 0.1.6 | 2024-07-06 | [40860](https://github.com/airbytehq/airbyte/pull/40860) | Update dependencies |
| 0.1.5 | 2024-06-25 | [40282](https://github.com/airbytehq/airbyte/pull/40282) | Update dependencies |
| 0.1.4 | 2024-06-22 | [39989](https://github.com/airbytehq/airbyte/pull/39989) | Update dependencies |
| 0.1.3 | 2024-06-17 | [39505](https://github.com/airbytehq/airbyte/pull/39505) | Make compatible with builder |
| 0.1.2 | 2024-06-06 | [39299](https://github.com/airbytehq/airbyte/pull/39299) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.1 | 2024-05-21 | [38492](https://github.com/airbytehq/airbyte/pull/38492) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-10-25 | [18455](https://github.com/airbytehq/airbyte/pull/18455) | Initial commit |

</details>
