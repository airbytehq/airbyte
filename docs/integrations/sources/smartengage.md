# SmartEngage

## Sync overview

This source can sync data from the [SmartEngage API](https://smartengage.com/docs/#smartengage-api). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

* avatars
* tags
* custom_fields
* sequences

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | No |  |


## Getting started

### Requirements

* SmartEngage API Key

## Changelog

| Version | Date       | Pull Request | Subject                                                    |
|:--------|:-----------| :----------- |:-----------------------------------------------------------|
| 0.1.0   | 2022-10-25 | [18701](https://github.com/airbytehq/airbyte/pull/18701) | Initial commit |