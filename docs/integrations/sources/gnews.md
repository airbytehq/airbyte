# GNews

## Overview

The GNews source supports full refresh syncs

### Output schema

Two output streams are available from this source:

_[Search](https://gnews.io/docs/v4?shell#search-endpoint).
_[Top Headlines](https://gnews.io/docs/v4?shell#top-headlines-endpoint).

### Features

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | Yes        |

### Performance considerations

Rate Limiting is based on the API Key tier subscription, get more info [here](https://gnews.io/#pricing).

## Getting started

### Requirements

- GNews API Key.

### Connect using `API Key`:

1. Generate an API Key as described [here](https://gnews.io/docs/v4?shell#authentication).
2. Use the generated `API Key` in the Airbyte connection.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                          |
| :------ | :--------- | :------------------------------------------------------- | :----------------------------------------------- |
| 0.2.11 | 2025-02-08 | [53366](https://github.com/airbytehq/airbyte/pull/53366) | Update dependencies |
| 0.2.10 | 2025-02-01 | [52861](https://github.com/airbytehq/airbyte/pull/52861) | Update dependencies |
| 0.2.9 | 2025-01-25 | [52320](https://github.com/airbytehq/airbyte/pull/52320) | Update dependencies |
| 0.2.8 | 2025-01-18 | [51622](https://github.com/airbytehq/airbyte/pull/51622) | Update dependencies |
| 0.2.7 | 2025-01-11 | [51072](https://github.com/airbytehq/airbyte/pull/51072) | Update dependencies |
| 0.2.6 | 2024-12-28 | [50535](https://github.com/airbytehq/airbyte/pull/50535) | Update dependencies |
| 0.2.5 | 2024-12-21 | [50037](https://github.com/airbytehq/airbyte/pull/50037) | Update dependencies |
| 0.2.4 | 2024-12-14 | [49521](https://github.com/airbytehq/airbyte/pull/49521) | Update dependencies |
| 0.2.3 | 2024-12-12 | [48214](https://github.com/airbytehq/airbyte/pull/48214) | Update dependencies |
| 0.2.2 | 2024-10-29 | [47918](https://github.com/airbytehq/airbyte/pull/47918) | Update dependencies |
| 0.2.1 | 2024-10-28 | [47499](https://github.com/airbytehq/airbyte/pull/47499) | Update dependencies |
| 0.2.0 | 2024-10-17 | [46959](https://github.com/airbytehq/airbyte/pull/46959) | Refactor connector to manifest-only format |
| 0.1.25 | 2024-10-12 | [46802](https://github.com/airbytehq/airbyte/pull/46802) | Update dependencies |
| 0.1.24 | 2024-10-05 | [46425](https://github.com/airbytehq/airbyte/pull/46425) | Update dependencies |
| 0.1.23 | 2024-09-28 | [46209](https://github.com/airbytehq/airbyte/pull/46209) | Update dependencies |
| 0.1.22 | 2024-09-21 | [45808](https://github.com/airbytehq/airbyte/pull/45808) | Update dependencies |
| 0.1.21 | 2024-09-14 | [45541](https://github.com/airbytehq/airbyte/pull/45541) | Update dependencies |
| 0.1.20 | 2024-09-07 | [45290](https://github.com/airbytehq/airbyte/pull/45290) | Update dependencies |
| 0.1.19 | 2024-08-31 | [45034](https://github.com/airbytehq/airbyte/pull/45034) | Update dependencies |
| 0.1.18 | 2024-08-24 | [44631](https://github.com/airbytehq/airbyte/pull/44631) | Update dependencies |
| 0.1.17 | 2024-08-17 | [44355](https://github.com/airbytehq/airbyte/pull/44355) | Update dependencies |
| 0.1.16 | 2024-08-12 | [43922](https://github.com/airbytehq/airbyte/pull/43922) | Update dependencies |
| 0.1.15 | 2024-08-10 | [43659](https://github.com/airbytehq/airbyte/pull/43659) | Update dependencies |
| 0.1.14 | 2024-08-03 | [43263](https://github.com/airbytehq/airbyte/pull/43263) | Update dependencies |
| 0.1.13 | 2024-07-27 | [42634](https://github.com/airbytehq/airbyte/pull/42634) | Update dependencies |
| 0.1.12 | 2024-07-20 | [42340](https://github.com/airbytehq/airbyte/pull/42340) | Update dependencies |
| 0.1.11 | 2024-07-13 | [41832](https://github.com/airbytehq/airbyte/pull/41832) | Update dependencies |
| 0.1.10 | 2024-07-10 | [41461](https://github.com/airbytehq/airbyte/pull/41461) | Update dependencies |
| 0.1.9 | 2024-07-09 | [41179](https://github.com/airbytehq/airbyte/pull/41179) | Update dependencies |
| 0.1.8 | 2024-07-06 | [40892](https://github.com/airbytehq/airbyte/pull/40892) | Update dependencies |
| 0.1.7 | 2024-06-25 | [40281](https://github.com/airbytehq/airbyte/pull/40281) | Update dependencies |
| 0.1.6 | 2024-06-22 | [40196](https://github.com/airbytehq/airbyte/pull/40196) | Update dependencies |
| 0.1.5 | 2024-06-06 | [39188](https://github.com/airbytehq/airbyte/pull/39188) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.4 | 2024-05-20 | [38394](https://github.com/airbytehq/airbyte/pull/38394) | [autopull] base image + poetry + up_to_date |
| 0.1.3 | 2022-12-16 | [21322](https://github.com/airbytehq/airbyte/pull/21322) | Reorganize manifest inline stream schemas |
| 0.1.2 | 2022-12-16 | [20405](https://github.com/airbytehq/airbyte/pull/20405) | Update the manifest to use inline stream schemas |
| 0.1.1 | 2022-12-13 | [20460](https://github.com/airbytehq/airbyte/pull/20460) | Update source acceptance test config |
| 0.1.0 | 2022-11-01 | [18808](https://github.com/airbytehq/airbyte/pull/18808) | 🎉 New Source: GNews |

</details>
