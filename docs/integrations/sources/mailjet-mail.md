# Mailjet - Mail API

## Sync overview

This source can sync data from the [Mailjet Mail API](https://dev.mailjet.com/email/guides/). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

- contact list
- contacts
- messages
- campaigns
- stats

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |

### Performance considerations

Mailjet APIs are under rate limits for the number of API calls allowed per API keys per second. If you reach a rate limit, API will return a 429 HTTP error code. See [here](https://dev.mailjet.com/email/reference/overview/rate-limits/)

## Getting started

### Requirements

- Mailjet Mail API_KEY
- Mailjet Mail SECRET_KEY

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                                        |
| :------ | :--------- | :-------------------------------------------------------- | :--------------------------------------------- |
| 0.1.4 | 2024-06-04 | [38939](https://github.com/airbytehq/airbyte/pull/38939) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.3 | 2024-05-21 | [38483](https://github.com/airbytehq/airbyte/pull/38483) | [autopull] base image + poetry + up_to_date |
| 0.1.2   | 2022-12-18 | [#30924](https://github.com/airbytehq/airbyte/pull/30924) | Adds Subject field to `message` stream         |
| 0.1.1   | 2022-04-19 | [#24689](https://github.com/airbytehq/airbyte/pull/24689) | Add listrecipient stream                       |
| 0.1.0   | 2022-10-26 | [#18332](https://github.com/airbytehq/airbyte/pull/18332) | 🎉 New Source: Mailjet Mail API [low-code CDK] |

</details>