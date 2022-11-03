# GNews

## Overview

The GNews source supports full refresh syncs

### Output schema

Two output streams are available from this source:

*[Search](https://gnews.io/docs/v4?shell#search-endpoint).
*[Top Headlines](https://gnews.io/docs/v4?shell#top-headlines-endpoint).

### Features

| Feature           | Supported? |
|:------------------|:-----------|
| Full Refresh Sync | Yes        |
| Incremental Sync  | Yes        |

### Performance considerations

Rate Limiting is based on the API Key tier subscription, get more info [here](https://gnews.io/#pricing).

## Getting started

### Requirements

* GNews API Key.

### Connect using `API Key`:

1. Generate an API Key as described [here](https://gnews.io/docs/v4?shell#authentication).
2. Use the generated `API Key` in the Airbyte connection.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                         |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------|
| 0.1.0   | 2022-11-01 | [18808](https://github.com/airbytehq/airbyte/pull/18808) | 🎉 New Source: GNews                            |
