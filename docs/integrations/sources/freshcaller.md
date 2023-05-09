# Freshcaller

## Overview

The Freshcaller source supports full refresh and incremental sync. Depending on your needs, one could choose appropriate sync mode - `full refresh` replicates all records every time a sync happens where as `incremental` replicates net-new records since the last successful sync.

### Output schema

The following endpoints are supported from this source:

* [Users](https://developers.freshcaller.com/api/#users)
* [Teams](https://developers.freshcaller.com/api/#teams)
* [Calls](https://developers.freshcaller.com/api/#calls)
* [Call Metrics](https://developers.freshcaller.com/api/#call-metrics)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| SSL connection | Yes |
| Namespaces | No |

### Performance considerations

The Freshcaller connector should not run into Freshcaller API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Freshcaller Account
* Freshcaller API Key

### Setup guide

Please read [How to find your API key](https://support.freshdesk.com/en/support/solutions/articles/225435-where-can-i-find-my-api-key-).

## Changelog
| 0.1.0   | 2022-08-11 | [14759](https://github.com/airbytehq/airbyte/pull/14759)   | 🎉 New Source: Freshcaller       |