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
| 0.4.8 | 2025-02-01 | [52813](https://github.com/airbytehq/airbyte/pull/52813) | Update dependencies |
| 0.4.7 | 2025-01-25 | [52323](https://github.com/airbytehq/airbyte/pull/52323) | Update dependencies |
| 0.4.6 | 2025-01-18 | [51691](https://github.com/airbytehq/airbyte/pull/51691) | Update dependencies |
| 0.4.5 | 2025-01-11 | [51116](https://github.com/airbytehq/airbyte/pull/51116) | Update dependencies |
| 0.4.4 | 2024-12-28 | [50546](https://github.com/airbytehq/airbyte/pull/50546) | Update dependencies |
| 0.4.3 | 2024-12-21 | [50028](https://github.com/airbytehq/airbyte/pull/50028) | Update dependencies |
| 0.4.2 | 2024-12-14 | [49497](https://github.com/airbytehq/airbyte/pull/49497) | Update dependencies |
| 0.4.1 | 2024-12-12 | [49149](https://github.com/airbytehq/airbyte/pull/49149) | Update dependencies |
| 0.4.0 | 2024-08-27 | [44818](https://github.com/airbytehq/airbyte/pull/44818) | Refactor connector to manifest-only format |
| 0.3.14 | 2024-08-24 | [44666](https://github.com/airbytehq/airbyte/pull/44666) | Update dependencies |
| 0.3.13 | 2024-08-17 | [44328](https://github.com/airbytehq/airbyte/pull/44328) | Update dependencies |
| 0.3.12 | 2024-08-12 | [43871](https://github.com/airbytehq/airbyte/pull/43871) | Update dependencies |
| 0.3.11 | 2024-08-10 | [43474](https://github.com/airbytehq/airbyte/pull/43474) | Update dependencies |
| 0.3.10 | 2024-08-03 | [43088](https://github.com/airbytehq/airbyte/pull/43088) | Update dependencies |
| 0.3.9 | 2024-07-27 | [42679](https://github.com/airbytehq/airbyte/pull/42679) | Update dependencies |
| 0.3.8 | 2024-07-20 | [42156](https://github.com/airbytehq/airbyte/pull/42156) | Update dependencies |
| 0.3.7 | 2024-07-13 | [41805](https://github.com/airbytehq/airbyte/pull/41805) | Update dependencies |
| 0.3.6 | 2024-07-10 | [41484](https://github.com/airbytehq/airbyte/pull/41484) | Update dependencies |
| 0.3.5 | 2024-07-09 | [41198](https://github.com/airbytehq/airbyte/pull/41198) | Update dependencies |
| 0.3.4 | 2024-07-06 | [40776](https://github.com/airbytehq/airbyte/pull/40776) | Update dependencies |
| 0.3.3 | 2024-06-26 | [40371](https://github.com/airbytehq/airbyte/pull/40371) | Update dependencies |
| 0.3.2 | 2024-06-22 | [40119](https://github.com/airbytehq/airbyte/pull/40119) | Update dependencies |
| 0.3.1 | 2024-05-21 | [38481](https://github.com/airbytehq/airbyte/pull/38481) | [autopull] base image + poetry + up_to_date |
| 0.3.0 | 2023-10-17 | [30994](https://github.com/airbytehq/airbyte/pull/30994) | Migrate to Low-code Framework |
| 0.2.0 | 2023-06-08 | [25103](https://github.com/airbytehq/airbyte/pull/25103) | Add fields to `conversation_export` stream |
| 0.1.3 | 2022-07-07 | [14437](https://github.com/airbytehq/airbyte/pull/14437) | 🎉 Source Dixa: bump version 0.1.3 |
| 0.1.2 | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499) | Remove base-python dependencies |
| 0.1.1 | 2021-08-12 | [5367](https://github.com/airbytehq/airbyte/pull/5367) | Migrated to CI Sandbox, refactorred code structure for future support |
| 0.1.0 | 2021-07-07 | [4358](https://github.com/airbytehq/airbyte/pull/4358) | New source |
  
</details>
