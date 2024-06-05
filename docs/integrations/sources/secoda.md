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
| 0.1.2 | 2024-06-04 | [38957](https://github.com/airbytehq/airbyte/pull/38957) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.1 | 2024-05-21 | [38530](https://github.com/airbytehq/airbyte/pull/38530) | [autopull] base image + poetry + up_to_date |
| 0.1.0   | 2022-10-27 | [#18378](https://github.com/airbytehq/airbyte/pull/18378) | 🎉 New Source: Secoda API [low-code CDK] |

</details>