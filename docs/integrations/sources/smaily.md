# Smaily

## Sync overview

This source can sync data from the [Smaily API](https://smaily.com/help/api/). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

- users
- segments
- campaigns
- templates
- automations
- A/B tests

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |

### Performance considerations

The connector has a rate limit of 5 API requests per second per IP-address.

## Getting started

### Requirements

- Smaily API user username
- Smaily API user password
- Smaily API subdomain

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject        |
| :------ | :--------- | :------------------------------------------------------- | :------------- |
| 0.2.6 | 2024-12-28 | [50774](https://github.com/airbytehq/airbyte/pull/50774) | Update dependencies |
| 0.2.5 | 2024-12-21 | [50330](https://github.com/airbytehq/airbyte/pull/50330) | Update dependencies |
| 0.2.4 | 2024-12-14 | [49791](https://github.com/airbytehq/airbyte/pull/49791) | Update dependencies |
| 0.2.3 | 2024-12-12 | [49394](https://github.com/airbytehq/airbyte/pull/49394) | Update dependencies |
| 0.2.2 | 2024-12-11 | [47809](https://github.com/airbytehq/airbyte/pull/47809) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.2.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.2.0 | 2024-08-14 | [44065](https://github.com/airbytehq/airbyte/pull/44065) | Refactor connector to manifest-only format |
| 0.1.14 | 2024-08-12 | [43872](https://github.com/airbytehq/airbyte/pull/43872) | Update dependencies |
| 0.1.13 | 2024-08-10 | [43664](https://github.com/airbytehq/airbyte/pull/43664) | Update dependencies |
| 0.1.12 | 2024-08-03 | [43175](https://github.com/airbytehq/airbyte/pull/43175) | Update dependencies |
| 0.1.11 | 2024-07-27 | [42777](https://github.com/airbytehq/airbyte/pull/42777) | Update dependencies |
| 0.1.10 | 2024-07-20 | [42227](https://github.com/airbytehq/airbyte/pull/42227) | Update dependencies |
| 0.1.9 | 2024-07-13 | [41838](https://github.com/airbytehq/airbyte/pull/41838) | Update dependencies |
| 0.1.8 | 2024-07-10 | [41579](https://github.com/airbytehq/airbyte/pull/41579) | Update dependencies |
| 0.1.7 | 2024-07-09 | [41093](https://github.com/airbytehq/airbyte/pull/41093) | Update dependencies |
| 0.1.6 | 2024-07-06 | [41010](https://github.com/airbytehq/airbyte/pull/41010) | Update dependencies |
| 0.1.5 | 2024-06-25 | [40460](https://github.com/airbytehq/airbyte/pull/40460) | Update dependencies |
| 0.1.4 | 2024-06-22 | [39959](https://github.com/airbytehq/airbyte/pull/39959) | Update dependencies |
| 0.1.3 | 2024-06-06 | [39176](https://github.com/airbytehq/airbyte/pull/39176) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.2 | 2024-06-06 | [38931](https://github.com/airbytehq/airbyte/pull/38931) | Make compatible with builder |
| 0.1.1 | 2024-05-20 | [38412](https://github.com/airbytehq/airbyte/pull/38412) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-10-25 | [18674](https://github.com/airbytehq/airbyte/pull/18674) | Initial commit |

</details>
