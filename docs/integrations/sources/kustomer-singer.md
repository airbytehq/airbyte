# Kustomer

:::warning

## Deprecation Notice

The Kustomer source connector is scheduled for deprecation on March 5th, 2024 due to incompatibility with upcoming platform updates as we prepare to launch Airbyte 1.0. This means it will no longer be supported or available for use in Airbyte.

This connector does not support new per-stream features which are vital for ensuring data integrity in Airbyte's synchronization processes. Without these capabilities, we cannot enforce our standards of reliability and correctness for data syncing operations.

### Recommended Actions

Users who still wish to sync data from this connector are advised to explore creating a custom connector as an alternative to continue their data synchronization needs. For guidance, please visit our [Custom Connector documentation](https://docs.airbyte.com/connector-development/).

:::

## Sync overview

The Kustomer source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This source can sync data for the [Kustomer API](https://developer.kustomer.com/kustomer-api-docs).

This Source Connector is based on a [Singer tap](https://github.com/singer-io/tap-kustomer).

### Output schema

This Source is capable of syncing the following core Streams:

- [Conversations](https://developer.kustomer.com/kustomer-api-docs/reference/conversations)
- [Customers](https://developer.kustomer.com/kustomer-api-docs/reference/customers)
- [KObjects](https://developer.kustomer.com/kustomer-api-docs/reference/kobjects-custom-objects)
- [Messages](https://developer.kustomer.com/kustomer-api-docs/reference/messages)
- [Notes](https://developer.kustomer.com/kustomer-api-docs/reference/notes)
- [Shortcuts](https://developer.kustomer.com/kustomer-api-docs/reference/shortcuts)
- [Tags](https://developer.kustomer.com/kustomer-api-docs/reference/tags-knowledge-base)
- [Teams](https://developer.kustomer.com/kustomer-api-docs/reference/teams)
- [Users](https://developer.kustomer.com/kustomer-api-docs/reference/users)

### Features

| Feature                   | Supported?\(Yes/No\) | Notes |
| :------------------------ | :------------------- | :---- |
| Full Refresh Sync         | Yes                  |       |
| Incremental - Append Sync | Yes                  |       |
| Namespaces                | No                   |       |

### Performance considerations

Kustomer has some [rate limit restrictions](https://developer.kustomer.com/kustomer-api-docs/reference/rate-limiting).

## Requirements

- **Kustomer API token**. See the [Kustomer docs](https://help.kustomer.com/api-keys-SJs5YTIWX) for information on how to obtain an API token.

## Changelog

| Version | Date       | Pull Request                                           | Subject                                                                           |
| :------ | :--------- | :----------------------------------------------------- | :-------------------------------------------------------------------------------- |
| 0.1.2   | 2021-12-25 | [8578](https://github.com/airbytehq/airbyte/pull/8578) | Update fields in source-connectors specifications                                 |
| 0.1.1   | 2021-12-22 | [8738](https://github.com/airbytehq/airbyte/pull/8738) | Deleted `user-agent`, `date_window_size`, `page_size_limit` from `spec.json` file |
| 0.1.0   | 2021-07-22 | [4550](https://github.com/airbytehq/airbyte/pull/4550) | Add Kustomer Source Connector                                                     |
