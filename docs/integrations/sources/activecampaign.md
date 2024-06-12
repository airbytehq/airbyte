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
| 0.1.2 | 2024-06-04 | [38989](https://github.com/airbytehq/airbyte/pull/38989) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.1 | 2024-05-21 | [38511](https://github.com/airbytehq/airbyte/pull/38511) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-10-25 | [18335](https://github.com/airbytehq/airbyte/pull/18335) | Initial commit |

</details>
