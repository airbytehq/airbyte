# Smaily

## Sync overview

This source can sync data from the [Smaily API](https://smaily.com/help/api/). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

- users
- segments
- campaigns
- templates
- automations
- A/B tests

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |

### Performance considerations

The connector has a rate limit of 5 API requests per second per IP-address.

## Getting started

### Requirements

- Smaily API user username
- Smaily API user password
- Smaily API subdomain

## Changelog

| Version | Date       | Pull Request                                             | Subject        |
| :------ | :--------- | :------------------------------------------------------- | :------------- |
| 0.1.0   | 2022-10-25 | [18674](https://github.com/airbytehq/airbyte/pull/18674) | Initial commit |
