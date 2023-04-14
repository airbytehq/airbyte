# Intruder.io API

## Sync overview

This source can sync data from the [Intruder.io API](https://dev.Intruder.io.com/email). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

* Issues
* Occurrences issue
* Targets
* Scans

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | No |  |

### Performance considerations

Intruder.io APIs are under rate limits for the number of API calls allowed per API keys per second. If you reach a rate limit, API will return a 429 HTTP error code. See [here](https://developers.intruder.io/docs/rate-limiting)

## Getting started

### Requirements

* Intruder.io Access token

## Changelog

| Version | Date       | Pull Request                                              | Subject                                    |
| :------ | :--------- | :-------------------------------------------------------- | :----------------------------------------- |
| 0.1.0   | 2022-10-30 | [#18668](https://github.com/airbytehq/airbyte/pull/18668) | 🎉 New Source: Intruder.io API [low-code CDK] |