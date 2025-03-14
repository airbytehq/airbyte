# Mailjet - SMS API

## Sync overview

This source can sync data from the [Mailjet SMS API](https://dev.mailjet.com/sms/guides/). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

- SMS

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |

### Performance considerations

Mailjet APIs are under rate limits for the number of API calls allowed per API keys per second. If you reach a rate limit, API will return a 429 HTTP error code. See [here](https://dev.mailjet.com/sms/reference/overview/rate-limits/)

## Getting started

### Requirements

- Mailjet SMS TOKEN

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                                                                         |
| :------ | :--------- | :-------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.2.16 | 2025-03-08 | [55459](https://github.com/airbytehq/airbyte/pull/55459) | Update dependencies |
| 0.2.15 | 2025-03-01 | [54808](https://github.com/airbytehq/airbyte/pull/54808) | Update dependencies |
| 0.2.14 | 2025-02-22 | [54351](https://github.com/airbytehq/airbyte/pull/54351) | Update dependencies |
| 0.2.13 | 2025-02-15 | [53858](https://github.com/airbytehq/airbyte/pull/53858) | Update dependencies |
| 0.2.12 | 2025-02-08 | [53255](https://github.com/airbytehq/airbyte/pull/53255) | Update dependencies |
| 0.2.11 | 2025-02-01 | [52740](https://github.com/airbytehq/airbyte/pull/52740) | Update dependencies |
| 0.2.10 | 2025-01-25 | [52286](https://github.com/airbytehq/airbyte/pull/52286) | Update dependencies |
| 0.2.9 | 2025-01-18 | [51809](https://github.com/airbytehq/airbyte/pull/51809) | Update dependencies |
| 0.2.8 | 2025-01-11 | [51208](https://github.com/airbytehq/airbyte/pull/51208) | Update dependencies |
| 0.2.7 | 2024-12-28 | [50614](https://github.com/airbytehq/airbyte/pull/50614) | Update dependencies |
| 0.2.6 | 2024-12-21 | [50111](https://github.com/airbytehq/airbyte/pull/50111) | Update dependencies |
| 0.2.5 | 2024-12-14 | [49647](https://github.com/airbytehq/airbyte/pull/49647) | Update dependencies |
| 0.2.4 | 2024-12-12 | [49235](https://github.com/airbytehq/airbyte/pull/49235) | Update dependencies |
| 0.2.3 | 2024-12-11 | [47810](https://github.com/airbytehq/airbyte/pull/47810) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.2.2 | 2024-10-28 | [47489](https://github.com/airbytehq/airbyte/pull/47489) | Update dependencies |
| 0.2.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.2.0 | 2024-08-15 | [44128](https://github.com/airbytehq/airbyte/pull/44128) | Refactor connector to manifest-only format |
| 0.1.15 | 2024-08-10 | [43594](https://github.com/airbytehq/airbyte/pull/43594) | Update dependencies |
| 0.1.14 | 2024-08-03 | [43179](https://github.com/airbytehq/airbyte/pull/43179) | Update dependencies |
| 0.1.13 | 2024-07-27 | [42747](https://github.com/airbytehq/airbyte/pull/42747) | Update dependencies |
| 0.1.12 | 2024-07-20 | [42161](https://github.com/airbytehq/airbyte/pull/42161) | Update dependencies |
| 0.1.11 | 2024-07-13 | [41804](https://github.com/airbytehq/airbyte/pull/41804) | Update dependencies |
| 0.1.10 | 2024-07-10 | [41516](https://github.com/airbytehq/airbyte/pull/41516) | Update dependencies |
| 0.1.9 | 2024-07-09 | [41208](https://github.com/airbytehq/airbyte/pull/41208) | Update dependencies |
| 0.1.8 | 2024-07-06 | [40775](https://github.com/airbytehq/airbyte/pull/40775) | Update dependencies |
| 0.1.7 | 2024-06-25 | [40402](https://github.com/airbytehq/airbyte/pull/40402) | Update dependencies |
| 0.1.6 | 2024-06-22 | [40010](https://github.com/airbytehq/airbyte/pull/40010) | Update dependencies |
| 0.1.5 | 2024-06-06 | [39165](https://github.com/airbytehq/airbyte/pull/39165) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.4 | 2024-05-28 | [38730](https://github.com/airbytehq/airbyte/pull/38730) | Make compatible with builder. |
| 0.1.3 | 2024-04-19 | [37195](https://github.com/airbytehq/airbyte/pull/37195) | Upgrade to CDK 0.80.0 and manage dependencies with Poetry. |
| 0.1.2 | 2024-04-15 | [37195](https://github.com/airbytehq/airbyte/pull/37195) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.1 | 2024-04-12 | [37195](https://github.com/airbytehq/airbyte/pull/37195) | schema descriptions |
| 0.1.0   | 2022-10-26 | [#18345](https://github.com/airbytehq/airbyte/pull/18345) | 🎉 New Source: Mailjet SMS API [low-code CDK]                                   |

</details>
