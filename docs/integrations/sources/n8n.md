# N8n

## Sync overview

This source can sync data from [N8n](https://docs.n8n.io/api/). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch.

## This Source Supports the Following Streams

- [executions](https://docs.n8n.io/api/api-reference/#tag/Execution/paths/~1executions/get)

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |

## Getting started

You need a n8n instance or use cloud version

### Create an API key

- Log in to n8n.
- Go to Settings > API.
- Select Create an API key.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                           |
| :------ | :--------- | :------------------------------------------------------- | :-------------------------------- |
| 0.1.16 | 2024-08-31 | [45042](https://github.com/airbytehq/airbyte/pull/45042) | Update dependencies |
| 0.1.15 | 2024-08-24 | [44695](https://github.com/airbytehq/airbyte/pull/44695) | Update dependencies |
| 0.1.14 | 2024-08-17 | [44314](https://github.com/airbytehq/airbyte/pull/44314) | Update dependencies |
| 0.1.13 | 2024-08-12 | [43862](https://github.com/airbytehq/airbyte/pull/43862) | Update dependencies |
| 0.1.12 | 2024-08-10 | [43499](https://github.com/airbytehq/airbyte/pull/43499) | Update dependencies |
| 0.1.11 | 2024-08-03 | [43170](https://github.com/airbytehq/airbyte/pull/43170) | Update dependencies |
| 0.1.10 | 2024-07-27 | [42590](https://github.com/airbytehq/airbyte/pull/42590) | Update dependencies |
| 0.1.9 | 2024-07-20 | [42248](https://github.com/airbytehq/airbyte/pull/42248) | Update dependencies |
| 0.1.8 | 2024-07-13 | [41738](https://github.com/airbytehq/airbyte/pull/41738) | Update dependencies |
| 0.1.7 | 2024-07-10 | [41427](https://github.com/airbytehq/airbyte/pull/41427) | Update dependencies |
| 0.1.6 | 2024-07-09 | [41191](https://github.com/airbytehq/airbyte/pull/41191) | Update dependencies |
| 0.1.5 | 2024-07-06 | [40861](https://github.com/airbytehq/airbyte/pull/40861) | Update dependencies |
| 0.1.4 | 2024-06-25 | [40317](https://github.com/airbytehq/airbyte/pull/40317) | Update dependencies |
| 0.1.3 | 2024-06-22 | [40124](https://github.com/airbytehq/airbyte/pull/40124) | Update dependencies |
| 0.1.2 | 2024-06-06 | [39273](https://github.com/airbytehq/airbyte/pull/39273) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.1 | 2024-05-21 | [38482](https://github.com/airbytehq/airbyte/pull/38482) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-11-08 | [18745](https://github.com/airbytehq/airbyte/pull/18745) | 🎉 New Source: N8n [low-code cdk] |

</details>
