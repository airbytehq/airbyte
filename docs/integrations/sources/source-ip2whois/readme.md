# Ip2whois API

## Sync overview

This source can sync data from the [Ip2whois API](https://www.ip2whois.com/developers-api). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch.

## This Source Supports the Following Streams

* [whois](https://www.ip2whois.com/developers-api)


### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | No |  |

### Performance considerations

Ip2whois APIs allows you to query up to 500 WHOIS domain name per month.

## Getting started

### Requirements

* [API token](https://www.ip2whois.com/register)


## Changelog
| Version | Date       | Pull Request                                              | Subject                                    |
| :------ | :--------- | :-------------------------------------------------------- | :----------------------------------------- |
| 0.1.0   | 2022-10-29 | [#18651](https://github.com/airbytehq/airbyte/pull/18651) | 🎉 New source: Ip2whois [low-code SDK]|

