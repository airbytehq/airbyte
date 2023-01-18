# Twitter API
API Documentation link [here](https://developer.twitter.com/en/docs/twitter-api)
## Overview

The Twitter API source supports full refresh syncs

### Output schema

Below output stream is available from this source:

*[recent_search_tweets](https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-recent).


### Features

| Feature           | Supported? |
|:------------------|:-----------|
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |

### Performance considerations

Rate limiting is mentioned in the API [docuemntation](https://developer.twitter.com/en/docs/twitter-api/rate-limits)

## Getting started

### Requirements

* Twitter API Key.

### Connect using `API Key`:

1. Generate an API Key as described [here](https://developer.twitter.com/en/docs/authentication/oauth-2-0/bearer-tokens).
2. Use the generated `API Key` in the Airbyte connection.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                         |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------|
| 0.1.0   | 2022-11-01 | [18883](https://github.com/airbytehq/airbyte/pull/18858) | 🎉 New Source: Twitter                          |
