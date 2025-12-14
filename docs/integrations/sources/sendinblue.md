# Sendinblue API

## Sync overview

This source can sync data from the [Sendinblue API](https://developers.sendinblue.com/).

## This Source Supports the Following Streams

- [contacts](https://developers.brevo.com/reference/getcontacts-1) _(Incremental Sync)_
- [campaigns](https://developers.brevo.com/reference/getemailcampaigns-1)
- [templates](https://developers.brevo.com/reference/getsmtptemplates)

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | Yes                  |       |

### Performance considerations

Sendinblue APIs are under rate limits for the number of API calls allowed per API keys per second. If you reach a rate limit, API will return a 429 HTTP error code. See [here](https://developers.sendinblue.com/docs/how-it-works#rate-limiting)

## Getting started

### Requirements

- Sendinblue API KEY

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                                                       |
| :------ | :--------- | :-------------------------------------------------------- | :------------------------------------------------------------ |
| 0.2.18 | 2025-12-09 | [70757](https://github.com/airbytehq/airbyte/pull/70757) | Update dependencies |
| 0.2.17 | 2025-11-25 | [69982](https://github.com/airbytehq/airbyte/pull/69982) | Update dependencies |
| 0.2.16 | 2025-11-18 | [69677](https://github.com/airbytehq/airbyte/pull/69677) | Update dependencies |
| 0.2.15 | 2025-10-29 | [68850](https://github.com/airbytehq/airbyte/pull/68850) | Update dependencies |
| 0.2.14 | 2025-10-21 | [68430](https://github.com/airbytehq/airbyte/pull/68430) | Update dependencies |
| 0.2.13 | 2025-10-14 | [67906](https://github.com/airbytehq/airbyte/pull/67906) | Update dependencies |
| 0.2.12 | 2025-10-07 | [67216](https://github.com/airbytehq/airbyte/pull/67216) | Update dependencies |
| 0.2.11 | 2025-09-30 | [66866](https://github.com/airbytehq/airbyte/pull/66866) | Update dependencies |
| 0.2.10 | 2025-09-23 | [66631](https://github.com/airbytehq/airbyte/pull/66631) | Update dependencies |
| 0.2.9 | 2025-09-09 | [66118](https://github.com/airbytehq/airbyte/pull/66118) | Update dependencies |
| 0.2.8 | 2025-08-24 | [65497](https://github.com/airbytehq/airbyte/pull/65497) | Update dependencies |
| 0.2.7 | 2025-08-09 | [64824](https://github.com/airbytehq/airbyte/pull/64824) | Update dependencies |
| 0.2.6 | 2025-08-02 | [64412](https://github.com/airbytehq/airbyte/pull/64412) | Update dependencies |
| 0.2.5 | 2025-07-26 | [63975](https://github.com/airbytehq/airbyte/pull/63975) | Update dependencies |
| 0.2.4 | 2025-07-20 | [63674](https://github.com/airbytehq/airbyte/pull/63674) | Update dependencies |
| 0.2.3 | 2025-06-28 | [48224](https://github.com/airbytehq/airbyte/pull/48224) | Update dependencies |
| 0.2.2 | 2024-10-29 | [47638](https://github.com/airbytehq/airbyte/pull/47638) | Update dependencies |
| 0.2.1 | 2024-10-21 | [47192](https://github.com/airbytehq/airbyte/pull/47192) | Update dependencies |
| 0.2.0 | 2024-08-26 | [44774](https://github.com/airbytehq/airbyte/pull/44774) | Refactor connector to manifest-only format |
| 0.1.13 | 2024-08-24 | [44670](https://github.com/airbytehq/airbyte/pull/44670) | Update dependencies |
| 0.1.12 | 2024-08-17 | [43825](https://github.com/airbytehq/airbyte/pull/43825) | Update dependencies |
| 0.1.11 | 2024-08-10 | [43654](https://github.com/airbytehq/airbyte/pull/43654) | Update dependencies |
| 0.1.10 | 2024-08-03 | [43253](https://github.com/airbytehq/airbyte/pull/43253) | Update dependencies |
| 0.1.9 | 2024-07-27 | [42740](https://github.com/airbytehq/airbyte/pull/42740) | Update dependencies |
| 0.1.8 | 2024-07-20 | [42145](https://github.com/airbytehq/airbyte/pull/42145) | Update dependencies |
| 0.1.7 | 2024-07-13 | [41807](https://github.com/airbytehq/airbyte/pull/41807) | Update dependencies |
| 0.1.6 | 2024-07-10 | [41513](https://github.com/airbytehq/airbyte/pull/41513) | Update dependencies |
| 0.1.5 | 2024-07-09 | [41305](https://github.com/airbytehq/airbyte/pull/41305) | Update dependencies |
| 0.1.4 | 2024-07-06 | [40853](https://github.com/airbytehq/airbyte/pull/40853) | Update dependencies |
| 0.1.3 | 2024-06-29 | [40625](https://github.com/airbytehq/airbyte/pull/40625) | Update dependencies |
| 0.1.2 | 2024-06-27 | [38346](https://github.com/airbytehq/airbyte/pull/38346) | Make comptability with builder |
| 0.1.1 | 2022-08-31 | [30022](https://github.com/airbytehq/airbyte/pull/30022) | ✨ Source SendInBlue: Add incremental sync to contacts stream |
| 0.1.0 | 2022-11-01 | [18771](https://github.com/airbytehq/airbyte/pull/18771) | 🎉 New Source: Sendinblue API [low-code CDK] |

</details>
