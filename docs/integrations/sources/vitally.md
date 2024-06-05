# Vitally

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

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                      |
| :------ | :--------- | :------------------------------------------------------- | :--------------------------- |
| 0.1.1 | 2024-05-20 | [38446](https://github.com/airbytehq/airbyte/pull/38446) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-10-27 | [18545](https://github.com/airbytehq/airbyte/pull/18545) | Add Vitally Source Connector |

</details>