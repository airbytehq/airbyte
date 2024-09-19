# ActiveCampaign

## Sync overview

This source can sync data from the [ActiveCampaign API](https://developers.activecampaign.com/reference/overview). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

- campaigns
- contacts
- lists
- deals
- segments
- forms

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |

### Performance considerations

The connector has a rate limit of 5 requests per second per account.

## Getting started

### Requirements

- ActiveCampaign account
- ActiveCampaign API Key

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject        |
| :------ | :--------- | :------------------------------------------------------- | :------------- |
| 0.2.1   | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version   |
| 0.2.0   | 2024-08-02 | [42987](https://github.com/airbytehq/airbyte/pull/42987) | Refactor connector to manifest-only format |
| 0.1.11  | 2024-07-27 | [42677](https://github.com/airbytehq/airbyte/pull/42677) | Update dependencies |
| 0.1.10  | 2024-07-20 | [42337](https://github.com/airbytehq/airbyte/pull/42337) | Update dependencies |
| 0.1.9   | 2024-07-13 | [41702](https://github.com/airbytehq/airbyte/pull/41702) | Update dependencies |
| 0.1.8   | 2024-07-10 | [41577](https://github.com/airbytehq/airbyte/pull/41577) | Update dependencies |
| 0.1.7   | 2024-07-10 | [41326](https://github.com/airbytehq/airbyte/pull/41326) | Update dependencies |
| 0.1.6   | 2024-07-06 | [40873](https://github.com/airbytehq/airbyte/pull/40873) | Update dependencies |
| 0.1.5   | 2024-06-27 | [38224](https://github.com/airbytehq/airbyte/pull/38224) | Make connector compatable with the builder |
| 0.1.4   | 2024-06-25 | [40327](https://github.com/airbytehq/airbyte/pull/40327) | Update dependencies |
| 0.1.3   | 2024-06-22 | [40046](https://github.com/airbytehq/airbyte/pull/40046) | Update dependencies |
| 0.1.2   | 2024-06-04 | [38989](https://github.com/airbytehq/airbyte/pull/38989) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.1   | 2024-05-21 | [38511](https://github.com/airbytehq/airbyte/pull/38511) | [autopull] base image + poetry + up_to_date |
| 0.1.0   | 2022-10-25 | [18335](https://github.com/airbytehq/airbyte/pull/18335) | Initial commit |

</details>
