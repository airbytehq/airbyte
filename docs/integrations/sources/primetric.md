# Primetric

## Overview

The Primetric source currently supports Full Refresh syncs only. This means that all contents for all chosen streams will be replaced with every sync.

### Output schema

This Source is capable of syncing the following core Streams:

- [Assignments](https://developer.primetric.com/#614ec96a-3a6e-4124-8e17-2a47b9fd2ab2)
- [Capacities](https://developer.primetric.com/#62d3dac7-130c-4251-abd1-fc4143e6135f)
- [Employees](https://developer.primetric.com/#2d3b810d-0bdf-4076-b635-bcb113c12dd2)
- [Hashtags](https://developer.primetric.com/#76dc7d53-f7ef-4e32-90c1-0bec3ee2954b)
- [Organization Clients](https://developer.primetric.com/#2bc0ae2d-ded2-4cad-b801-ce5b0e16dd0c)
- [Organization Company Groups](https://developer.primetric.com/#76fbffd3-9410-41cf-b1c7-c28f8934259b)
- [Organization Departments](https://developer.primetric.com/#e7b85cda-6a7e-4b5c-81eb-38ef22b9476b)
- [Organization Identity Providers](https://developer.primetric.com/#6194d5dd-a461-48ca-a98c-b43e22a8eaf9)
- [Organization Positions](https://developer.primetric.com/#8bb3e61c-8309-47fa-a11b-e809b5b6fa85)
- [Organization Rag Scopes](https://developer.primetric.com/#ade4f7f0-5afe-464d-a882-af0752d8b812)
- [Organization Roles](https://developer.primetric.com/#dbd3780e-a0bd-49ba-b55c-df2ac34cc59f)
- [Organization Seniorities](https://developer.primetric.com/#d87953ac-a26d-419f-8b68-290551acab66)
- [Organization Tags](https://developer.primetric.com/#04573d40-054e-480b-9b4d-af61152a8a80)
- [Organization Teams](https://developer.primetric.com/#1fa80784-7955-41bb-b0cd-7ea0a2791936)
- [Organization Timeoff Types](https://developer.primetric.com/#e6dd9b98-66ec-4854-9a25-6f6f6f34399c)
- [People](https://developer.primetric.com/#21d5b65a-2f0d-464a-a6c3-8026f0096b83)
- [Projects](https://developer.primetric.com/#2dbef41d-2b82-4697-a5b8-15b253077703)
- [Projects Vacancies](https://developer.primetric.com/#c43bef20-60c4-4f83-bbf0-0aa55c05d4d9)
- [Rag Ratings](https://developer.primetric.com/#1dfc0346-4f47-4e32-b602-00700404f881)
- [Skills](https://developer.primetric.com/#f60a6ff4-b301-4bff-9a7d-a7694572bfb4)
- [Timeoffs](https://developer.primetric.com/#daecfab4-1f4a-4744-b6eb-49f291b6092c)
- [Worklogs](https://developer.primetric.com/#cd27074c-2918-4894-b656-c56d38527981)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature                       | Supported? |     |
| :---------------------------- | :--------- | :-- |
| Full Refresh Sync             | Yes        |     |
| Incremental Sync              | No         |     |
| Replicate Incremental Deletes | No         |     |
| SSL connection                | Yes        |     |
| Namespaces                    | No         |     |

## Getting started

Primetric facilitates resource planning. With it you can manage your employee's skills and schedule assignment of
your employees to the right projects.

### Requirements

- Primetric [client secret](https://app.primetric.com/administrator/integrations)
- Primetric client id

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                 |
| :------ | :--------- | :------------------------------------------------------- | :---------------------- |
| 1.1.8 | 2025-02-08 | [52958](https://github.com/airbytehq/airbyte/pull/52958) | Update dependencies |
| 1.1.7 | 2025-01-25 | [52523](https://github.com/airbytehq/airbyte/pull/52523) | Update dependencies |
| 1.1.6 | 2025-01-18 | [51891](https://github.com/airbytehq/airbyte/pull/51891) | Update dependencies |
| 1.1.5 | 2025-01-11 | [51339](https://github.com/airbytehq/airbyte/pull/51339) | Update dependencies |
| 1.1.4 | 2025-01-04 | [50287](https://github.com/airbytehq/airbyte/pull/50287) | Update dependencies |
| 1.1.3 | 2024-12-14 | [49670](https://github.com/airbytehq/airbyte/pull/49670) | Update dependencies |
| 1.1.2 | 2024-12-12 | [43808](https://github.com/airbytehq/airbyte/pull/43808) | Update dependencies |
| 1.1.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 1.1.0 | 2024-08-14 | [44083](https://github.com/airbytehq/airbyte/pull/44083) | Refactor connector to manifest-only format |
| 1.0.1 | 2024-06-04 | [38956](https://github.com/airbytehq/airbyte/pull/38956) | [autopull] Upgrade base image to v1.2.1 |
| 1.0.0 | 2024-04-01 | [36508](https://github.com/airbytehq/airbyte/pull/36508) | Migrate to low code cdk |
| 0.1.0 | 2022-09-05 | [15880](https://github.com/airbytehq/airbyte/pull/15880) | Initial implementation |

</details>
