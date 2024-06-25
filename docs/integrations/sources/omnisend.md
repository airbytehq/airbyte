# Omnisend

## Sync overview

This source can sync data from the [Omnisend API](https://api-docs.omnisend.com/reference/intro). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

- contacts
- campaigns
- carts
- orders
- products

### Features

| Feature           | Supported?\(Yes/No\) |
|:------------------|:---------------------|
| Full Refresh Sync | Yes                  |
| Incremental Sync  | No                   |

### Performance considerations

The connector has a rate limit of 400 requests per 1 minute.

## Getting started

### Requirements

- Omnisend API Key

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject        |
| :------ | :--------- | :------------------------------------------------------- | :------------- |
| 0.1.2 | 2024-06-22 | [40167](https://github.com/airbytehq/airbyte/pull/40167) | Update dependencies |
| 0.1.1 | 2024-05-30 | [38533](https://github.com/airbytehq/airbyte/pull/38533) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-10-25 | [18577](https://github.com/airbytehq/airbyte/pull/18577) | Initial commit |

</details>
