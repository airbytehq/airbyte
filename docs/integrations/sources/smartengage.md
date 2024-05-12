# SmartEngage

## Sync overview

This source can sync data from the [SmartEngage API](https://smartengage.com/docs/#smartengage-api). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

- avatars
- tags
- custom_fields
- sequences

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |

## Getting started

### Requirements

- SmartEngage API Key

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.1.3   | 2024-04-19 | [37261](https://github.com/airbytehq/airbyte/pull/37261) | Upgrade to CDK 0.80.0 and manage dependencies with Poetry.                      |
| 0.1.2   | 2024-04-15 | [37261](https://github.com/airbytehq/airbyte/pull/37261) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.1   | 2024-04-12 | [37261](https://github.com/airbytehq/airbyte/pull/37261) | schema descriptions                                                             |
| 0.1.0   | 2022-10-25 | [18701](https://github.com/airbytehq/airbyte/pull/18701) | Initial commit                                                                  |
