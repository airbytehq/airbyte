# Sumo Logic

## Overview

The Sumo Logic source supports incremental syncs of their [Job Search API](https://help.sumologic.com/APIs/Search-Job-API/About-the-Search-Job-API).

### Output schema

This Source is capable of syncing the following core Streams:

* [Search Job Messages](https://help.sumologic.com/APIs/Search-Job-API/About-the-Search-Job-API) \(Incremental\)

### Note on Incremental Syncs

By default, this connector uses `_messagetime` as cursor for incremental syncs, but user can set `by_receipt_time` option to `True` to use `_receipttime` instead.

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |
| Incremental - Dedupe Sync | Yes |
| SSL connection | Yes |
| Namespaces | No |

## Getting started

### Requirements

* Sumo Logic API Access ID and Access Key

### Setup guide

Generate your own Sumo Logic API `Access ID` and `Access Key`. See details [here](https://help.sumologic.com/Manage/Security/Access-Keys)

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.0 | 2021-10-22 | [7283](https://github.com/airbytehq/airbyte/pull/7283) | Initial Release |

