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
| 0.2.5 | 2025-03-08 | [55444](https://github.com/airbytehq/airbyte/pull/55444) | Update dependencies |
| 0.2.4 | 2025-03-01 | [54764](https://github.com/airbytehq/airbyte/pull/54764) | Update dependencies |
| 0.2.3 | 2025-02-22 | [54322](https://github.com/airbytehq/airbyte/pull/54322) | Update dependencies |
| 0.2.2 | 2025-02-15 | [47463](https://github.com/airbytehq/airbyte/pull/47463) | Update dependencies |
| 0.2.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.2.0 | 2024-08-15 | [44129](https://github.com/airbytehq/airbyte/pull/44129) | Refactor connector to manifest-only format |
| 0.1.16 | 2024-08-12 | [43814](https://github.com/airbytehq/airbyte/pull/43814) | Update dependencies |
| 0.1.15 | 2024-08-10 | [43571](https://github.com/airbytehq/airbyte/pull/43571) | Update dependencies |
| 0.1.14 | 2024-08-03 | [43161](https://github.com/airbytehq/airbyte/pull/43161) | Update dependencies |
| 0.1.13 | 2024-07-27 | [42613](https://github.com/airbytehq/airbyte/pull/42613) | Update dependencies |
| 0.1.12 | 2024-07-20 | [42245](https://github.com/airbytehq/airbyte/pull/42245) | Update dependencies |
| 0.1.11 | 2024-07-13 | [41867](https://github.com/airbytehq/airbyte/pull/41867) | Update dependencies |
| 0.1.10 | 2024-07-10 | [41587](https://github.com/airbytehq/airbyte/pull/41587) | Update dependencies |
| 0.1.9 | 2024-07-09 | [41177](https://github.com/airbytehq/airbyte/pull/41177) | Update dependencies |
| 0.1.8 | 2024-07-06 | [40930](https://github.com/airbytehq/airbyte/pull/40930) | Update dependencies |
| 0.1.7 | 2024-07-02 | [40257](https://github.com/airbytehq/airbyte/pull/40257) | Make compatible with builder |
| 0.1.6 | 2024-06-25 | [40415](https://github.com/airbytehq/airbyte/pull/40415) | Update dependencies |
| 0.1.5 | 2024-06-22 | [40065](https://github.com/airbytehq/airbyte/pull/40065) | Update dependencies |
| 0.1.4 | 2024-06-04 | [38939](https://github.com/airbytehq/airbyte/pull/38939) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.3 | 2024-05-21 | [38483](https://github.com/airbytehq/airbyte/pull/38483) | [autopull] base image + poetry + up_to_date |
| 0.1.2   | 2022-12-18 | [#30924](https://github.com/airbytehq/airbyte/pull/30924) | Adds Subject field to `message` stream         |
| 0.1.1   | 2022-04-19 | [#24689](https://github.com/airbytehq/airbyte/pull/24689) | Add listrecipient stream                       |
| 0.1.0   | 2022-10-26 | [#18332](https://github.com/airbytehq/airbyte/pull/18332) | 🎉 New Source: Mailjet Mail API [low-code CDK] |

</details>
