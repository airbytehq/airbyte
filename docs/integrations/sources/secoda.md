# Secoda API

## Sync overview

This source can sync data from the [Secoda API](https://docs.secoda.co/secoda-api). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

- collections
- tables
- terms

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |

### Performance considerations

## Getting started

### Requirements

- API Access

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                                  |
| :------ | :--------- | :-------------------------------------------------------- | :--------------------------------------- |
| 0.1.11 | 2024-07-27 | [42829](https://github.com/airbytehq/airbyte/pull/42829) | Update dependencies |
| 0.1.10 | 2024-07-20 | [42189](https://github.com/airbytehq/airbyte/pull/42189) | Update dependencies |
| 0.1.9 | 2024-07-13 | [41723](https://github.com/airbytehq/airbyte/pull/41723) | Update dependencies |
| 0.1.8 | 2024-07-10 | [41459](https://github.com/airbytehq/airbyte/pull/41459) | Update dependencies |
| 0.1.7 | 2024-07-09 | [41202](https://github.com/airbytehq/airbyte/pull/41202) | Update dependencies |
| 0.1.6 | 2024-07-06 | [40848](https://github.com/airbytehq/airbyte/pull/40848) | Update dependencies |
| 0.1.5 | 2024-06-25 | [40266](https://github.com/airbytehq/airbyte/pull/40266) | Update dependencies |
| 0.1.4 | 2024-06-22 | [39983](https://github.com/airbytehq/airbyte/pull/39983) | Update dependencies |
| 0.1.3 | 2024-06-05 | [38932](https://github.com/airbytehq/airbyte/pull/38932) | Make connector compatible with builder |
| 0.1.2 | 2024-06-04 | [38957](https://github.com/airbytehq/airbyte/pull/38957) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.1 | 2024-05-21 | [38530](https://github.com/airbytehq/airbyte/pull/38530) | [autopull] base image + poetry + up_to_date |
| 0.1.0   | 2022-10-27 | [#18378](https://github.com/airbytehq/airbyte/pull/18378) | 🎉 New Source: Secoda API [low-code CDK] |

</details>
