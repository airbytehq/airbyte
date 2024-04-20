# Launchdarkly API

## Sync overview

This source can sync data from the [Launchdarkly API](https://apidocs.launchdarkly.com/#section/Overview). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

* projects
* environments
* metrics
* members
* audit_log
* flags

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | No |  |

### Performance considerations

Launchdarkly APIs are under rate limits for the number of API calls allowed per API keys per second. If you reach a rate limit, API will return a 429 HTTP error code. See [here](https://apidocs.launchdarkly.com/#section/Overview/Rate-limiting)

## Getting started

### Requirements

* Access Token

## Changelog

| Version | Date       | Pull Request                                              | Subject                                    |
| :------ | :--------- | :-------------------------------------------------------- | :----------------------------------------- |
| 0.1.3 | 2024-04-19 | [0](https://github.com/airbytehq/airbyte/pull/0) | Manage dependencies with Poetry. |
| 0.1.2 | 2024-04-15 | [37185](https://github.com/airbytehq/airbyte/pull/37185) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.1 | 2024-04-12 | [37185](https://github.com/airbytehq/airbyte/pull/37185) | schema descriptions |
| 0.1.0   | 2022-10-30 | [#18660](https://github.com/airbytehq/airbyte/pull/18660) | 🎉 New Source: Launchdarkly API [low-code CDK] |
