# Drift

## Overview

The Drift source supports Full Refresh syncs. That is, every time a sync is run, Airbyte will copy all rows in the tables and columns you set up for replication into the destination in a new table.

### Output schema

Several output streams are available from this source:

* [Accounts](https://devdocs.drift.com/docs/account-model)
* [Conversations](https://devdocs.drift.com/docs/conversation-model)
* [Users](https://devdocs.drift.com/docs/user-model)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | No |
| Replicate Incremental Deletes | No |
| SSL connection | Yes |

### Performance considerations

The Drift connector should not run into Drift API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Create an App
* Give your app permission scopes:
  * `conversation_read` to access Conversions
  * `user_read` to access Users
  * `account_read` to access Accounts
* Install it to your Drift Account

### Setup guide

Please read [Quick start](https://devdocs.drift.com/docs/quick-start).

