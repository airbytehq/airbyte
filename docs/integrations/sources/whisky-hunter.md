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
| 0.2.1   | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version   |
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
