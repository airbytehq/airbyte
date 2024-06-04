# Dixa

## Sync overview

This source can sync data for the [Dixa conversation_export API](https://support.dixa.help/en/articles/174-export-conversations-via-api). It supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Output schema

This Source is capable of syncing the following Streams:

- [Conversation export](https://support.dixa.help/en/articles/174-export-conversations-via-api)

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--------------- | :----------- | :---- |
| `string`         | `string`     |       |
| `int`            | `integer`    |       |
| `timestamp`      | `integer`    |       |
| `array`          | `array`      |       |

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | Yes                  |       |
| Namespaces        | No                   |       |

### Performance considerations

The connector is limited by standard Dixa conversation_export API [limits](https://support.dixa.help/en/articles/174-export-conversations-via-api). It should not run into limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

When using the connector, keep in mind that increasing the `batch_size` parameter will decrease the number of requests sent to the API, but increase the response and processing time.

## Getting started

### Requirements

- Dixa API token

### Setup guide

1. Generate an API token using the [Dixa documentation](https://support.dixa.help/en/articles/259-how-to-generate-an-api-token).
2. Define a `start_timestamp`: the connector will pull records with `updated_at >= start_timestamp`
3. Define a `batch_size`: this represents the number of days which will be batched in a single request.

   Keep the performance consideration above in mind

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                               |
| :------ | :--------- | :------------------------------------------------------- | :-------------------------------------------------------------------- |
| 0.3.0   | 2023-10-17 | [30994](https://github.com/airbytehq/airbyte/pull/30994) | Migrate to Low-code Framework                                         |
| 0.2.0   | 2023-06-08 | [25103](https://github.com/airbytehq/airbyte/pull/25103) | Add fields to `conversation_export` stream                            |
| 0.1.3   | 2022-07-07 | [14437](https://github.com/airbytehq/airbyte/pull/14437) | 🎉 Source Dixa: bump version 0.1.3                                    |
| 0.1.2   | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499)   | Remove base-python dependencies                                       |
| 0.1.1   | 2021-08-12 | [5367](https://github.com/airbytehq/airbyte/pull/5367)   | Migrated to CI Sandbox, refactorred code structure for future support |
| 0.1.0   | 2021-07-07 | [4358](https://github.com/airbytehq/airbyte/pull/4358)   | New source                                                            |

</details>