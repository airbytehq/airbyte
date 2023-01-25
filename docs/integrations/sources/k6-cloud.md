# K6 Cloud API

## Sync overview

This source can sync data from the [K6 Cloud API](https://developers.k6.io). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

* organizations
* projects
* tests

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | No |  |

### Performance considerations

## Getting started

### Requirements

* API Token

## Changelog

| Version | Date       | Pull Request                                              | Subject                                    |
| :------ | :--------- | :-------------------------------------------------------- | :----------------------------------------- |
| 0.1.0   | 2022-10-27 | [#18393](https://github.com/airbytehq/airbyte/pull/18393) | 🎉 New Source: K6 Cloud API [low-code CDK] |