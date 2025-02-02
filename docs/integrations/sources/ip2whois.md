# Ip2whois API

## Sync overview

This source can sync data from the [Ip2whois API](https://www.ip2whois.com/developers-api). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch.

## This Source Supports the Following Streams

- [whois](https://www.ip2whois.com/developers-api)

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |

### Performance considerations

Ip2whois APIs allows you to query up to 500 WHOIS domain name per month.

## Getting started

### Requirements

- [API token](https://www.ip2whois.com/register)

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                                                                         |
| :------ | :--------- | :-------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.2.10 | 2025-02-01 | [52773](https://github.com/airbytehq/airbyte/pull/52773) | Update dependencies |
| 0.2.9 | 2025-01-25 | [52233](https://github.com/airbytehq/airbyte/pull/52233) | Update dependencies |
| 0.2.8 | 2025-01-18 | [51830](https://github.com/airbytehq/airbyte/pull/51830) | Update dependencies |
| 0.2.7 | 2025-01-11 | [51152](https://github.com/airbytehq/airbyte/pull/51152) | Update dependencies |
| 0.2.6 | 2024-12-28 | [50644](https://github.com/airbytehq/airbyte/pull/50644) | Update dependencies |
| 0.2.5 | 2024-12-21 | [50069](https://github.com/airbytehq/airbyte/pull/50069) | Update dependencies |
| 0.2.4 | 2024-12-14 | [49644](https://github.com/airbytehq/airbyte/pull/49644) | Update dependencies |
| 0.2.3 | 2024-12-12 | [47893](https://github.com/airbytehq/airbyte/pull/47893) | Update dependencies |
| 0.2.2 | 2024-10-28 | [47471](https://github.com/airbytehq/airbyte/pull/47471) | Update dependencies |
| 0.2.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.2.0 | 2024-08-15 | [44138](https://github.com/airbytehq/airbyte/pull/44138) | Refactor connector to manifest-only format |
| 0.1.15 | 2024-08-10 | [43644](https://github.com/airbytehq/airbyte/pull/43644) | Update dependencies |
| 0.1.14 | 2024-08-03 | [43158](https://github.com/airbytehq/airbyte/pull/43158) | Update dependencies |
| 0.1.13 | 2024-07-27 | [42611](https://github.com/airbytehq/airbyte/pull/42611) | Update dependencies |
| 0.1.12 | 2024-07-20 | [42216](https://github.com/airbytehq/airbyte/pull/42216) | Update dependencies |
| 0.1.11 | 2024-07-13 | [41860](https://github.com/airbytehq/airbyte/pull/41860) | Update dependencies |
| 0.1.10 | 2024-07-10 | [41445](https://github.com/airbytehq/airbyte/pull/41445) | Update dependencies |
| 0.1.9 | 2024-07-09 | [41310](https://github.com/airbytehq/airbyte/pull/41310) | Update dependencies |
| 0.1.8 | 2024-07-06 | [40966](https://github.com/airbytehq/airbyte/pull/40966) | Update dependencies |
| 0.1.7 | 2024-06-25 | [40342](https://github.com/airbytehq/airbyte/pull/40342) | Update dependencies |
| 0.1.6 | 2024-06-22 | [40157](https://github.com/airbytehq/airbyte/pull/40157) | Update dependencies |
| 0.1.5 | 2024-06-06 | [39283](https://github.com/airbytehq/airbyte/pull/39283) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.4 | 2024-05-20 | [38215](https://github.com/airbytehq/airbyte/pull/38215) | Make connector compatible with builder |
| 0.1.3 | 2024-04-19 | [37180](https://github.com/airbytehq/airbyte/pull/37180) | Upgrade to CDK 0.80.0 and manage dependencies with Poetry. |
| 0.1.2 | 2024-04-15 | [37180](https://github.com/airbytehq/airbyte/pull/37180) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.1 | 2024-04-12 | [37180](https://github.com/airbytehq/airbyte/pull/37180) | schema descriptions |
| 0.1.0   | 2022-10-29 | [#18651](https://github.com/airbytehq/airbyte/pull/18651) | 🎉 New source: Ip2whois [low-code SDK]                                          |

</details>
