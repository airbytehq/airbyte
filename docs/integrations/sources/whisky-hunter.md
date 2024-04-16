# Whisky Hunter

## Overview

The Whisky Hunter source can sync data from the [Whisky Hunter API](https://whiskyhunter.net/api/)

#### Output schema

This source is capable of syncing the following streams:
* `auctions_data`
    * Provides stats about specific auctions.
* `auctions_info`
    * Provides information and metadata about recurring and one-off auctions.
* `distilleries_info`
    * Provides information about distilleries.

#### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | No |
| Namespaces | No |

### Requirements / Setup Guide

No config is required.

## Performance considerations

There is no published rate limit. However, since this data updates infrequently, it is recommended to set the update cadence to 24hr or higher.

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.2 | 2024-04-15 | [37287](https://github.com/airbytehq/airbyte/pull/37287) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.1 | 2024-04-12 | [37287](https://github.com/airbytehq/airbyte/pull/37287) | schema descriptions |
| 0.1.0 | 2022-10-12 | [17918](https://github.com/airbytehq/airbyte/pull/17918) | Initial release supporting the Whisky Hunter API |
