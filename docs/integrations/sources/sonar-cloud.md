# Sonar Cloud API

## Sync overview

This source can sync data from the [Sonar cloud API](https://sonarcloud.io/web_api). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

* components
* issues
* metrics

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | No |  |


## Getting started

### Requirements

* Sonar cloud User Token

## Changelog

| Version | Date       | Pull Request                                              | Subject                                    |
| :------ | :--------- | :-------------------------------------------------------- | :----------------------------------------- |
| 0.1.0   | 2022-10-26 | [#18475](https://github.com/airbytehq/airbyte/pull/18475) | 🎉 New Source: Sonar Cloud API [low-code CDK] |