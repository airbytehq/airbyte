# MailerLite

## Sync overview

This source can sync data from the [MailerLite API](https://developers.mailerlite.com/docs/#mailerlite-api). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

- campaigns
- subscribers
- automations
- timezones
- segments
- forms_popup
- forms_embedded
- forms_promotion

### Features

| Feature           | Supported?\(Yes/No\) | 
|:------------------|:---------------------|
| Full Refresh Sync | Yes                  |
| Incremental Sync  | No                   |

### Performance considerations

MailerLite API has a global rate limit of 120 requests per minute.

## Getting started

### Requirements

- MailerLite API Key

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                     |
|:--------|:-----------|:---------------------------------------------------------|:--------------------------------------------|
| 1.0.1   | 2024-05-30 | [38385](https://github.com/airbytehq/airbyte/pull/38385) | [autopull] base image + poetry + up_to_date |
| 1.0.0   | 2024-05-28 | [38342](https://github.com/airbytehq/airbyte/pull/38342) | Make compatability with builder             |
| 0.1.0   | 2022-10-25 | [18336](https://github.com/airbytehq/airbyte/pull/18336) | Initial commit                              |

</details>