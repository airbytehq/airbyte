# Omnisend

## Sync overview

This source can sync data from the [Omnisend API](https://api-docs.omnisend.com/reference/intro). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

* contacts
* campaigns
* carts
* orders
* products

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | No |  |

### Performance considerations

The connector has a rate limit of 400 requests per 1 minute.

## Getting started

### Requirements

* Omnisend API Key

## Changelog

| Version | Date       | Pull Request | Subject                                                    |
|:--------|:-----------| :----------- |:-----------------------------------------------------------|
| 0.1.3 | 2024-04-19 | [37206](https://github.com/airbytehq/airbyte/pull/37206) | Upgrade to CDK 0.80.0 and manage dependencies with Poetry. |
| 0.1.2 | 2024-04-15 | [37206](https://github.com/airbytehq/airbyte/pull/37206) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.1 | 2024-04-12 | [37206](https://github.com/airbytehq/airbyte/pull/37206) | schema descriptions |
| 0.1.0 | 2022-10-25 | [18577](https://github.com/airbytehq/airbyte/pull/18577) | Initial commit |
