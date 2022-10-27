# Newsdata API

## Sync overview

This source retrieves the latests news from the [Newsdata API](https://newsdata.io/).

### Output schema

This source is capable of syncing the following streams:

* `latest`
* `sources`

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature           | Supported? | Notes |
|:------------------|------------|:------|
| Full Refresh Sync | Yes        |       |
| Incremental Sync  | No         |       |

### Performance considerations

The News API free tier only allows 200 requests per day, and only up to 10
news per request.

The free tier does not allow to perform advanced search queries.

## Getting started

### Requirements

1. A Newsdata API key. You can get one [here](https://newsdata.io/register).

### Setup guide

The following fields are required fields for the connector to work:

- `api_key`: Your Newsdata API key.

## Changelog

| Version | Date       | Pull Request                                             | Subject                 |
|:--------|:-----------|:---------------------------------------------------------|:------------------------|
| 0.1.0   | 2022-10-21 | [18576](https://github.com/airbytehq/airbyte/pull/18576) | 🎉 New Source: Newsdata |
