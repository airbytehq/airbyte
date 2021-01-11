# Slack

## Sync overview

This source can sync data for the [Slack API](https://api.slack.com/). It supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This Source Connector is based on a [Singer Tap](https://github.com/singer-io/tap-slack).

### Output schema

This Source is capable of syncing the following core Streams:

* [Channels \(Conversations\)](https://api.slack.com/methods/conversations.list)
* [Channel Members \(Conversation Members\)](https://api.slack.com/methods/conversations.members)
* [Messages \(Conversation History\)](https://api.slack.com/methods/conversations.history)
* [Users](https://api.slack.com/methods/users.list)
* [Threads \(Conversation Replies\)](https://api.slack.com/methods/conversations.replies)
* [User Groups](https://api.slack.com/methods/usergroups.list)
* [Files](https://api.slack.com/methods/files.list)
* [Remote Files](https://api.slack.com/methods/files.remote.list)

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| `string` | `string` |  |
| `number` | `number` |  |
| `array` | `array` |  |
| `object` | `object` |  |

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | yes |  |
| Incremental Sync | yes |  |

### Performance considerations

The connector is restricted by normal Slack [requests limitation](https://api.slack.com/docs/rate-limits).

The Slack connector should not run into Slack API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Slack API Token 

### Setup guide

Generate a API access token using the [Slack documentation](https://slack.com/intl/en-ua/help/articles/215770388-Create-and-regenerate-API-tokens)

We recommend creating a restricted, read-only key specifically for Airbyte access. This will allow you to control which resources Airbyte should be able to access.

