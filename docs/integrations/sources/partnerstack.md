# Partnerstack

## Sync overview

The Partnerstack source supports both Full Refresh only.

This source can sync data for the [Partnerstack API](https://docs.partnerstack.com/reference).

### Output schema

This Source is capable of syncing the following core Streams:

- [Customers](https://docs.partnerstack.com/reference/get_v2-customers-2)
- [Deals](https://docs.partnerstack.com/reference/get_v2-deals)
- [Groups](https://docs.partnerstack.com/reference/get_v2-groups)
- [Leads](https://docs.partnerstack.com/reference/get_v2-leads)
- [Partnerships](https://docs.partnerstack.com/reference/get_v2-partnerships-2)
- [Rewards](https://docs.partnerstack.com/reference/get_v2-rewards-2)
- [Transactions](https://docs.partnerstack.com/reference/get_v2-transactions-2)

### Features

| Feature                   | Supported?\(Yes/No\) | Notes |
| :------------------------ | :------------------- | :---- |
| Full Refresh Sync         | Yes                  |       |
| Incremental - Append Sync | No                   |       |
| Namespaces                | No                   |       |

### Performance considerations

The Partnerstack connector should not run into Partnerstack API limitations under normal usage.

## Requirements

- **Partnerstack API keys**. See the [Partnerstack docs](https://docs.partnerstack.com/reference/auth) for information on how to obtain the API keys.

## Changelog

| Version | Date       | Pull Request                                         | Subject                           |
| :------ | :--------- | :--------------------------------------------------- | :-------------------------------- |
| 0.1.3 | 2024-04-19 | [0](https://github.com/airbytehq/airbyte/pull/0) | Manage dependencies with Poetry. |
| 0.1.2 | 2024-04-15 | [37218](https://github.com/airbytehq/airbyte/pull/37218) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.1 | 2024-04-12 | [37218](https://github.com/airbytehq/airbyte/pull/37218) | schema descriptions |
| 0.1.0   | 2022-10-27 | [XXX](https://github.com/airbytehq/airbyte/pull/XXX) | Add Partnerstack Source Connector |
