# Sonar Cloud API

## Sync overview

This source can sync data from the [Sonar cloud API](https://sonarcloud.io/web_api). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

- components
- issues
- metrics

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |

## Getting started

### Requirements

- Sonar cloud User Token

## Changelog

| Version | Date                                                                  | Pull Request                                              | Subject                                                                         |
| :------ | :-------------------------------------------------------------------- | :-------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.1.5   | 2024-04-19                                                            | [37262](https://github.com/airbytehq/airbyte/pull/37262)  | Updating to 0.80.0 CDK                                                          |
| 0.1.4   | 2024-04-18                                                            | [37262](https://github.com/airbytehq/airbyte/pull/37262)  | Manage dependencies with Poetry.                                                |
| 0.1.3   | 2024-04-15                                                            | [37262](https://github.com/airbytehq/airbyte/pull/37262)  | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.2   | 2024-04-12                                                            | [37262](https://github.com/airbytehq/airbyte/pull/37262)  | schema descriptions                                                             |
| 0.1.1   | 2023-02-11 l [22868](https://github.com/airbytehq/airbyte/pull/22868) | Specified date formatting in specification                |
| 0.1.0   | 2022-10-26                                                            | [#18475](https://github.com/airbytehq/airbyte/pull/18475) | 🎉 New Source: Sonar Cloud API [low-code CDK]                                   |
