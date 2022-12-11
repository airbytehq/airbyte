# Public APIs

## Sync overview

This source can sync data for the [Public APIs](https://api.publicapis.org/) REST API. It supports only Full Refresh syncs.

### Output schema

This Source is capable of syncing the following Streams:

* [Services](https://api.publicapis.org#get-entries)
* [Categories](https://api.publicapis.org#get-categories)

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| `string` | `string` |  |
| `integer`, `number` | `number` |  |
| `boolean` | `boolean` |  |

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | No |  |
| SSL connection | Yes |
| Namespaces | No |  |
| Pagination | No |  |

## Getting started

### Requirements

There is no requirements to setup this source.

### Setup guide

This source requires no setup.

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.0 | 2022-10-28 | [18471](https://github.com/airbytehq/airbyte/pull/18471) |  Initial Release |
