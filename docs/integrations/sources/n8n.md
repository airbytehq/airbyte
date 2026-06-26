# N8n

## Sync overview

The n8n source connector extracts data from your n8n workflow automation instance (both Cloud and Self-Hosted). It connects via the n8n API to seamlessly replicate comprehensive operational and metadata records, enabling you to monitor workflow performance, user activity, and manage custom data structures.

The connector supports syncing executions (tracking workflow run history), as well as an expanded catalog of data including workflows, users, credentials, tags, and nested data table contents. Both Full Refresh and Incremental sync modes are supported.

## This Source Supports the Following Streams

- [executions](https://docs.n8n.io/api/api-reference/#tag/Execution/paths/~1executions/get)
- [users](https://docs.n8n.io/api/api-reference/#tag/Users)
- [workflows](https://docs.n8n.io/api/api-reference/#tag/Workflow/paths/~1workflows/get)
- [credentials](https://docs.n8n.io/api/api-reference/#tag/Credential/paths/~1credentials/get)
- [tags](https://docs.n8n.io/api/api-reference/#tag/Tag/paths/~1tags/get)
- [data-tables](https://docs.n8n.io/api/api-reference/#tag/Data-Tables/paths/~1data-tables/get)
- [data-table-rows](https://docs.n8n.io/api/api-reference/#tag/Data-Tables/paths/~1data-tables~1{tableId}~1rows/get)
- [data-table-columns](https://docs.n8n.io/api/api-reference/#tag/Data-Tables/paths/~1data-tables~1{tableId}~1columns/get)

### Stream Details

| Stream | Primary Key | Incremental Cursor | Sync Modes | Description |
| :--- | :--- | :--- | :--- | :--- |
| executions | id | startedAt | Full Refresh, Incremental | History of workflow runs |
| users | id | updatedAt | Full Refresh, Incremental | User profiles and metadata |
| workflows | id | updatedAt | Full Refresh, Incremental | Workflow definitions, node configurations, and parameters |
| credentials | id | updatedAt | Full Refresh, Incremental | Credential names and sharing access (excludes sensitive secrets) |
| tags | id | updatedAt | Full Refresh, Incremental | Workflow tags |
| data-tables | id | updatedAt | Full Refresh, Incremental | Custom n8n data table metadata |
| data-table-rows | - | - | Full Refresh | Individual row data per table (substream of data-tables) |
| data-table-columns | - | - | Full Refresh | Column schemas per table (substream of data-tables) |

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | Yes                  | executions tracks `startedAt`; all other streams track `updatedAt` |

## Getting started

You need a n8n instance or use cloud version

### Create an API key

- Log in to n8n.
- Go to Settings > API.
- Select Create an API key.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                           |
| :------ | :--------- | :------------------------------------------------------- | :-------------------------------- |
| 0.2.12 | 2026-04-28 | [60138](https://github.com/airbytehq/airbyte/pull/60138) | Update dependencies |
| 0.2.11 | 2025-05-03 | [59471](https://github.com/airbytehq/airbyte/pull/59471) | Update dependencies |
| 0.2.10 | 2025-04-27 | [59082](https://github.com/airbytehq/airbyte/pull/59082) | Update dependencies |
| 0.2.9 | 2025-04-19 | [58528](https://github.com/airbytehq/airbyte/pull/58528) | Update dependencies |
| 0.2.8 | 2025-04-12 | [57855](https://github.com/airbytehq/airbyte/pull/57855) | Update dependencies |
| 0.2.7 | 2025-04-05 | [57320](https://github.com/airbytehq/airbyte/pull/57320) | Update dependencies |
| 0.2.6 | 2025-03-29 | [56659](https://github.com/airbytehq/airbyte/pull/56659) | Update dependencies |
| 0.2.5 | 2025-03-22 | [56061](https://github.com/airbytehq/airbyte/pull/56061) | Update dependencies |
| 0.2.4 | 2025-03-08 | [55505](https://github.com/airbytehq/airbyte/pull/55505) | Update dependencies |
| 0.2.3 | 2025-03-01 | [54751](https://github.com/airbytehq/airbyte/pull/54751) | Update dependencies |
| 0.2.2 | 2025-02-22 | [54313](https://github.com/airbytehq/airbyte/pull/54313) | Update dependencies |
| 0.2.1 | 2025-02-15 | [47529](https://github.com/airbytehq/airbyte/pull/47529) | Update dependencies |
| 0.2.0 | 2024-10-06 | [46520](https://github.com/airbytehq/airbyte/pull/46520) | Migrate to Manifest-only |
| 0.1.21 | 2024-10-05 | [46407](https://github.com/airbytehq/airbyte/pull/46407) | Update dependencies |
| 0.1.20 | 2024-09-28 | [46125](https://github.com/airbytehq/airbyte/pull/46125) | Update dependencies |
| 0.1.19 | 2024-09-21 | [45745](https://github.com/airbytehq/airbyte/pull/45745) | Update dependencies |
| 0.1.18 | 2024-09-14 | [45507](https://github.com/airbytehq/airbyte/pull/45507) | Update dependencies |
| 0.1.17 | 2024-09-07 | [45271](https://github.com/airbytehq/airbyte/pull/45271) | Update dependencies |
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
