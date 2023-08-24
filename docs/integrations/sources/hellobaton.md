# Hellobaton

## Sync overview

This source can sync data from the [hellobaton API](https://app.hellobaton.com/api/redoc/). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

- activity
- companies
- milestones
- phases
- project_attachments
- projects
- task_attachemnts
- tasks
- templates
- time_entries
- users

Hellobaton adds new streams fairly regularly please submit an issue or PR if this project doesn't support required streams for your use case.

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--------------- | :----------- | :---- |
| `string`         | `string`     |       |
| `integer`        | `integer`    |       |
| `number`         | `number`     |       |
| `array`          | `array`      |       |
| `object`         | `object`     |       |

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |
| Namespaces        | No                   |       |

### Performance considerations

The connector is rate limited at 1000 requests per minute per api key. If you find yourself receiving errors contact your customer success manager and request a rate limit increase.

## Getting started

### Requirements

- Hellobaton account
- Hellobaton api key

## Changelog

| Version | Date       | Pull Request                                           | Subject                   |
| :------ | :--------- | :----------------------------------------------------- | :------------------------ |
| 0.2.0   | 2023-08-19 | [29490](https://github.com/airbytehq/airbyte/pull/29490) | Migrate CDK from Python to Low Code |
| 0.1.0   | 2022-01-14 | [8461](https://github.com/airbytehq/airbyte/pull/8461) | 🎉 New Source: Hellobaton |
