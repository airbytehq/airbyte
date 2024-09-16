# Configcat API

## Sync overview

This source can sync data from the [Configcat API](https://api.configcat.com/docs). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

- organizations
- organization_members
- products
- tags
- environments

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |

### Performance considerations

Configcat APIs are under rate limits for the number of API calls allowed per API keys per second. If you reach a rate limit, API will return a 429 HTTP error code. See [here](https://api.configcat.com/docs/#section/Throttling-and-rate-limits)

## Getting started

### Requirements

- Username
- Password

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                                     |
| :------ | :--------- | :-------------------------------------------------------- | :------------------------------------------ |
| 0.2.0 | 2024-08-23 | [44594](https://github.com/airbytehq/airbyte/pull/44594) | Refactor connector to manifest-only format |
| 0.1.13 | 2024-08-17 | [44357](https://github.com/airbytehq/airbyte/pull/44357) | Update dependencies |
| 0.1.12 | 2024-08-12 | [43870](https://github.com/airbytehq/airbyte/pull/43870) | Update dependencies |
| 0.1.11 | 2024-08-10 | [43596](https://github.com/airbytehq/airbyte/pull/43596) | Update dependencies |
| 0.1.10 | 2024-08-03 | [43272](https://github.com/airbytehq/airbyte/pull/43272) | Update dependencies |
| 0.1.9 | 2024-07-27 | [42702](https://github.com/airbytehq/airbyte/pull/42702) | Update dependencies |
| 0.1.8 | 2024-07-20 | [42329](https://github.com/airbytehq/airbyte/pull/42329) | Update dependencies |
| 0.1.7 | 2024-07-13 | [41705](https://github.com/airbytehq/airbyte/pull/41705) | Update dependencies |
| 0.1.6 | 2024-07-10 | [41450](https://github.com/airbytehq/airbyte/pull/41450) | Update dependencies |
| 0.1.5 | 2024-07-06 | [40929](https://github.com/airbytehq/airbyte/pull/40929) | Update dependencies |
| 0.1.4 | 2024-06-25 | [40442](https://github.com/airbytehq/airbyte/pull/40442) | Update dependencies |
| 0.1.3 | 2024-06-22 | [40076](https://github.com/airbytehq/airbyte/pull/40076) | Update dependencies |
| 0.1.2 | 2024-06-06 | [39230](https://github.com/airbytehq/airbyte/pull/39230) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.1 | 2024-05-21 | [38547](https://github.com/airbytehq/airbyte/pull/38547) | [autopull] base image + poetry + up_to_date |
| 0.1.0   | 2022-10-30 | [#18649](https://github.com/airbytehq/airbyte/pull/18649) | 🎉 New Source: Configcat API [low-code CDK] |

</details>
