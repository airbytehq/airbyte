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
| 0.1.3 | 2024-06-06 | [39219](https://github.com/airbytehq/airbyte/pull/39219) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.2 | 2024-06-05 | [38841](https://github.com/airbytehq/airbyte/pull/38841) | Make compatible with builder |
| 0.1.1 | 2024-05-21 | [38508](https://github.com/airbytehq/airbyte/pull/38508) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-10-12 | [17918](https://github.com/airbytehq/airbyte/pull/17918) | Initial release supporting the Whisky Hunter API |

</details>
