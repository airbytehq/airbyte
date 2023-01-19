# Configcat API

## Sync overview

This source can sync data from the [Configcat API](https://api.configcat.com/docs). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

* organizations
* organization_members
* products
* tags
* environments

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | No |  |

### Performance considerations

Configcat APIs are under rate limits for the number of API calls allowed per API keys per second. If you reach a rate limit, API will return a 429 HTTP error code. See [here](https://api.configcat.com/docs/#section/Throttling-and-rate-limits)

## Getting started

### Requirements

* Username
* Password

## Changelog

| Version | Date       | Pull Request                                              | Subject                                    |
| :------ | :--------- | :-------------------------------------------------------- | :----------------------------------------- |
| 0.1.0   | 2022-10-30 | [#18649](https://github.com/airbytehq/airbyte/pull/18649) | 🎉 New Source: Configcat API [low-code CDK] |