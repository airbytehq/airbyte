# Oura

## Sync overview

This source can sync various data from the [Oura](https://ouraring.com/) ring.
It currently only supports authentication through personal access tokens, and
is therefore not suitable for syncing data from multiple Oura rings.

### Output schema

This source is capable of syncing the following streams:

- `daily_activity`
- `daily_readiness`
- `daily_sleep`
- `heart_rate`
- `sessions`
- `sleep_periods`
- `tags`
- `workouts`

### Features

| Feature           | Supported? \(Yes/No\) | Notes                             |
|:------------------|:----------------------|:----------------------------------|
| Full Refresh Sync | Yes                   |                                   |
| Incremental Sync  | No                    |                                   |
| Multiple rings    | No                    | May be implemented in the future. |

### Performance considerations

There are no documented rate limits for the Oura V2 API at the time of writing.
However, users must have an up-to-date version of the Oura app installed to use
the API.

## Getting started

### Requirements

1. Purchase an Oura ring.
2. Create a personal access token via the
   [Oura developer portal](https://cloud.ouraring.com/personal-access-tokens).

### Setup guide

The following fields are required fields for the connector to work:

- `api_key`: Your Oura API key.
- (optional) `start_datetime`: The start date and time for the sync.
- (optional) `end_datetime`: The end date and time for the sync.

## Changelog

| Version | Date       | Pull Request                                             | Subject    |
|:--------|:-----------|:---------------------------------------------------------|:-----------|
| 0.1.0   | 2022-10-20 | [18224](https://github.com/airbytehq/airbyte/pull/18224) | New source |
