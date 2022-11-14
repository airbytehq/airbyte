# New York Times

## Overview

The New York Times source supports full refresh syncs

### Output schema

Several output streams are available from this source:

*[Archive](https://developer.nytimes.com/docs/archive-product/1/overview).
*[Most Popular Emailed Articles](https://developer.nytimes.com/docs/most-popular-product/1/routes/emailed/%7Bperiod%7D.json/get).
*[Most Popular Shared Articles](https://developer.nytimes.com/docs/most-popular-product/1/routes/shared/%7Bperiod%7D.json/get).
*[Most Popular Viewed Articles](https://developer.nytimes.com/docs/most-popular-product/1/routes/viewed/%7Bperiod%7D.json/get).

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature           | Supported? |
|:------------------|:-----------|
| Full Refresh Sync | Yes        |
| Incremental Sync  | Yes        |

### Performance considerations

The New York Times connector should not run into limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* New York Times API Key. 

### Connect using `API Key`:

1. Create a new App [here](https://developer.nytimes.com/my-apps/new-app) (You need to have an account to create a new App).
2. Enable API access for the supported endpoints (see Output schema section for supported streams).
3. Write the key into `secrets/config.json` file.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                         |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------|
| 0.1.0   | 2022-11-01 | [18746](https://github.com/airbytehq/airbyte/pull/18746) | 🎉 New Source: New York Times                   |
