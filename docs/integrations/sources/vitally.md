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

| Version | Date       | Pull Request                                             | Subject                                     |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------ |
| 0.3.2 | 2025-02-22 | [54500](https://github.com/airbytehq/airbyte/pull/54500) | Update dependencies |
| 0.3.1 | 2025-02-15 | [47470](https://github.com/airbytehq/airbyte/pull/47470) | Update dependencies |
| 0.3.0 | 2025-02-12 | [53648](https://github.com/airbytehq/airbyte/pull/53648) | Add support for custom domain. |
| 0.2.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.2.0 | 2024-08-14 | [44049](https://github.com/airbytehq/airbyte/pull/44049) | Refactor connector to manifest-only format |
| 0.1.13 | 2024-08-12 | [43850](https://github.com/airbytehq/airbyte/pull/43850) | Update dependencies |
| 0.1.12 | 2024-08-10 | [43505](https://github.com/airbytehq/airbyte/pull/43505) | Update dependencies |
| 0.1.11 | 2024-08-03 | [43189](https://github.com/airbytehq/airbyte/pull/43189) | Update dependencies |
| 0.1.10 | 2024-07-27 | [42607](https://github.com/airbytehq/airbyte/pull/42607) | Update dependencies |
| 0.1.9 | 2024-07-20 | [41877](https://github.com/airbytehq/airbyte/pull/41877) | Update dependencies |
| 0.1.8 | 2024-07-10 | [41378](https://github.com/airbytehq/airbyte/pull/41378) | Update dependencies |
| 0.1.7 | 2024-07-09 | [41223](https://github.com/airbytehq/airbyte/pull/41223) | Update dependencies |
| 0.1.6 | 2024-07-06 | [40808](https://github.com/airbytehq/airbyte/pull/40808) | Update dependencies |
| 0.1.5 | 2024-06-25 | [40287](https://github.com/airbytehq/airbyte/pull/40287) | Update dependencies |
| 0.1.4 | 2024-06-22 | [40189](https://github.com/airbytehq/airbyte/pull/40189) | Update dependencies |
| 0.1.3 | 2024-06-25 | [38605](https://github.com/airbytehq/airbyte/pull/38605) | Make compatible with builder |
| 0.1.2 | 2024-06-06 | [39203](https://github.com/airbytehq/airbyte/pull/39203) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.1 | 2024-05-20 | [38446](https://github.com/airbytehq/airbyte/pull/38446) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-10-27 | [18545](https://github.com/airbytehq/airbyte/pull/18545) | Add Vitally Source Connector |

</details>
