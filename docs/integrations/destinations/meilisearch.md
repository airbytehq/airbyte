# MeiliSearch

## Overview

The Airbyte MeilSearch destination allows you to sync data to MeiliSearch. MeiliSearch is a search engine that makes it easy for a non-developer to search through data. It does not require any SQL.

### Sync overview

#### Output schema

Each stream will be output into its own index in MeiliSearch. Each table will be named after the stream with all non-alpha numeric characters removed. Each table will contain one column per top-levelfield in a stream. In addition, it will contain a table called `_ab_pk`. This column is used internally by Airbyte to prevent records from getting overwritten and can be ignored.

#### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | Yes |  |
| Incremental - Deduped History | No | As this connector does not support dbt, we don't support this sync mode on this destination. |
| Namespaces | No |  |

## Getting started

### Requirements

To use the MeiliSearch destination, you'll need an existing MeiliSearch instance. You can learn about how to create one in the [MeiliSearch docs](https://docs.meilisearch.com/reference/features/installation.html#download-and-launch).

### Setup guide

The setup only requires two fields. First is the `host` which is the address at which MeiliSearch can be reached. If running on a localhost by default it will be on `http://localhost:7700`. Note that you must include the protocol. The second piece of information is the API key. If no API key is set for your MeiliSearch instance, then this field can be left blank. If it is set, you can find the value for your API by following these [instructions](https://docs.meilisearch.com/reference/features/authentication.html#master-key). in the MeiliSearch docs.

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 1.0.0 | 2022-10-26 | [18036](https://github.com/airbytehq/airbyte/pull/18036) |  Migrate MeiliSearch to Python CDK |
| 0.2.13 | 2022-06-17 | [13864](https://github.com/airbytehq/airbyte/pull/13864) | Updated stacktrace format for any trace message errors |
| 0.2.12 | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256) | Add `-XX:+ExitOnOutOfMemoryError` JVM option |
| 0.2.11 | 2021-12-28 | [9156](https://github.com/airbytehq/airbyte/pull/9156) | Update connector fields title/description |
