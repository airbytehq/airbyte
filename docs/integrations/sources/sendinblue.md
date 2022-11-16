# Sendinblue API

## Sync overview

This source can sync data from the [Sendinblue API](https://developers.sendinblue.com/). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

* contacts
* campaigns
* templates

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | No |  |

### Performance considerations

Sendinblue APIs are under rate limits for the number of API calls allowed per API keys per second. If you reach a rate limit, API will return a 429 HTTP error code. See [here](https://developers.sendinblue.com/docs/how-it-works#rate-limiting)

## Getting started

### Requirements

* Sendinblue API KEY

## Changelog

| Version | Date       | Pull Request                                              | Subject                                    |
| :------ | :--------- | :-------------------------------------------------------- | :----------------------------------------- |
| 0.1.0   | 2022-11-01 | [#18771](https://github.com/airbytehq/airbyte/pull/18771) | 🎉 New Source: Sendinblue API [low-code CDK] |