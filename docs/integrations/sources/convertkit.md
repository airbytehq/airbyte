# ConvertKit

## Sync overview

This source can sync data from the [ConvertKit API](https://developers.convertkit.com/#getting-started). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

- sequences
- subscribers
- broadcasts
- tags
- forms

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |

### Performance considerations

The connector has a rate limit of no more than 120 requests over a rolling 60 second period, for a given api secret.

## Getting started

### Requirements

- ConvertKit API Secret

## Changelog

| Version | Date       | Pull Request                                             | Subject        |
| :------ | :--------- | :------------------------------------------------------- | :------------- |
| 0.1.0   | 2022-10-25 | [18455](https://github.com/airbytehq/airbyte/pull/18455) | Initial commit |
