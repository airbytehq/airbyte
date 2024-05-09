# Statuspage.io API

## Sync overview

This source can sync data from the [Statuspage.io API](https://developer.statuspage.io). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

- pages
- subscribers
- subscribers_histogram_by_state
- incident_templates
- incidents
- components
- metrics

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |

### Performance considerations

Mailjet APIs are under rate limits for the number of API calls allowed per API keys per second. If you reach a rate limit, API will return a 429 HTTP error code. See [here](https://developer.statuspage.io/#section/Rate-Limiting)

## Getting started

### Requirements

- Statuspage.io API KEY

## Changelog

| Version | Date       | Pull Request                                              | Subject                                         |
| :------ | :--------- | :-------------------------------------------------------- | :---------------------------------------------- |
| 0.1.0   | 2022-10-30 | [#18664](https://github.com/airbytehq/airbyte/pull/18664) | 🎉 New Source: Statuspage.io API [low-code CDK] |
