# TVMaze Schedule

## Sync overview

This source retrieves historical and future TV scheduling data using the
[TVMaze](https://www.tvmaze.com/) schedule API.

### Output schema

This source is capable of syncing the following streams:

- `domestic`
- `web`
- `future`

### Features

| Feature           | Supported? \(Yes/No\) | Notes |
| :---------------- | :-------------------- | :---- |
| Full Refresh Sync | Yes                   |       |
| Incremental Sync  | No                    |       |

### Performance considerations

TVMaze has a rate limit of 20 requests per 10 seconds. This source should not
run into this limit.

## Getting started

### Requirements

1. Choose a start date for your sync. This may be in the future.
2. Choose an ISO 3166-1 country code for domestic schedule syncs.

### Setup guide

The following fields are required fields for the connector to work:

- `start_date`: The start date to pull `history` data from.
- (optional) `end_date`: The end date to pull `history` data until.
- `domestic_schedule_country_code`: The ISO 3166-1 country code to pull domestic
  schedule data for.
- (optional) `web_schedule_country_code`: The ISO 3166-1 country code to pull
  web schedule data for. Can be left blank for all countries and global
  channels, or set to 'global' for only global channels.

## Changelog

| Version | Date       | Pull Request                                             | Subject    |
| :------ | :--------- | :------------------------------------------------------- | :--------- |
| 0.1.0   | 2022-10-22 | [18333](https://github.com/airbytehq/airbyte/pull/18333) | New source |
