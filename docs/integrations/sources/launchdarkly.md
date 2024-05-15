# Launchdarkly API

## Sync overview

This source can sync data from the [Launchdarkly API](https://apidocs.launchdarkly.com/#section/Overview). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

- projects
- environments
- metrics
- members
- audit_log
- flags

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |

### Performance considerations

Launchdarkly APIs are under rate limits for the number of API calls allowed per API keys per second. If you reach a rate limit, API will return a 429 HTTP error code. See [here](https://apidocs.launchdarkly.com/#section/Overview/Rate-limiting)

## Getting started

### Requirements

- Access Token

## Changelog

| Version | Date       | Pull Request                                              | Subject                                        |
| :------ | :--------- | :-------------------------------------------------------- | :--------------------------------------------- |
| 0.1.0   | 2022-10-30 | [#18660](https://github.com/airbytehq/airbyte/pull/18660) | 🎉 New Source: Launchdarkly API [low-code CDK] |
