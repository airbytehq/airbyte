# Zendesk Chat

## Sync overview

The Zendesk Chat source supports Full Refresh and Incremental syncs.

This source can sync data for the [Zendesk Chat API](https://developer.zendesk.com/rest_api/docs/chat/introduction).

### Output schema

This Source is capable of syncing the following core Streams:

* [Accounts](https://developer.zendesk.com/rest_api/docs/chat/accounts#show-account)
* [Agents](https://developer.zendesk.com/rest_api/docs/chat/agents#list-agents) \(Incremental\)
* [Agent Timelines](https://developer.zendesk.com/rest_api/docs/chat/incremental_export#incremental-agent-timeline-export) \(Incremental\)
* [Chats](https://developer.zendesk.com/rest_api/docs/chat/chats#list-chats)
* [Shortcuts](https://developer.zendesk.com/rest_api/docs/chat/shortcuts#list-shortcuts)
* [Triggers](https://developer.zendesk.com/rest_api/docs/chat/triggers#list-triggers)
* [Bans](https://developer.zendesk.com/rest_api/docs/chat/bans#list-bans) \(Incremental\)
* [Departments](https://developer.zendesk.com/rest_api/docs/chat/departments#list-departments)
* [Goals](https://developer.zendesk.com/rest_api/docs/chat/goals#list-goals)
* [Skills](https://developer.zendesk.com/rest_api/docs/chat/skills#list-skills)
* [Roles](https://developer.zendesk.com/rest_api/docs/chat/roles#list-roles)
* [Routing Settings](https://developer.zendesk.com/rest_api/docs/chat/routing_settings#show-account-routing-settings)

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
| Full Refresh Sync | Yes |  |
| Incremental Sync | Yes |  |
| SSL connection | Yes |  |

### Performance considerations

The connector is restricted by normal Zendesk [requests limitation](https://developer.zendesk.com/rest_api/docs/voice-api/introduction#rate-limits).

The Zendesk connector should not run into Zendesk API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Zendesk Chat Access Token

### Setup guide

Generate a Access Token as described in [Zendesk Chat docs](https://developer.zendesk.com/rest_api/docs/chat/auth)

We recommend creating a restricted, read-only key specifically for Airbyte access. This will allow you to control which resources Airbyte should be able to access.

## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.1.2   | 2021-08-17 | [5476](https://github.com/airbytehq/airbyte/pull/5476) | Correct field unread to boolean type |
| 0.1.1   | 2021-06-09 | [3973](https://github.com/airbytehq/airbyte/pull/3973) | Add `AIRBYTE_ENTRYPOINT` for Kubernetes support |
| 0.1.0   | 2021-05-03 | [3088](https://github.com/airbytehq/airbyte/pull/3088) | Initial release |