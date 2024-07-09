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
| 0.1.4 | 2024-07-06 | [40853](https://github.com/airbytehq/airbyte/pull/40853) | Update dependencies |
| 0.1.3 | 2024-06-29 | [40625](https://github.com/airbytehq/airbyte/pull/40625) | Update dependencies |
| 0.1.2 | 2024-06-27 | [38346](https://github.com/airbytehq/airbyte/pull/38346) | Make comptability with builder |
| 0.1.1 | 2022-08-31 | [30022](https://github.com/airbytehq/airbyte/pull/30022) | ✨ Source SendInBlue: Add incremental sync to contacts stream |
| 0.1.0 | 2022-11-01 | [18771](https://github.com/airbytehq/airbyte/pull/18771) | 🎉 New Source: Sendinblue API [low-code CDK] |

</details>
