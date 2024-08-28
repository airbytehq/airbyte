# Omnisend

## Sync overview

This source can sync data from the [Omnisend API](https://api-docs.omnisend.com/reference/intro). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

- contacts
- campaigns
- carts
- orders
- products

### Features

| Feature           | Supported?\(Yes/No\) |
|:------------------|:---------------------|
| Full Refresh Sync | Yes                  |
| Incremental Sync  | No                   |

### Performance considerations

The connector has a rate limit of 400 requests per 1 minute.

## Getting started

### Requirements

- Omnisend API Key

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject        |
|:--------|:-----------| :------------------------------------------------------- | :------------- |
| 0.2.0 | 2024-08-19 | [44411](https://github.com/airbytehq/airbyte/pull/44411) | Refactor connector to manifest-only format |
| 0.1.13 | 2024-08-17 | [44307](https://github.com/airbytehq/airbyte/pull/44307) | Update dependencies |
| 0.1.12 | 2024-08-12 | [43727](https://github.com/airbytehq/airbyte/pull/43727) | Update dependencies |
| 0.1.11 | 2024-08-10 | [43581](https://github.com/airbytehq/airbyte/pull/43581) | Update dependencies |
| 0.1.10 | 2024-08-03 | [42745](https://github.com/airbytehq/airbyte/pull/42745) | Update dependencies |
| 0.1.9 | 2024-07-20 | [42325](https://github.com/airbytehq/airbyte/pull/42325) | Update dependencies |
| 0.1.8 | 2024-07-13 | [41697](https://github.com/airbytehq/airbyte/pull/41697) | Update dependencies |
| 0.1.7 | 2024-07-10 | [41454](https://github.com/airbytehq/airbyte/pull/41454) | Update dependencies |
| 0.1.6 | 2024-07-09 | [41319](https://github.com/airbytehq/airbyte/pull/41319) | Update dependencies |
| 0.1.5 | 2024-07-06 | [40969](https://github.com/airbytehq/airbyte/pull/40969) | Update dependencies |
| 0.1.4 | 2024-06-28 | [38664](https://github.com/airbytehq/airbyte/pull/38664) | Make connector compatible with Builder |
| 0.1.3 | 2024-06-25 | [40440](https://github.com/airbytehq/airbyte/pull/40440) | Update dependencies |
| 0.1.2 | 2024-06-22 | [40167](https://github.com/airbytehq/airbyte/pull/40167) | Update dependencies |
| 0.1.1 | 2024-05-30 | [38533](https://github.com/airbytehq/airbyte/pull/38533) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-10-25 | [18577](https://github.com/airbytehq/airbyte/pull/18577) | Initial commit |

</details>
