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
| 0.2.28 | 2025-01-18 | [51361](https://github.com/airbytehq/airbyte/pull/51361) | Update dependencies |
| 0.2.27 | 2025-01-04 | [50928](https://github.com/airbytehq/airbyte/pull/50928) | Update dependencies |
| 0.2.26 | 2024-12-28 | [50671](https://github.com/airbytehq/airbyte/pull/50671) | Update dependencies |
| 0.2.25 | 2024-12-21 | [50273](https://github.com/airbytehq/airbyte/pull/50273) | Update dependencies |
| 0.2.24 | 2024-12-14 | [49723](https://github.com/airbytehq/airbyte/pull/49723) | Update dependencies |
| 0.2.23 | 2024-12-12 | [49039](https://github.com/airbytehq/airbyte/pull/49039) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.2.22 | 2024-11-04 | [48230](https://github.com/airbytehq/airbyte/pull/48230) | Update dependencies |
| 0.2.21 | 2024-10-29 | [47035](https://github.com/airbytehq/airbyte/pull/47035) | Update dependencies |
| 0.2.20 | 2024-10-12 | [46839](https://github.com/airbytehq/airbyte/pull/46839) | Update dependencies |
| 0.2.19 | 2024-10-05 | [46440](https://github.com/airbytehq/airbyte/pull/46440) | Update dependencies |
| 0.2.18 | 2024-09-28 | [46198](https://github.com/airbytehq/airbyte/pull/46198) | Update dependencies |
| 0.2.17 | 2024-09-21 | [45797](https://github.com/airbytehq/airbyte/pull/45797) | Update dependencies |
| 0.2.16 | 2024-09-14 | [45515](https://github.com/airbytehq/airbyte/pull/45515) | Update dependencies |
| 0.2.15 | 2024-09-07 | [45273](https://github.com/airbytehq/airbyte/pull/45273) | Update dependencies |
| 0.2.14 | 2024-08-31 | [44947](https://github.com/airbytehq/airbyte/pull/44947) | Update dependencies |
| 0.2.13 | 2024-08-24 | [44360](https://github.com/airbytehq/airbyte/pull/44360) | Update dependencies |
| 0.2.12 | 2024-08-12 | [43763](https://github.com/airbytehq/airbyte/pull/43763) | Update dependencies |
| 0.2.11 | 2024-08-10 | [43632](https://github.com/airbytehq/airbyte/pull/43632) | Update dependencies |
| 0.2.10 | 2024-08-03 | [43202](https://github.com/airbytehq/airbyte/pull/43202) | Update dependencies |
| 0.2.9 | 2024-07-27 | [42815](https://github.com/airbytehq/airbyte/pull/42815) | Update dependencies |
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
