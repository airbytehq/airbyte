# RSS

## Overview

The RSS source allows you to read data from any individual RSS feed.

#### Output schema

This source is capable of syncing the following streams:
* `items`
    * Provides stats about specific RSS items.
    * Most fields are simply kept from RSS items as strings if present (`title`, `link`, `description`, `author`, `category`, `comments`, `enclosure`, `guid`).
    * The date field is handled differently. It's transformed into a UTC datetime in a `published` field for easier use in data warehouses and other destinations.
    * The RSS feed you're subscribing to must have a valid `pubDate` field for each item for incremental syncs to work properly.
    * Since `guid` is not a required field, there is no primary key for the feed, only a cursor on the published date.

#### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |
| Namespaces | No |

### Requirements / Setup Guide

Only the `url` of an RSS feed is required.

## Performance considerations

None

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.4 | 2024-04-19 | [37252](https://github.com/airbytehq/airbyte/pull/37252) | Updating to 0.80.0 CDK |
| 0.1.3 | 2024-04-18 | [37252](https://github.com/airbytehq/airbyte/pull/37252) | Manage dependencies with Poetry. |
| 0.1.2 | 2024-04-15 | [37252](https://github.com/airbytehq/airbyte/pull/37252) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.1 | 2024-04-12 | [37252](https://github.com/airbytehq/airbyte/pull/37252) | schema descriptions |
| 0.1.0 | 2022-10-12 | [18838](https://github.com/airbytehq/airbyte/pull/18838) | Initial release supporting RSS |
