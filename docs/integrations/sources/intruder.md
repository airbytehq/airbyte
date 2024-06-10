# Intruder.io API

## Sync overview

This source can sync data from the [Intruder.io API](https://dev.Intruder.io.com/email). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

- Issues
- Occurrences issue
- Targets
- Scans

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |

### Performance considerations

Intruder.io APIs are under rate limits for the number of API calls allowed per API keys per second. If you reach a rate limit, API will return a 429 HTTP error code. See [here](https://developers.intruder.io/docs/rate-limiting)

## Getting started

### Requirements

- Intruder.io Access token

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                                       |
| :------ | :--------- | :-------------------------------------------------------- | :-------------------------------------------- |
| 0.1.3   | 2024-06-15 | [39112](https://github.com/airbytehq/airbyte/pull/39112)  | Make compatible with builder                  |
| 0.1.2   | 2024-06-06 | [39222](https://github.com/airbytehq/airbyte/pull/39222)  | [autopull] Upgrade base image to v1.2.2       |
| 0.1.1   | 2024-05-21 | [38495](https://github.com/airbytehq/airbyte/pull/38495)  | [autopull] base image + poetry + up_to_date   |
| 0.1.0   | 2022-10-30 | [#18668](https://github.com/airbytehq/airbyte/pull/18668) | 🎉 New Source: Intruder.io API [low-code CDK] |

</details>
