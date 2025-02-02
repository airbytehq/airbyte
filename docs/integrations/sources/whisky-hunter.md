# Whisky Hunter

## Overview

The Whisky Hunter source can sync data from the [Whisky Hunter API](https://whiskyhunter.net/api/)

#### Output schema

This source is capable of syncing the following streams:

- `auctions_data`
  - Provides stats about specific auctions.
- `auctions_info`
  - Provides information and metadata about recurring and one-off auctions.
- `distilleries_info`
  - Provides information about distilleries.

#### Features

| Feature                   | Supported? |
| :------------------------ | :--------- |
| Full Refresh Sync         | Yes        |
| Incremental - Append Sync | No         |
| Namespaces                | No         |

### Requirements / Setup Guide

No config is required.

## Performance considerations

There is no published rate limit. However, since this data updates infrequently, it is recommended to set the update cadence to 24hr or higher.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                          |
| :------ | :--------- | :------------------------------------------------------- | :----------------------------------------------- |
| 0.2.13 | 2025-02-01 | [53057](https://github.com/airbytehq/airbyte/pull/53057) | Update dependencies |
| 0.2.12 | 2025-01-25 | [52444](https://github.com/airbytehq/airbyte/pull/52444) | Update dependencies |
| 0.2.11 | 2025-01-18 | [51987](https://github.com/airbytehq/airbyte/pull/51987) | Update dependencies |
| 0.2.10 | 2025-01-11 | [51411](https://github.com/airbytehq/airbyte/pull/51411) | Update dependencies |
| 0.2.9 | 2024-12-28 | [50786](https://github.com/airbytehq/airbyte/pull/50786) | Update dependencies |
| 0.2.8 | 2024-12-21 | [50315](https://github.com/airbytehq/airbyte/pull/50315) | Update dependencies |
| 0.2.7 | 2024-12-14 | [49780](https://github.com/airbytehq/airbyte/pull/49780) | Update dependencies |
| 0.2.6 | 2024-12-12 | [49380](https://github.com/airbytehq/airbyte/pull/49380) | Update dependencies |
| 0.2.5 | 2024-12-11 | [49126](https://github.com/airbytehq/airbyte/pull/49126) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.2.4 | 2024-11-04 | [48275](https://github.com/airbytehq/airbyte/pull/48275) | Update dependencies |
| 0.2.3 | 2024-10-29 | [47795](https://github.com/airbytehq/airbyte/pull/47795) | Update dependencies |
| 0.2.2 | 2024-10-28 | [47555](https://github.com/airbytehq/airbyte/pull/47555) | Update dependencies |
| 0.2.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.2.0 | 2024-08-14 | [44045](https://github.com/airbytehq/airbyte/pull/44045) | Refactor connector to manifest-only format |
| 0.1.14 | 2024-08-12 | [43793](https://github.com/airbytehq/airbyte/pull/43793) | Update dependencies |
| 0.1.13 | 2024-08-10 | [43553](https://github.com/airbytehq/airbyte/pull/43553) | Update dependencies |
| 0.1.12 | 2024-08-03 | [43090](https://github.com/airbytehq/airbyte/pull/43090) | Update dependencies |
| 0.1.11 | 2024-07-27 | [42807](https://github.com/airbytehq/airbyte/pull/42807) | Update dependencies |
| 0.1.10 | 2024-07-20 | [42344](https://github.com/airbytehq/airbyte/pull/42344) | Update dependencies |
| 0.1.9 | 2024-07-13 | [41790](https://github.com/airbytehq/airbyte/pull/41790) | Update dependencies |
| 0.1.8 | 2024-07-10 | [41474](https://github.com/airbytehq/airbyte/pull/41474) | Update dependencies |
| 0.1.7 | 2024-07-09 | [41217](https://github.com/airbytehq/airbyte/pull/41217) | Update dependencies |
| 0.1.6 | 2024-07-06 | [40841](https://github.com/airbytehq/airbyte/pull/40841) | Update dependencies |
| 0.1.5 | 2024-06-25 | [40489](https://github.com/airbytehq/airbyte/pull/40489) | Update dependencies |
| 0.1.4 | 2024-06-22 | [40017](https://github.com/airbytehq/airbyte/pull/40017) | Update dependencies |
| 0.1.3 | 2024-06-06 | [39219](https://github.com/airbytehq/airbyte/pull/39219) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.2 | 2024-06-05 | [38841](https://github.com/airbytehq/airbyte/pull/38841) | Make compatible with builder |
| 0.1.1 | 2024-05-21 | [38508](https://github.com/airbytehq/airbyte/pull/38508) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-10-12 | [17918](https://github.com/airbytehq/airbyte/pull/17918) | Initial release supporting the Whisky Hunter API |

</details>
