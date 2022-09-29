# Zendesk Chat

This page contains the setup guide and reference information for the Zendesk Chat source connector.

## Prerequisites

- Zendesk Account with permission to access data from accounts you want to sync
- Access Token as described in [Zendesk Chat docs](https://developer.zendesk.com/rest_api/docs/chat/auth). We recommend creating a restricted, read-only key specifically for Airbyte access. This will allow you to control which resources Airbyte should be able to access.

## Setup guide

## Step 1: Set up Zendesk Chat

Generate an Access Token as described in [Zendesk Chat docs](https://developer.zendesk.com/rest_api/docs/chat/auth)


## Step 2: Set up the Zendesk Chat connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Zendesk Chat connector and select **Zendesk Chat** from the Source type dropdown. 
4. Select `Authenticate your account` and log in and Authorize to the Zendesk account.
5. Enter your `subdomain`.
6. Enter your `start_time`. 
7. Enter your `access_token`. 
8. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source. 
3. Enter your `subdomain`.
4. Enter your `start_time`. 
5. Enter your `access_token`. 
6. Click **Set up source**.

## Supported sync modes

The Zendesk Chat source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | Yes        |
| SSL connection    | Yes        |

## Supported Streams

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

## Performance considerations

The connector is restricted by normal Zendesk [requests limitation](https://developer.zendesk.com/rest_api/docs/voice-api/introduction#rate-limits).

## Data type map

| Integration Type | Airbyte Type |
| :--------------- | :----------- |
| `string`         | `string`     |
| `number`         | `number`     |
| `array`          | `array`      |
| `object`         | `object`     |

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                                          |
| :------ | :--------- | :------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------- |
| 0.1.9   | 2022-08-23 | [15879](https://github.com/airbytehq/airbyte/pull/15879) | Corrected specification and stream schemas to support backward capability                                                                          |
| 0.1.8   | 2022-06-28 | [13387](https://github.com/airbytehq/airbyte/pull/13387) | Add state checkpoint to allow long runs                                                                          |
| 0.1.7   | 2022-05-25 | [12883](https://github.com/airbytehq/airbyte/pull/12883) | Pass timeout in request to prevent a stuck connection                                                            |
| 0.1.6   | 2021-12-15 | [7313](https://github.com/airbytehq/airbyte/pull/7313)   | Add support of `OAuth 2.0` authentication. Fixed the issue with `created_at` can now be `null` for `bans` stream |
| 0.1.5   | 2021-12-06 | [8425](https://github.com/airbytehq/airbyte/pull/8425)   | Update title, description fields in spec                                                                         |
| 0.1.4   | 2021-11-22 | [8166](https://github.com/airbytehq/airbyte/pull/8166)   | Make `Chats` stream incremental + add tests for all streams                                                      |
| 0.1.3   | 2021-10-21 | [7210](https://github.com/airbytehq/airbyte/pull/7210)   | Chats stream is only getting data from first page                                                                |
| 0.1.2   | 2021-08-17 | [5476](https://github.com/airbytehq/airbyte/pull/5476)   | Correct field unread to boolean type                                                                             |
| 0.1.1   | 2021-06-09 | [3973](https://github.com/airbytehq/airbyte/pull/3973)   | Add `AIRBYTE_ENTRYPOINT` for Kubernetes support                                                                  |
| 0.1.0   | 2021-05-03 | [3088](https://github.com/airbytehq/airbyte/pull/3088)   | Initial release                                                                                                  |
