# Mailjet - SMS API

## Sync overview

This source can sync data from the [Mailjet SMS API](https://dev.mailjet.com/sms/guides/). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

- SMS

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |

### Performance considerations

Mailjet APIs are under rate limits for the number of API calls allowed per API keys per second. If you reach a rate limit, API will return a 429 HTTP error code. See [here](https://dev.mailjet.com/sms/reference/overview/rate-limits/)

## Getting started

### Requirements

- Mailjet SMS TOKEN

## Changelog

| Version | Date       | Pull Request                                              | Subject                                                                         |
| :------ | :--------- | :-------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.1.3   | 2024-04-19 | [37195](https://github.com/airbytehq/airbyte/pull/37195)  | Upgrade to CDK 0.80.0 and manage dependencies with Poetry.                      |
| 0.1.2   | 2024-04-15 | [37195](https://github.com/airbytehq/airbyte/pull/37195)  | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.1   | 2024-04-12 | [37195](https://github.com/airbytehq/airbyte/pull/37195)  | schema descriptions                                                             |
| 0.1.0   | 2022-10-26 | [#18345](https://github.com/airbytehq/airbyte/pull/18345) | 🎉 New Source: Mailjet SMS API [low-code CDK]                                   |
