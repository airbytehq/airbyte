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
