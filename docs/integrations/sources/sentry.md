# Sentry

## Sync overview

This source can sync data for the [Sentry API](https://docs.sentry.io/api/). It supports only Full Refresh syncs.

### Output schema

This Source is capable of syncing the following Streams:

* [Events](https://docs.sentry.io/api/events/list-a-projects-events/)
* [Issues](https://docs.sentry.io/api/events/list-a-projects-issues/)

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| `string` | `string` |  |
| `integer`, `number` | `number` |  |
| `array` | `array` |  |
| `object` | `object` |  |

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | No |  |
| SSL connection | Yes |
| Namespaces | No |  |

## Getting started

### Requirements

* `auth_token` - Sentry Authentication Token with the necessary permissions \(described below\)
* `organization` - Organization Slug. You can check it at https://sentry.io/settings/$YOUR_ORG_HERE/
* `project` - The name of the Project you wanto sync. You can list it from https://sentry.io/settings/$YOUR_ORG_HERE/projects/
* `hostname` - Host name of Sentry API server. For self-hosted, specify your host name here. Otherwise, leave it empty. \(default: sentry.io\)

### Setup guide

You can find or create authentication tokens within [Sentry](https://sentry.io/settings/account/api/auth-tokens/).

## Changelog

| Version | Date | Pull Request | Subject                                           |
|:--------| :--- | :--- |:--------------------------------------------------|
| 0.1.2   | 2021-12-28 | [15345](https://github.com/airbytehq/airbyte/pull/15345) | Migrate to config-based framework                 |
| 0.1.1   | 2021-12-28 | [8628](https://github.com/airbytehq/airbyte/pull/8628) | Update fields in source-connectors specifications |
| 0.1.0   | 2021-10-12 | [6975](https://github.com/airbytehq/airbyte/pull/6975) | New Source: Sentry                                |
