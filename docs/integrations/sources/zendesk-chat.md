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

### Connect using `OAuth 2.0` option:
1. Select `OAuth2.0` in `Authorization Method`
2. Click on `authenticate your Zendesk Chat account`
2. Proceed the authentication using your credentials for your Zendesk account.

### Connect using `Access Token` option:
1. Generate a Access Token as described in [Zendesk Chat docs](https://developer.zendesk.com/rest_api/docs/chat/auth)
2. Use the generated `access_token` in Airbyte connection.


### Setup guide

Generate a Access Token as described in [Zendesk Chat docs](https://developer.zendesk.com/rest_api/docs/chat/auth)

We recommend creating a restricted, read-only key specifically for Airbyte access. This will allow you to control which resources Airbyte should be able to access.

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.8 | 2022-06-28 | [13387](https://github.com/airbytehq/airbyte/pull/13387) | Add state checkpoint to allow long runs |
| 0.1.7 | 2022-05-25 | [12883](https://github.com/airbytehq/airbyte/pull/12883) | Passing timeout in request to prevent a stuck connection |
| 0.1.6 | 2021-12-15 | [7313](https://github.com/airbytehq/airbyte/pull/7313) | Added support of `OAuth 2.0` authentication. [8819](https://github.com/airbytehq/airbyte/pull/8819) Fixed the issue with `created_at` can now be `null` for `bans` stream |
| 0.1.5 | 2021-12-06 | [8425](https://github.com/airbytehq/airbyte/pull/8425) | Update title, description fields in spec |
| 0.1.4 | 2021-11-22 | [8166](https://github.com/airbytehq/airbyte/pull/8166) | Make `Chats` stream incremental + add tests for all streams |
| 0.1.3 | 2021-10-21 | [7210](https://github.com/airbytehq/airbyte/pull/7210) | Chats stream is only getting data from first page |
| 0.1.2 | 2021-08-17 | [5476](https://github.com/airbytehq/airbyte/pull/5476) | Correct field unread to boolean type |
| 0.1.1 | 2021-06-09 | [3973](https://github.com/airbytehq/airbyte/pull/3973) | Add `AIRBYTE_ENTRYPOINT` for Kubernetes support |
| 0.1.0 | 2021-05-03 | [3088](https://github.com/airbytehq/airbyte/pull/3088) | Initial release |

