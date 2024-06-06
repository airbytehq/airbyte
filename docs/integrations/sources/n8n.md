# N8n

## Sync overview

This source can sync data from [N8n](https://docs.n8n.io/api/). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch.

## This Source Supports the Following Streams

- [execitions](https://docs.n8n.io/api/api-reference/#tag/Execution/paths/~1executions/get)

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
| 0.1.1 | 2024-05-21 | [38482](https://github.com/airbytehq/airbyte/pull/38482) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-11-08 | [18745](https://github.com/airbytehq/airbyte/pull/18745) | 🎉 New Source: N8n [low-code cdk] |

</details>