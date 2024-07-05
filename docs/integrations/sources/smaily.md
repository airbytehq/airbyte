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
| 0.1.3 | 2024-06-06 | [39176](https://github.com/airbytehq/airbyte/pull/39176) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.2 | 2024-06-06 | [38931](https://github.com/airbytehq/airbyte/pull/38931) | Make compatible with builder |
| 0.1.1 | 2024-05-20 | [38412](https://github.com/airbytehq/airbyte/pull/38412) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-10-25 | [18674](https://github.com/airbytehq/airbyte/pull/18674) | Initial commit |

</details>
