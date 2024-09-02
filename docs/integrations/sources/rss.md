# RSS

## Overview

The RSS source allows you to read data from any individual RSS feed.

#### Output schema

This source is capable of syncing the following streams:

- `items`
  - Provides stats about specific RSS items.
  - Most fields are simply kept from RSS items as strings if present (`title`, `link`, `description`, `author`, `category`, `comments`, `enclosure`, `guid`).
  - The date field is handled differently. It's transformed into a UTC datetime in a `published` field for easier use in data warehouses and other destinations.
  - The RSS feed you're subscribing to must have a valid `pubDate` field for each item for incremental syncs to work properly.
  - Since `guid` is not a required field, there is no primary key for the feed, only a cursor on the published date.

#### Features

| Feature                   | Supported? |
| :------------------------ | :--------- |
| Full Refresh Sync         | Yes        |
| Incremental - Append Sync | Yes        |
| Namespaces                | No         |

### Requirements / Setup Guide

Only the `url` of an RSS feed is required.

## Performance considerations

None

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                        |
| :------ | :--------- | :------------------------------------------------------- | :----------------------------- |
| 1.0.16 | 2024-08-31 | [45058](https://github.com/airbytehq/airbyte/pull/45058) | Update dependencies |
| 1.0.15 | 2024-08-24 | [44635](https://github.com/airbytehq/airbyte/pull/44635) | Update dependencies |
| 1.0.14 | 2024-08-17 | [44257](https://github.com/airbytehq/airbyte/pull/44257) | Update dependencies |
| 1.0.13 | 2024-08-12 | [43883](https://github.com/airbytehq/airbyte/pull/43883) | Update dependencies |
| 1.0.12 | 2024-08-10 | [43687](https://github.com/airbytehq/airbyte/pull/43687) | Update dependencies |
| 1.0.11 | 2024-08-03 | [43073](https://github.com/airbytehq/airbyte/pull/43073) | Update dependencies |
| 1.0.10 | 2024-07-27 | [42687](https://github.com/airbytehq/airbyte/pull/42687) | Update dependencies |
| 1.0.9 | 2024-07-20 | [42139](https://github.com/airbytehq/airbyte/pull/42139) | Update dependencies |
| 1.0.8 | 2024-07-13 | [41741](https://github.com/airbytehq/airbyte/pull/41741) | Update dependencies |
| 1.0.7 | 2024-07-10 | [41570](https://github.com/airbytehq/airbyte/pull/41570) | Update dependencies |
| 1.0.6 | 2024-07-09 | [41197](https://github.com/airbytehq/airbyte/pull/41197) | Update dependencies |
| 1.0.5 | 2024-07-06 | [40921](https://github.com/airbytehq/airbyte/pull/40921) | Update dependencies |
| 1.0.4 | 2024-06-25 | [40410](https://github.com/airbytehq/airbyte/pull/40410) | Update dependencies |
| 1.0.3 | 2024-06-22 | [40083](https://github.com/airbytehq/airbyte/pull/40083) | Update dependencies |
| 1.0.2 | 2024-06-04 | [39085](https://github.com/airbytehq/airbyte/pull/39085) | [autopull] Upgrade base image to v1.2.1 |
| 1.0.1 | 2024-04-30 | [37535](https://github.com/airbytehq/airbyte/pull/37535) | Fix incremental sync |
| 1.0.0 | 2024-04-20 | [36418](https://github.com/airbytehq/airbyte/pull/36418) | Migrate python cdk to low code |
| 0.1.0 | 2022-10-12 | [18838](https://github.com/airbytehq/airbyte/pull/18838) | Initial release supporting RSS |


</details>
