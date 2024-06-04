# Ip2whois API

## Sync overview

This source can sync data from the [Ip2whois API](https://www.ip2whois.com/developers-api). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch.

## This Source Supports the Following Streams

- [whois](https://www.ip2whois.com/developers-api)

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |

### Performance considerations

Ip2whois APIs allows you to query up to 500 WHOIS domain name per month.

## Getting started

### Requirements

- [API token](https://www.ip2whois.com/register)

## Changelog

| Version | Date       | Pull Request                                              | Subject                                                                         |
| :------ | :--------- | :-------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.1.4   | 2024-05-20 | [38215](https://github.com/airbytehq/airbyte/pull/38215)  | Make connector compatible with builder                                          |
| 0.1.3   | 2024-04-19 | [37180](https://github.com/airbytehq/airbyte/pull/37180)  | Upgrade to CDK 0.80.0 and manage dependencies with Poetry.                      |
| 0.1.2   | 2024-04-15 | [37180](https://github.com/airbytehq/airbyte/pull/37180)  | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.1   | 2024-04-12 | [37180](https://github.com/airbytehq/airbyte/pull/37180)  | schema descriptions                                                             |
| 0.1.0   | 2022-10-29 | [#18651](https://github.com/airbytehq/airbyte/pull/18651) | 🎉 New source: Ip2whois [low-code SDK]                                          |
