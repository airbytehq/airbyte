# Vittally

## Sync overview

The Vitally source supports both Full Refresh only.

This source can sync data for the [Vitally API](https://docs.vitally.io/pushing-data-to-vitally/rest-api).

### Output schema

This Source is capable of syncing the following core Streams:

- [Accounts](https://docs.vitally.io/pushing-data-to-vitally/rest-api/accounts)
- [Admins](https://docs.vitally.io/pushing-data-to-vitally/rest-api/admins)
- [Conversations](https://docs.vitally.io/pushing-data-to-vitally/rest-api/conversations)
- [Notes](https://docs.vitally.io/pushing-data-to-vitally/rest-api/notes)
- [NPS Responses](https://docs.vitally.io/pushing-data-to-vitally/rest-api/nps-responses)
- [Tasks](https://docs.vitally.io/pushing-data-to-vitally/rest-api/tasks)
- [Users](https://docs.vitally.io/pushing-data-to-vitally/rest-api/users)

### Features

| Feature                   | Supported?\(Yes/No\) | Notes |
| :------------------------ | :------------------- | :---- |
| Full Refresh Sync         | Yes                  |       |
| Incremental - Append Sync | No                   |       |
| Namespaces                | No                   |       |

### Performance considerations

The Vitally connector should not run into Vitally API limitations under normal usage.

## Requirements

- **Vitaly API key**. See the [Vitally docs](https://docs.vitally.io/pushing-data-to-vitally/rest-api#authentication) for information on how to obtain an API key.

## Changelog

| Version | Date       | Pull Request                                             | Subject                      |
| :------ | :--------- | :------------------------------------------------------- | :--------------------------- |
| 0.1.2 | 2024-04-15 | [37284](https://github.com/airbytehq/airbyte/pull/37284) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.1 | 2024-04-12 | [37284](https://github.com/airbytehq/airbyte/pull/37284) | schema descriptions |
| 0.1.0   | 2022-10-27 | [18545](https://github.com/airbytehq/airbyte/pull/18545) | Add Vitally Source Connector |
