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
| 0.1.3 | 2024-06-17 | [39505](https://github.com/airbytehq/airbyte/pull/39505) | Make compatible with builder |
| 0.1.2 | 2024-06-06 | [39299](https://github.com/airbytehq/airbyte/pull/39299) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.1 | 2024-05-21 | [38492](https://github.com/airbytehq/airbyte/pull/38492) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-10-25 | [18455](https://github.com/airbytehq/airbyte/pull/18455) | Initial commit |

</details>
