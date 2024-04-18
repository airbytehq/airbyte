# Sendinblue API

## Sync overview

This source can sync data from the [Sendinblue API](https://developers.sendinblue.com/).

## This Source Supports the Following Streams

* [contacts](https://developers.brevo.com/reference/getcontacts-1) *(Incremental Sync)*
* [campaigns](https://developers.brevo.com/reference/getemailcampaigns-1)
* [templates](https://developers.brevo.com/reference/getsmtptemplates)

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | Yes |  |

### Performance considerations

Sendinblue APIs are under rate limits for the number of API calls allowed per API keys per second. If you reach a rate limit, API will return a 429 HTTP error code. See [here](https://developers.sendinblue.com/docs/how-it-works#rate-limiting)

## Getting started

### Requirements

* Sendinblue API KEY

## Changelog

| Version | Date       | Pull Request                                              | Subject                                    |
| :------ | :--------- | :-------------------------------------------------------- | :----------------------------------------- |
| 0.1.4 | 2024-04-18 | [37256](https://github.com/airbytehq/airbyte/pull/37256) | Manage dependencies with Poetry. |
| 0.1.3 | 2024-04-15 | [37256](https://github.com/airbytehq/airbyte/pull/37256) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.2 | 2024-04-12 | [37256](https://github.com/airbytehq/airbyte/pull/37256) | schema descriptions |
| 0.1.1   | 2022-08-31 | [#30022](https://github.com/airbytehq/airbyte/pull/30022) | ✨ Source SendInBlue: Add incremental sync to contacts stream |
| 0.1.0   | 2022-11-01 | [#18771](https://github.com/airbytehq/airbyte/pull/18771) | 🎉 New Source: Sendinblue API [low-code CDK] |
