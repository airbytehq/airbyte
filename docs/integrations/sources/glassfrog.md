# Glassfrog

## Sync overview

The Glassfrog source supports only Full Refresh syncs. This source can sync data for the [Glassfrog API](https://documenter.getpostman.com/view/1014385/glassfrog-api-v3/2SJViY).

This Source Connector is based on the [Airbyte CDK](https://docs.airbyte.com/connector-development/cdk-python).

### Output schema

This Source is capable of syncing the following Streams:

- [Assignments](https://documenter.getpostman.com/view/1014385/glassfrog-api-v3/2SJViY#db2934bd-8c07-1951-b273-51fbc2dc6422)
- [Checklist items](https://documenter.getpostman.com/view/1014385/glassfrog-api-v3/2SJViY#a81716d4-b492-79ff-1348-9048fd9dc527)
- [Circles](https://documenter.getpostman.com/view/1014385/glassfrog-api-v3/2SJViY#ed696857-c3d8-fba1-a174-fbe63de07798)
- [Custom fields](https://documenter.getpostman.com/view/1014385/glassfrog-api-v3/2SJViY#901f8ec2-a986-0291-2fa2-281c16622107)
- [Metrics](https://documenter.getpostman.com/view/1014385/glassfrog-api-v3/2SJViY#00d4f5fb-d6e5-5521-a77d-bdce50a9fb84)
- [People](https://documenter.getpostman.com/view/1014385/glassfrog-api-v3/2SJViY#78b74b9f-72b7-63fc-a18c-18518932944b)
- [Projects](https://documenter.getpostman.com/view/1014385/glassfrog-api-v3/2SJViY#110bde88-a319-ae9c-077a-9752fd2f0843)
- [Roles](https://documenter.getpostman.com/view/1014385/glassfrog-api-v3/2SJViY#d1f31f7a-1d42-8c86-be1d-a36e640bf993)

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--------------- | :----------- | :---- |
| `string`         | `string`     |       |
| `number`         | `number`     |       |
| `array`          | `array`      |       |
| `object`         | `object`     |       |

### Features

| Feature                   | Supported?\(Yes/No\) | Notes |
| :------------------------ | :------------------- | :---- |
| Full Refresh Sync         | Yes                  |       |
| Incremental - Append Sync | No                   |       |
| Namespaces                | No                   |       |

## Getting started

1. Sign in at `app.glassfrog.com`.
2. Go to `Profile & Settings`.
3. In the API tab, enter the label for your new API key (e.g. `Airbyte`) and clik on the button `Create new API Key`.
4. Use the created secret key to configure your source!

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.3.10 | 2025-02-01 | [52828](https://github.com/airbytehq/airbyte/pull/52828) | Update dependencies |
| 0.3.9 | 2025-01-25 | [52369](https://github.com/airbytehq/airbyte/pull/52369) | Update dependencies |
| 0.3.8 | 2025-01-18 | [51658](https://github.com/airbytehq/airbyte/pull/51658) | Update dependencies |
| 0.3.7 | 2025-01-11 | [51101](https://github.com/airbytehq/airbyte/pull/51101) | Update dependencies |
| 0.3.6 | 2024-12-28 | [50543](https://github.com/airbytehq/airbyte/pull/50543) | Update dependencies |
| 0.3.5 | 2024-12-21 | [50052](https://github.com/airbytehq/airbyte/pull/50052) | Update dependencies |
| 0.3.4 | 2024-12-14 | [49471](https://github.com/airbytehq/airbyte/pull/49471) | Update dependencies |
| 0.3.3 | 2024-12-12 | [47782](https://github.com/airbytehq/airbyte/pull/47782) | Update dependencies |
| 0.3.2 | 2024-10-28 | [47519](https://github.com/airbytehq/airbyte/pull/47519) | Update dependencies |
| 0.3.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.3.0 | 2024-08-15 | [44146](https://github.com/airbytehq/airbyte/pull/44146) | Refactor connector to manifest-only format |
| 0.2.15 | 2024-08-10 | [43676](https://github.com/airbytehq/airbyte/pull/43676) | Update dependencies |
| 0.2.14 | 2024-08-03 | [43261](https://github.com/airbytehq/airbyte/pull/43261) | Update dependencies |
| 0.2.13 | 2024-07-27 | [42636](https://github.com/airbytehq/airbyte/pull/42636) | Update dependencies |
| 0.2.12 | 2024-07-20 | [41866](https://github.com/airbytehq/airbyte/pull/41866) | Update dependencies |
| 0.2.11 | 2024-07-10 | [41400](https://github.com/airbytehq/airbyte/pull/41400) | Update dependencies |
| 0.2.10 | 2024-07-09 | [41169](https://github.com/airbytehq/airbyte/pull/41169) | Update dependencies |
| 0.2.9 | 2024-07-06 | [40925](https://github.com/airbytehq/airbyte/pull/40925) | Update dependencies |
| 0.2.8 | 2024-06-25 | [40279](https://github.com/airbytehq/airbyte/pull/40279) | Update dependencies |
| 0.2.7 | 2024-06-22 | [40135](https://github.com/airbytehq/airbyte/pull/40135) | Update dependencies |
| 0.2.6 | 2024-06-04 | [39056](https://github.com/airbytehq/airbyte/pull/39056) | [autopull] Upgrade base image to v1.2.1 |
| 0.2.5 | 2024-05-20 | [38323](https://github.com/airbytehq/airbyte/pull/38323) | Make compatibility with builder |
| 0.2.4 | 2024-04-19 | [37167](https://github.com/airbytehq/airbyte/pull/37167) | Updating to 0.80.0 CDK |
| 0.2.3 | 2024-04-18 | [37167](https://github.com/airbytehq/airbyte/pull/37167) | Manage dependencies with Poetry. |
| 0.2.2 | 2024-04-15 | [37167](https://github.com/airbytehq/airbyte/pull/37167) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.2.1 | 2024-04-12 | [37167](https://github.com/airbytehq/airbyte/pull/37167) | schema descriptions |
| 0.2.0 | 2023-08-10 | [29306](https://github.com/airbytehq/airbyte/pull/29306) | Migrated to LowCode CDK |
| 0.1.1 | 2023-08-15 | [13868](https://github.com/airbytehq/airbyte/pull/13868) | Fix schema and tests |
| 0.1.0 | 2022-06-16 | [13868](https://github.com/airbytehq/airbyte/pull/13868) | Add Native Glassfrog Source Connector |

</details>
