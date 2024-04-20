# MailerLite

## Sync overview

This source can sync data from the [MailerLite API](https://developers.mailerlite.com/docs/#mailerlite-api). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

* campaigns
* subscribers
* automations
* timezones
* segments
* forms_popup
* forms_embedded
* forms_promotion

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | No |  |

### Performance considerations

MailerLite API has a global rate limit of 120 requests per minute.

## Getting started

### Requirements

* MailerLite API Key

## Changelog

| Version | Date       | Pull Request                                             | Subject        |
| :------ | :--------- | :------------------------------------------------------- | :------------- |
| 0.1.3 | 2024-04-19 | [0](https://github.com/airbytehq/airbyte/pull/0) | Manage dependencies with Poetry. |
| 0.1.2 | 2024-04-15 | [37191](https://github.com/airbytehq/airbyte/pull/37191) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.1 | 2024-04-12 | [37191](https://github.com/airbytehq/airbyte/pull/37191) | schema descriptions |
| 0.1.0 | 2022-10-25 | [18336](https://github.com/airbytehq/airbyte/pull/18336) | Initial commit |
