# Toggl API

## Sync overview

This source can sync data from the [Toggl API](https://developers.track.toggl.com/docs/). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

* time_entries
* organizations
* organizations_users
* organizations_groups
* workspace
* workspace_clients
* workspace_tasks

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | No |  |

### Performance considerations

Toggl APIs are under rate limits for the number of API calls allowed per API keys per second. If you reach a rate limit, API will return a 429 HTTP error code. See [here](https://developers.track.toggl.com/docs/#the-api-format)

## Getting started

### Requirements

* API token

## Changelog

| Version | Date       | Pull Request                                              | Subject                                    |
| :------ | :--------- | :-------------------------------------------------------- | :----------------------------------------- |
| 0.1.0   | 2022-10-28 | [#18507](https://github.com/airbytehq/airbyte/pull/18507) | 🎉 New Source: Toggl API [low-code CDK] |