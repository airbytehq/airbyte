# K6 Cloud API

## Sync overview

This source can sync data from the [K6 Cloud API](https://developers.k6.io). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

- organizations
- projects
- tests

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |

### Performance considerations

## Getting started

### Requirements

- API Token

## Changelog

| Version | Date       | Pull Request                                              | Subject                                                                         |
| :------ | :--------- | :-------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.1.4   | 2024-05-15 | [38150](https://github.com/airbytehq/airbyte/pull/38150)  | Make connector compatable with the builder                                      |
| 0.1.3   | 2024-04-19 | [37181](https://github.com/airbytehq/airbyte/pull/37181)  | Upgrade to CDK 0.80.0 and manage dependencies with Poetry.                      |
| 0.1.2   | 2024-04-15 | [37181](https://github.com/airbytehq/airbyte/pull/37181)  | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.1   | 2024-04-12 | [37181](https://github.com/airbytehq/airbyte/pull/37181)  | schema descriptions                                                             |
| 0.1.0   | 2022-10-27 | [#18393](https://github.com/airbytehq/airbyte/pull/18393) | 🎉 New Source: K6 Cloud API [low-code CDK]                                      |
