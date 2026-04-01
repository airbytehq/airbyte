# Slack

<HideInUI>

This page contains the setup guide and reference information for the [Slack](https://www.slack.com) source connector.

</HideInUI>

## Prerequisites

Before you begin, have the following ready:

- Administrator access to an active Slack workspace
- A Slack App with OAuth credentials (preferred) or a legacy Slack API token

## Setup guide

### Step 1: Set up Slack

The following instructions guide you through creating a Slack app. Airbyte can only replicate messages from channels that the app has been added to.

:::info
If you are using a legacy Slack API token, you can skip this section.
:::

:::warning
**OAuth-only rate limit note:** When authenticating via **OAuth**, the Slack source applies a stricter API budget for the **Channel Messages** and **Threads** streams (effectively one request per minute). To avoid slowing down other Slack streams, we recommend creating a separate connection for these two streams. See the [Rate limiting](#rate-limiting) section for details.

If you authenticate using a **legacy Slack API token**, this OAuth-specific limit does **not** apply.
:::

To create a Slack app, read this [tutorial](https://api.slack.com/tutorials/tracks/getting-a-token), or follow these instructions:

1. Go to [Your Apps](https://api.slack.com/apps).
2. Click **Create New App**, then select **From Scratch**.
3. Choose a name for your app, select your Slack workspace, and click **Create App**.
4. In the navigation menu, select **OAuth & Permissions**.
5. Scroll to **Scopes** and add the following **Bot Token Scopes**:

   | Scope | Required for |
   | :--- | :--- |
   | `channels:history` | Channel Messages, Threads |
   | `channels:join` | Automatically joining public channels |
   | `channels:read` | Channels |
   | `groups:read` | Private channels (Channels stream) |
   | `groups:history` | Private channel messages and threads |
   | `im:history` | Direct message history |
   | `im:read` | Direct message channel listing |
   | `mpim:history` | Group direct message history |
   | `mpim:read` | Group direct message channel listing |
   | `users:read` | Users |

   :::tip
   If you plan to sync data beyond what the connector streams cover, you can also add `files:read`, `reactions:read`, `team:read`, `usergroups:read`, and `users.profile:read`. These are not required by the connector but may be useful for future streams or custom integrations.
   :::

6. At the top of the **OAuth & Permissions** page, click **Install to Workspace**. This generates a Bot User OAuth Token. Copy this token if you are using API token authentication.
7. Go to your Slack workspace. For any public channel, open **Channel details**, click **More**, then select **Add apps**.
8. Search for and add your app. If you are using the Slack desktop app, you may need to restart it to detect the new app. Add the app to every channel you want to sync.

:::note
If you are using a legacy Slack API token, a refresh token is not required because these tokens do not expire. For more information, see [Token rotation](https://api.slack.com/authentication/rotation).
:::

### Step 2: Set up the Slack connector in Airbyte

<!-- env:cloud -->

**For Airbyte Cloud:**

1. In the navigation bar, click **Sources**. 
2. Click **New source**.
3. Find and click **Slack**.
4. Click **Authenticate your Slack account**. Log in and authorize Airbyte to access your Slack account.
<FieldAnchor field="join_channels">
5. Toggle **Join all channels** if you want the bot to automatically join all public channels. If disabled, you must manually add the bot to each channel you want to sync.
</FieldAnchor>
<FieldAnchor field="start_date">
6. **Start Date**: Any data before this date will not be replicated.
</FieldAnchor>
<FieldAnchor field="lookback_window">
7. **Threads Lookback window (Days)**: The number of days to look back for thread replies.
</FieldAnchor>
<FieldAnchor field="channel_filter">
8. (Optional) **Channel filter**: A list of channel names (without the leading `#`) to limit which channels are synced. If empty, all channels are synced.
</FieldAnchor>
<FieldAnchor field="include_private_channels">
9. (Optional) **Include private channels**: Toggle on to sync data from private channels. You must manually add the bot to private channels even if **Join all channels** is enabled.
</FieldAnchor>
10. Click **Set up source**. The app you created in Step 1 must be added to the channels you want to sync.
<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

1. In the navigation bar, click **Sources**. 
2. Click **New source**.
3. Find and click **Slack**.
4. Click **Sign in via Slack (OAuth)**. Enter the Access Token, Client ID, and Client Secret. Alternatively, enter the API Token from Step 1.
5. Toggle **Join all channels** if you want the bot to automatically join all public channels. If disabled, you must manually add the bot to each channel you want to sync.
6. **Start Date**: Any data before this date will not be replicated.
7. **Threads Lookback window (Days)**: The number of days to look back for thread replies.
8. (Optional) **Channel filter**: A list of channel names (without the leading `#`) to limit which channels are synced. If empty, all channels are synced.
9. (Optional) **Include private channels**: Toggle on to sync data from private channels. You must manually add the bot to private channels even if **Join all channels** is enabled.
10. Click **Set up source**. The app you created in Step 1 must be added to the channels you want to sync.
<!-- /env:oss -->

<HideInUI>

## Supported sync modes

The Slack source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | Yes        |
| Namespaces        | No         |

## Supported streams

The Slack source connector uses the [Conversations API](https://api.slack.com/docs/conversations-api) under the hood.

- [Channels (Conversations)](https://api.slack.com/methods/conversations.list)
- [Channel Members (Conversation Members)](https://api.slack.com/methods/conversations.members)
- [Channel Messages (Conversation History)](https://api.slack.com/methods/conversations.history) — Replicates messages from non-archived public and private channels that the app is a member of.
- [Users](https://api.slack.com/methods/users.list)
- [Threads (Conversation Replies)](https://api.slack.com/methods/conversations.replies)

## Performance considerations

The connector is restricted by Slack [rate limits](https://api.slack.com/docs/rate-limits).

To improve performance, sync only the channels you need by specifying the **Channel filter** in the connector configuration.

If you are syncing a large amount of data, such as historical messages, you can increase the **Number of concurrent workers** setting (default is 2). Higher values increase parallelism but also increase the risk of hitting Slack rate limits. Monitor sync logs for rate limit errors.

## Data type map

| Integration Type | Airbyte Type |
| :--------------- | :----------- |
| `string`         | `string`     |
| `number`         | `number`     |
| `array`          | `array`      |
| `object`         | `object`     |

## Limitations & Troubleshooting

<details>
<summary>
Expand to see details about Slack connector limitations and troubleshooting.
</summary>

### Connector limitations

#### Rate limiting

Slack has [rate limit restrictions](https://api.slack.com/docs/rate-limits).

###### Rate limits for Channel Messages and Threads streams

**OAuth authentication:** For apps authenticated via OAuth, the connector enforces a stricter budget on:
- [`conversations.replies`](https://api.slack.com/methods/conversations.replies)
- [`conversations.history`](https://api.slack.com/methods/conversations.history)

These two streams are effectively limited to **one request per minute**. Consider creating a **separate connection** for them so other streams (Users, Channels, Channel Members, etc.) are not slowed down.

**Legacy API token authentication:** When using a legacy Slack API token, this OAuth-specific one-per-minute policy does **not** apply; only Slack’s general rate limits apply.

### Troubleshooting

- Check out common troubleshooting issues for the Slack source connector on our Airbyte Forum [here](https://github.com/airbytehq/airbyte/discussions).


</details>

</HideInUI>


## Changelog

<details>
  <summary>Expand to review</summary>

| Version    | Date       | Pull Request                                             | Subject                                                                                                                                                                |
|:-----------|:-----------|:---------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 3.1.14 | 2026-03-27 | [75197](https://github.com/airbytehq/airbyte/pull/75197) | Add declarative OAuth with `oauth_connector_input_specification` and granular scopes |
| 3.1.13 | 2026-03-24 | [75329](https://github.com/airbytehq/airbyte/pull/75329) | Update dependencies |
| 3.1.12 | 2026-03-10 | [74598](https://github.com/airbytehq/airbyte/pull/74598) | Update dependencies |
| 3.1.11 | 2026-02-24 | [73948](https://github.com/airbytehq/airbyte/pull/73948) | Update dependencies |
| 3.1.10 | 2026-02-17 | [73564](https://github.com/airbytehq/airbyte/pull/73564) | Update dependencies |
| 3.1.9 | 2026-02-10 | [73208](https://github.com/airbytehq/airbyte/pull/73208) | Update dependencies |
| 3.1.8 | 2026-02-03 | [69495](https://github.com/airbytehq/airbyte/pull/69495) | Update dependencies |
| 3.1.7 | 2025-10-29 | [68772](https://github.com/airbytehq/airbyte/pull/68772) | Update dependencies |
| 3.1.6 | 2025-10-21 | [68282](https://github.com/airbytehq/airbyte/pull/68282) | Update dependencies |
| 3.1.5 | 2025-10-14 | [67767](https://github.com/airbytehq/airbyte/pull/67767) | Update dependencies |
| 3.1.4 | 2025-10-07 | [67449](https://github.com/airbytehq/airbyte/pull/67449) | Update dependencies |
| 3.1.3 | 2025-10-06 | [67084](https://github.com/airbytehq/airbyte/pull/67084) | Update dependencies |
| 3.1.2 | 2025-09-30 | [66566](https://github.com/airbytehq/airbyte/pull/66566) | Update to CDK v7 |
| 3.1.1 | 2025-09-24 | [66640](https://github.com/airbytehq/airbyte/pull/66640) | Update dependencies |
| 3.1.0 | 2025-09-18 | [66501](https://github.com/airbytehq/airbyte/pull/66501) | Promoting release candidate 3.1.0-rc.1 to a main version. |
| 3.1.0-rc.1 | 2025-09-10 | [64160](https://github.com/airbytehq/airbyte/pull/64160) | Migrate to manifest-only.                                                                                                                                              |
| 3.0.0      | 2025-09-10 | [65937](https://github.com/airbytehq/airbyte/pull/65937) | Add migration guide for missing state issue                                                                                                                            |
| 2.2.0      | 2025-09-10 | [66155](https://github.com/airbytehq/airbyte/pull/66155) | Promoting release candidate 2.2.0-rc.7 to a main version.                                                                                                              |
| 2.2.0-rc.7 | 2025-08-21 | [65132](https://github.com/airbytehq/airbyte/pull/65132) | Update API budget to depend on auth method (rate limits apply only with OAuth).                                                                                        |
| 2.2.0-rc.6 | 2025-08-14 | [64553](https://github.com/airbytehq/airbyte/pull/64553) | Add API budget for Threads and Channel Messages streams.                                                                                                               |
| 2.2.0-rc.5 | 2025-08-06 | [64530](https://github.com/airbytehq/airbyte/pull/64530) | Set use_cache = true for Channels and Channel Messages streams.                                                                                                        |
| 2.2.0-rc.4 | 2025-08-04 | [64486](https://github.com/airbytehq/airbyte/pull/64486) | Add backoff strategy for Channels stream.                                                                                                                              |
| 2.2.0-rc.3 | 2025-07-29 | [64107](https://github.com/airbytehq/airbyte/pull/64107) | Add custom partition router.                                                                                                                                           |
| 2.2.0-rc.2 | 2025-07-23 | [63732](https://github.com/airbytehq/airbyte/pull/63732) | Enable progressive rollout.                                                                                                                                            |
| 2.2.0-rc.1 | 2025-07-23 | [63278](https://github.com/airbytehq/airbyte/pull/63278) | Migrate Threads stream to manifest.                                                                                                                                    |
| 2.1.0      | 2025-07-11 | [62930](https://github.com/airbytehq/airbyte/pull/62930) | Promoting release candidate 2.1.0-rc.1 to a main version.                                                                                                              |
| 2.1.0-rc.1 | 2025-07-07 | [62110](https://github.com/airbytehq/airbyte/pull/62110) | Bump cdk v6                                                                                                                                                            |
| 2.0.2      | 2025-07-05 | [62709](https://github.com/airbytehq/airbyte/pull/62709) | Update dependencies                                                                                                                                                    |
| 2.0.1      | 2025-06-28 | [51965](https://github.com/airbytehq/airbyte/pull/51965) | Update dependencies                                                                                                                                                    |
| 2.0.0      | 2025-06-25 | [62055](https://github.com/airbytehq/airbyte/pull/62055) | Add breaking change notification for migrating to the new Slack Marketplace application to retain higher rate limits.                                                  |
| 1.3.2      | 2025-01-11 | [43812](https://github.com/airbytehq/airbyte/pull/43812) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 1.3.1      | 2024-07-24 | [42485](https://github.com/airbytehq/airbyte/pull/42485) | Fix MRO error for `IncrementalMessageStream`                                                                                                                           |
| 1.3.0      | 2024-07-17 | [41994](https://github.com/airbytehq/airbyte/pull/41994) | Migrate to CDK v3.5.1                                                                                                                                                  |
| 1.2.0      | 2024-07-16 | [41970](https://github.com/airbytehq/airbyte/pull/41970) | Migrate to CDK v2.4.0                                                                                                                                                  |
| 1.1.13     | 2024-07-13 | [41863](https://github.com/airbytehq/airbyte/pull/41863) | Update dependencies                                                                                                                                                    |
| 1.1.12     | 2024-07-10 | [41485](https://github.com/airbytehq/airbyte/pull/41485) | Update dependencies                                                                                                                                                    |
| 1.1.11     | 2024-07-09 | [41231](https://github.com/airbytehq/airbyte/pull/41231) | Update dependencies                                                                                                                                                    |
| 1.1.10     | 2024-07-06 | [40839](https://github.com/airbytehq/airbyte/pull/40839) | Update dependencies                                                                                                                                                    |
| 1.1.9      | 2024-06-25 | [40347](https://github.com/airbytehq/airbyte/pull/40347) | Update dependencies                                                                                                                                                    |
| 1.1.8      | 2024-06-22 | [40166](https://github.com/airbytehq/airbyte/pull/40166) | Update dependencies                                                                                                                                                    |
| 1.1.7      | 2025-06-14 | [39343](https://github.com/airbytehq/airbyte/pull/39343) | Update state handling for `threads` Python stream                                                                                                                      |
| 1.1.6      | 2024-06-12 | [39416](https://github.com/airbytehq/airbyte/pull/39416) | Respect `include_private_channels` option in `threads` stream                                                                                                          |
| 1.1.5      | 2024-06-10 | [39132](https://github.com/airbytehq/airbyte/pull/39132) | Convert string state to float for `threads` stream                                                                                                                     |
| 1.1.4      | 2024-06-06 | [39271](https://github.com/airbytehq/airbyte/pull/39271) | [autopull] Upgrade base image to v1.2.2                                                                                                                                |
| 1.1.3      | 2024-06-05 | [39121](https://github.com/airbytehq/airbyte/pull/39121) | Change cursor format for `channel_messages` stream to `%s_as_float`                                                                                                    |
| 1.1.2      | 2024-05-23 | [38619](https://github.com/airbytehq/airbyte/pull/38619) | Fix cursor granularity for the `channel_messages` stream                                                                                                               |
| 1.1.1      | 2024-05-02 | [36661](https://github.com/airbytehq/airbyte/pull/36661) | Schema descriptions                                                                                                                                                    |
| 1.1.0      | 2024-04-18 | [37332](https://github.com/airbytehq/airbyte/pull/37332) | Add the capability to sync from private channels                                                                                                                       |
| 1.0.0      | 2024-04-02 | [35477](https://github.com/airbytehq/airbyte/pull/35477) | Migration to low-code CDK                                                                                                                                              |
| 0.4.1      | 2024-03-27 | [36579](https://github.com/airbytehq/airbyte/pull/36579) | Upgrade airbyte-cdk version to emit record counts as floats                                                                                                            |
| 0.4.0      | 2024-03-19 | [36267](https://github.com/airbytehq/airbyte/pull/36267) | Pin airbyte-cdk version to `^0`                                                                                                                                        |
| 0.3.9      | 2024-02-12 | [35157](https://github.com/airbytehq/airbyte/pull/35157) | Manage dependencies with Poetry                                                                                                                                        |
| 0.3.8      | 2024-02-09 | [35131](https://github.com/airbytehq/airbyte/pull/35131) | Fixed the issue when `schema discovery` fails with `502` due to the platform timeout                                                                                   |
| 0.3.7      | 2024-01-10 | [1234](https://github.com/airbytehq/airbyte/pull/1234)   | Prepare for airbyte-lib                                                                                                                                                |
| 0.3.6      | 2023-11-21 | [32707](https://github.com/airbytehq/airbyte/pull/32707) | Threads: do not use client-side record filtering                                                                                                                       |
| 0.3.5      | 2023-10-19 | [31599](https://github.com/airbytehq/airbyte/pull/31599) | Base image migration: remove Dockerfile and use the python-connector-base image                                                                                        |
| 0.3.4      | 2023-10-06 | [31134](https://github.com/airbytehq/airbyte/pull/31134) | Update CDK and remove non iterable return from records                                                                                                                 |
| 0.3.3      | 2023-09-28 | [30580](https://github.com/airbytehq/airbyte/pull/30580) | Add `bot_id` field to threads schema                                                                                                                                   |
| 0.3.2      | 2023-09-20 | [30613](https://github.com/airbytehq/airbyte/pull/30613) | Set default value for channel_filters during discover                                                                                                                  |
| 0.3.1      | 2023-09-19 | [30570](https://github.com/airbytehq/airbyte/pull/30570) | Use default availability strategy                                                                                                                                      |
| 0.3.0      | 2023-09-18 | [30521](https://github.com/airbytehq/airbyte/pull/30521) | Add unexpected fields to streams `channel_messages`, `channels`, `threads`, `users`                                                                                    |
| 0.2.0      | 2023-05-24 | [26497](https://github.com/airbytehq/airbyte/pull/26497) | Fixed `lookback window` value limitations                                                                                                                              |
| 0.1.26     | 2023-05-17 | [26186](https://github.com/airbytehq/airbyte/pull/26186) | Limited the `lookback window` range for input configuration                                                                                                            |
| 0.1.25     | 2023-03-20 | [22889](https://github.com/airbytehq/airbyte/pull/22889) | Specified date formatting in specification                                                                                                                             |
| 0.1.24     | 2023-03-20 | [24126](https://github.com/airbytehq/airbyte/pull/24126) | Increase page size to 1000                                                                                                                                             |
| 0.1.23     | 2023-02-21 | [21907](https://github.com/airbytehq/airbyte/pull/21907) | Do not join channels that not gonna be synced                                                                                                                          |
| 0.1.22     | 2023-01-27 | [22022](https://github.com/airbytehq/airbyte/pull/22022) | Set `AvailabilityStrategy` for streams explicitly to `None`                                                                                                            |
| 0.1.21     | 2023-01-12 | [21321](https://github.com/airbytehq/airbyte/pull/21321) | Retry Timeout error                                                                                                                                                    |
| 0.1.20     | 2022-12-21 | [20767](https://github.com/airbytehq/airbyte/pull/20767) | Update schema                                                                                                                                                          |
| 0.1.19     | 2022-12-01 | [19970](https://github.com/airbytehq/airbyte/pull/19970) | Remove OAuth2.0 broken `refresh_token` support                                                                                                                         |
| 0.1.18     | 2022-09-28 | [17315](https://github.com/airbytehq/airbyte/pull/17315) | Always install latest version of Airbyte CDK                                                                                                                           |
| 0.1.17     | 2022-08-28 | [16085](https://github.com/airbytehq/airbyte/pull/16085) | Increase unit test coverage                                                                                                                                            |
| 0.1.16     | 2022-08-28 | [16050](https://github.com/airbytehq/airbyte/pull/16050) | Fix SATs                                                                                                                                                               |
| 0.1.15     | 2022-03-31 | [11613](https://github.com/airbytehq/airbyte/pull/11613) | Add 'channel_filter' config and improve performance                                                                                                                    |
| 0.1.14     | 2022-01-26 | [9575](https://github.com/airbytehq/airbyte/pull/9575)   | Correct schema                                                                                                                                                         |
| 0.1.13     | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499)   | Remove base-python dependencies                                                                                                                                        |
| 0.1.12     | 2021-10-07 | [6570](https://github.com/airbytehq/airbyte/pull/6570)   | Implement OAuth support with OAuth authenticator                                                                                                                       |
| 0.1.11     | 2021-08-27 | [5830](https://github.com/airbytehq/airbyte/pull/5830)   | Fix sync operations hang forever issue                                                                                                                                 |
| 0.1.10     | 2021-08-27 | [5697](https://github.com/airbytehq/airbyte/pull/5697)   | Fix max retries issue                                                                                                                                                  |
| 0.1.9      | 2021-07-20 | [4860](https://github.com/airbytehq/airbyte/pull/4860)   | Fix reading threads issue                                                                                                                                              |
| 0.1.8      | 2021-07-14 | [4683](https://github.com/airbytehq/airbyte/pull/4683)   | Add float_ts primary key                                                                                                                                               |
| 0.1.7      | 2021-06-25 | [3978](https://github.com/airbytehq/airbyte/pull/3978)   | Release Slack CDK Connector                                                                                                                                            |

</details>
