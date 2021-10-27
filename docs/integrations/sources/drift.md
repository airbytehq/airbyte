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
| Incremental Sync | Coming soon |
| Replicate Incremental Deletes | Coming soon |
| SSL connection | Yes |
| Namespaces | No |

### Performance considerations

The Drift connector should not run into Drift API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* A Drift API token linked to a Drift App with the following scopes: 
  * `conversation_read` to access Conversions
  * `user_read` to access Users
  * `account_read` to access Accounts

### Setup guide

Follow Drift's [Setting Things Up ](https://devdocs.drift.com/docs/quick-start)guide for a more detailed description of how to obtain the API token.

## CHANGELOG

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| `0.2.3` | 2021-10-27 | [7247](https://github.com/airbytehq/airbyte/pull/7247) | Migrate to the CDK |