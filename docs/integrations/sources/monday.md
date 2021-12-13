# Monday

## Overview

The Monday supports full refresh syncs

### Output schema

Several output streams are available from this source:

* [Items](https://api.developer.monday.com/docs/items-queries)
* [Boards](https://api.developer.monday.com/docs/groups-queries#groups-queries)
* [Teams](https://api.developer.monday.com/docs/teams-queries)
* [Updates](https://api.developer.monday.com/docs/updates-queries)
* [Users](https://api.developer.monday.com/docs/users-queries-1)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | No |
| SSL connection | No |
| Namespaces | No |

### Performance considerations

The Monday connector should not run into Monday API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Monday Account
* Monday API Token

### Setup guide

You can get the API key for Monday by going to Profile picture (bottom left) => Admin => API

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.1 | 2021-11-18 | [8016](https://github.com/airbytehq/airbyte/pull/8016) | 🐛 Source Monday: fix pagination and schema bug |
| 0.1.0 | 2021-11-07 | [7168](https://github.com/airbytehq/airbyte/pull/7168) | 🎉 New Source: Monday |
