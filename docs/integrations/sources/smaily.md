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
