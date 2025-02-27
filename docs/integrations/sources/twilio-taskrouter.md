# Twilio Taskrouter

This page contains the setup guide and reference information for the Twilio Taskrouter source connector.

## Prerequisites

Twilio Taskroute HTTP requests to the REST API are protected with HTTP Basic authentication. You will use your Twilio Account SID as the username and your Auth Token as the password for HTTP Basic authentication. You will also have to use your Workspace ID as the sid if you wish to access a particular workspace or it's subresources.

You can find your Account SID and Auth Token on your [dashboard](https://www.twilio.com/user/account) by scrolling down the console once you have created a Twilio account.
You can find [Taskrouter](https://console.twilio.com/develop/explore) in the Explore Products page under Solutions in the list. Click on it to expand a panel in the sidebar and click on Workspaces to be taken to your created workspaces. Each workspace has it's unique ID as SID with which you can access the streams.

See [docs](https://www.twilio.com/docs/taskrouter/api) for more details.

## Setup guide

## Step 1: Set up the Twilio Takrouter connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Twilio connector and select **Twilio Taskrouter** from the Source/Destination type dropdown.
4. Enter your `account_sid`.
5. Enter your `auth_token`.
6. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your `account_sid`.
4. Enter your `auth_token`.
5. Click **Set up source**.

## Supported sync modes

The Twilio source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | No         |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |

## Supported Streams

- [Workspaces](https://www.twilio.com/docs/taskrouter/api/workspace)
- [All Workspaces](https://www.twilio.com/docs/taskrouter/api/workspace)
- [Workers](https://www.twilio.com/docs/taskrouter/api/worker)

## Performance considerations

The Twilio Taskrouter connector will gracefully handle rate limits.
For more information, see [the Twilio docs for rate limitations](https://support.twilio.com/hc/en-us/articles/360044308153-Twilio-API-response-Error-429-Too-Many-Requests).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.2.11 | 2025-02-22 | [54514](https://github.com/airbytehq/airbyte/pull/54514) | Update dependencies |
| 0.2.10 | 2025-02-15 | [54089](https://github.com/airbytehq/airbyte/pull/54089) | Update dependencies |
| 0.2.9 | 2025-02-08 | [53522](https://github.com/airbytehq/airbyte/pull/53522) | Update dependencies |
| 0.2.8 | 2025-02-01 | [53040](https://github.com/airbytehq/airbyte/pull/53040) | Update dependencies |
| 0.2.7 | 2025-01-25 | [52391](https://github.com/airbytehq/airbyte/pull/52391) | Update dependencies |
| 0.2.6 | 2025-01-18 | [52003](https://github.com/airbytehq/airbyte/pull/52003) | Update dependencies |
| 0.2.5 | 2025-01-11 | [51394](https://github.com/airbytehq/airbyte/pull/51394) | Update dependencies |
| 0.2.4 | 2024-12-28 | [50816](https://github.com/airbytehq/airbyte/pull/50816) | Update dependencies |
| 0.2.3 | 2024-12-21 | [50366](https://github.com/airbytehq/airbyte/pull/50366) | Update dependencies |
| 0.2.2 | 2024-12-14 | [49383](https://github.com/airbytehq/airbyte/pull/49383) | Update dependencies |
| 0.2.1 | 2024-10-28 | [47458](https://github.com/airbytehq/airbyte/pull/47458) | Update dependencies |
| 0.2.0 | 2024-08-26 | [44776](https://github.com/airbytehq/airbyte/pull/44776) | Refactor connector to manifest-only format |
| 0.1.17 | 2024-08-24 | [44727](https://github.com/airbytehq/airbyte/pull/44727) | Update dependencies |
| 0.1.16 | 2024-08-17 | [44294](https://github.com/airbytehq/airbyte/pull/44294) | Update dependencies |
| 0.1.15 | 2024-08-10 | [43626](https://github.com/airbytehq/airbyte/pull/43626) | Update dependencies |
| 0.1.14 | 2024-08-03 | [43255](https://github.com/airbytehq/airbyte/pull/43255) | Update dependencies |
| 0.1.13 | 2024-07-27 | [42718](https://github.com/airbytehq/airbyte/pull/42718) | Update dependencies |
| 0.1.12 | 2024-07-20 | [42282](https://github.com/airbytehq/airbyte/pull/42282) | Update dependencies |
| 0.1.11 | 2024-07-13 | [41858](https://github.com/airbytehq/airbyte/pull/41858) | Update dependencies |
| 0.1.10 | 2024-07-10 | [41585](https://github.com/airbytehq/airbyte/pull/41585) | Update dependencies |
| 0.1.9 | 2024-07-09 | [41125](https://github.com/airbytehq/airbyte/pull/41125) | Update dependencies |
| 0.1.8 | 2024-07-06 | [40827](https://github.com/airbytehq/airbyte/pull/40827) | Update dependencies |
| 0.1.7 | 2024-06-25 | [40295](https://github.com/airbytehq/airbyte/pull/40295) | Update dependencies |
| 0.1.6 | 2024-06-22 | [39965](https://github.com/airbytehq/airbyte/pull/39965) | Update dependencies |
| 0.1.5 | 2024-06-10 | [38788](https://github.com/airbytehq/airbyte/pull/38788) | Make compatible with the builder |
| 0.1.4 | 2024-06-04 | [39067](https://github.com/airbytehq/airbyte/pull/39067) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.3.  | 2024-04-19 | [37278](https://github.com/airbytehq/airbyte/pull/37278) | Upgrade to CDK 0.80.0 and manage dependencies with Poetry.                      |
| 0.1.2   | 2024-04-15 | [37278](https://github.com/airbytehq/airbyte/pull/37278) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.1   | 2024-04-12 | [37278](https://github.com/airbytehq/airbyte/pull/37278) | schema descriptions                                                             |
| 0.1.0   | 2022-11-18 | [18685](https://github.com/airbytehq/airbyte/pull/18685) | 🎉 New Source: Twilio Taskrouter API [low-code cdk]                             |

</details>
