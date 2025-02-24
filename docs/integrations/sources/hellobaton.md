# Hellobaton

## Sync overview

This source can sync data from the [hellobaton API](https://app.hellobaton.com/api/redoc/). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

- activity
- companies
- milestones
- phases
- project_attachments
- projects
- task_attachemnts
- tasks
- templates
- time_entries
- users

Hellobaton adds new streams fairly regularly please submit an issue or PR if this project doesn't support required streams for your use case.

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--------------- | :----------- | :---- |
| `string`         | `string`     |       |
| `integer`        | `integer`    |       |
| `number`         | `number`     |       |
| `array`          | `array`      |       |
| `object`         | `object`     |       |

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |
| Namespaces        | No                   |       |

### Performance considerations

The connector is rate limited at 1000 requests per minute per api key. If you find yourself receiving errors contact your customer success manager and request a rate limit increase.

## Getting started

### Requirements

- Hellobaton account
- Hellobaton api key

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                             |
| :------ | :--------- | :------------------------------------------------------- | :---------------------------------- |
| 0.3.16 | 2025-02-22 | [54347](https://github.com/airbytehq/airbyte/pull/54347) | Update dependencies |
| 0.3.15 | 2025-02-15 | [53806](https://github.com/airbytehq/airbyte/pull/53806) | Update dependencies |
| 0.3.14 | 2025-02-08 | [53286](https://github.com/airbytehq/airbyte/pull/53286) | Update dependencies |
| 0.3.13 | 2025-02-01 | [52772](https://github.com/airbytehq/airbyte/pull/52772) | Update dependencies |
| 0.3.12 | 2025-01-25 | [52292](https://github.com/airbytehq/airbyte/pull/52292) | Update dependencies |
| 0.3.11 | 2025-01-18 | [51810](https://github.com/airbytehq/airbyte/pull/51810) | Update dependencies |
| 0.3.10 | 2025-01-11 | [51203](https://github.com/airbytehq/airbyte/pull/51203) | Update dependencies |
| 0.3.9 | 2025-01-04 | [50657](https://github.com/airbytehq/airbyte/pull/50657) | Update dependencies |
| 0.3.8 | 2024-12-21 | [50122](https://github.com/airbytehq/airbyte/pull/50122) | Update dependencies |
| 0.3.7 | 2024-12-14 | [49643](https://github.com/airbytehq/airbyte/pull/49643) | Update dependencies |
| 0.3.6 | 2024-12-12 | [49245](https://github.com/airbytehq/airbyte/pull/49245) | Update dependencies |
| 0.3.5 | 2024-12-11 | [48981](https://github.com/airbytehq/airbyte/pull/48981) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.3.4 | 2024-11-05 | [48359](https://github.com/airbytehq/airbyte/pull/48359) | Revert to source-declarative-manifest v5.17.0 |
| 0.3.3 | 2024-11-05 | [48320](https://github.com/airbytehq/airbyte/pull/48320) | Update dependencies |
| 0.3.2 | 2024-10-22 | [47236](https://github.com/airbytehq/airbyte/pull/47236) | Update dependencies |
| 0.3.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.3.0 | 2024-08-15 | [44142](https://github.com/airbytehq/airbyte/pull/44142) | Refactor connector to manifest-only format |
| 0.2.14 | 2024-08-12 | [43779](https://github.com/airbytehq/airbyte/pull/43779) | Update dependencies |
| 0.2.13 | 2024-08-10 | [43465](https://github.com/airbytehq/airbyte/pull/43465) | Update dependencies |
| 0.2.12 | 2024-08-03 | [43233](https://github.com/airbytehq/airbyte/pull/43233) | Update dependencies |
| 0.2.11 | 2024-07-27 | [42678](https://github.com/airbytehq/airbyte/pull/42678) | Update dependencies |
| 0.2.10 | 2024-07-20 | [42232](https://github.com/airbytehq/airbyte/pull/42232) | Update dependencies |
| 0.2.9 | 2024-07-13 | [41888](https://github.com/airbytehq/airbyte/pull/41888) | Update dependencies |
| 0.2.8 | 2024-07-10 | [41538](https://github.com/airbytehq/airbyte/pull/41538) | Update dependencies |
| 0.2.7 | 2024-07-09 | [41277](https://github.com/airbytehq/airbyte/pull/41277) | Update dependencies |
| 0.2.6 | 2024-07-06 | [40838](https://github.com/airbytehq/airbyte/pull/40838) | Update dependencies |
| 0.2.5 | 2024-06-26 | [40445](https://github.com/airbytehq/airbyte/pull/40445) | Update dependencies |
| 0.2.4 | 2024-06-22 | [40195](https://github.com/airbytehq/airbyte/pull/40195) | Update dependencies |
| 0.2.3 | 2024-06-15 | [39113](https://github.com/airbytehq/airbyte/pull/39113) | Make compatible with builder |
| 0.2.2 | 2024-06-06 | [39189](https://github.com/airbytehq/airbyte/pull/39189) | [autopull] Upgrade base image to v1.2.2 |
| 0.2.1 | 2024-05-21 | [38507](https://github.com/airbytehq/airbyte/pull/38507) | [autopull] base image + poetry + up_to_date |
| 0.2.0 | 2023-08-19 | [29490](https://github.com/airbytehq/airbyte/pull/29490) | Migrate CDK from Python to Low Code |
| 0.1.0 | 2022-01-14 | [8461](https://github.com/airbytehq/airbyte/pull/8461) | 🎉 New Source: Hellobaton |

</details>
