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
| 1.1.1   | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version   |
| 1.1.0 | 2024-08-15 | [44131](https://github.com/airbytehq/airbyte/pull/44131) | Refactor connector to manifest-only format |
| 1.0.13 | 2024-08-12 | [43839](https://github.com/airbytehq/airbyte/pull/43839) | Update dependencies |
| 1.0.12 | 2024-08-10 | [43483](https://github.com/airbytehq/airbyte/pull/43483) | Update dependencies |
| 1.0.11 | 2024-08-03 | [43220](https://github.com/airbytehq/airbyte/pull/43220) | Update dependencies |
| 1.0.10 | 2024-07-27 | [42758](https://github.com/airbytehq/airbyte/pull/42758) | Update dependencies |
| 1.0.9 | 2024-07-20 | [42362](https://github.com/airbytehq/airbyte/pull/42362) | Update dependencies |
| 1.0.8 | 2024-07-13 | [41859](https://github.com/airbytehq/airbyte/pull/41859) | Update dependencies |
| 1.0.7 | 2024-07-10 | [41404](https://github.com/airbytehq/airbyte/pull/41404) | Update dependencies |
| 1.0.6 | 2024-07-09 | [41150](https://github.com/airbytehq/airbyte/pull/41150) | Update dependencies |
| 1.0.5 | 2024-07-06 | [40858](https://github.com/airbytehq/airbyte/pull/40858) | Update dependencies |
| 1.0.4 | 2024-06-25 | [40447](https://github.com/airbytehq/airbyte/pull/40447) | Update dependencies |
| 1.0.3 | 2024-06-22 | [40060](https://github.com/airbytehq/airbyte/pull/40060) | Update dependencies |
| 1.0.2 | 2024-06-06 | [39181](https://github.com/airbytehq/airbyte/pull/39181) | [autopull] Upgrade base image to v1.2.2 |
| 1.0.1 | 2024-05-30 | [38385](https://github.com/airbytehq/airbyte/pull/38385) | [autopull] base image + poetry + up_to_date |
| 1.0.0 | 2024-05-28 | [38342](https://github.com/airbytehq/airbyte/pull/38342) | Make compatability with builder |
| 0.1.0 | 2022-10-25 | [18336](https://github.com/airbytehq/airbyte/pull/18336) | Initial commit |

</details>
