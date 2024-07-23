# Public APIs

## Sync overview

This source can sync data for the [Public APIs](https://api.publicapis.org/) REST API. It supports only Full Refresh syncs.

### Output schema

This Source is capable of syncing the following Streams:

- [Services](https://api.publicapis.org#get-entries)
- [Categories](https://api.publicapis.org#get-categories)

### Data type mapping

| Integration Type    | Airbyte Type | Notes |
| :------------------ | :----------- | :---- |
| `string`            | `string`     |       |
| `integer`, `number` | `number`     |       |
| `boolean`           | `boolean`    |       |

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |
| SSL connection    | Yes                  |
| Namespaces        | No                   |       |
| Pagination        | No                   |       |

## Getting started

### Requirements

There is no requirements to setup this source.

### Setup guide

This source requires no setup.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject              |
| :------ | :--------- | :------------------------------------------------------- | :------------------- |
| 0.2.8 | 2024-07-20 | [42379](https://github.com/airbytehq/airbyte/pull/42379) | Update dependencies |
| 0.2.7 | 2024-07-13 | [41750](https://github.com/airbytehq/airbyte/pull/41750) | Update dependencies |
| 0.2.6 | 2024-07-10 | [41359](https://github.com/airbytehq/airbyte/pull/41359) | Update dependencies |
| 0.2.5 | 2024-07-09 | [41218](https://github.com/airbytehq/airbyte/pull/41218) | Update dependencies |
| 0.2.4 | 2024-07-06 | [40998](https://github.com/airbytehq/airbyte/pull/40998) | Update dependencies |
| 0.2.3 | 2024-06-25 | [40276](https://github.com/airbytehq/airbyte/pull/40276) | Update dependencies |
| 0.2.2 | 2024-06-22 | [40073](https://github.com/airbytehq/airbyte/pull/40073) | Update dependencies |
| 0.2.1 | 2024-05-20 | [38377](https://github.com/airbytehq/airbyte/pull/38377) | [autopull] base image + poetry + up_to_date |
| 0.2.0 | 2023-06-15 | [29391](https://github.com/airbytehq/airbyte/pull/29391) | Migrated to Low Code |
| 0.1.0 | 2022-10-28 | [18471](https://github.com/airbytehq/airbyte/pull/18471) | Initial Release |

</details>
