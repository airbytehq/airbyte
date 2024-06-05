# Postmarkapp

## Overview

The Postmarkapp source can sync data from the [Postmarkapp API](https://postmarkapp.com/developer)

## Requirements

Postmarkapp requires an API key to make request and retrieve data. You can find your API key in the [Postmarkapp dashboard](https://account.postmarkapp.com/servers/9708911/credentials).

## Streams

Current supported streams:

Server-API

- [Bounces: Deliverystats](https://postmarkapp.com/developer/api/bounce-api#delivery-stats): Lets you access all reports regarding your bounces for a specific server. Bounces are available for 45 days after a bounce.
- [Message-Streams](https://postmarkapp.com/developer/api/message-streams-api#list-message-streams): Lets you manage message streams for a specific server. Please note: A Server may have up to 10 Streams, including the default ones. Default Streams cannot be deleted, and Servers can only have 1 Inbound Stream.
- [Outbound stats](https://account.postmarkapp.com/servers/9708911/credentials): Lets you get all of the statistics of your outbound emails for a specific server. These statistics are stored permantently and do not expire. All stats use EST timezone

Account-API

- [Servers](https://postmarkapp.com/developer/api/servers-api): Lets you manage servers for a specific account.
- [Domains](https://postmarkapp.com/developer/api/domains-api): Gets a list of domains containing an overview of the domain and authentication status.
- [Sender signatures](https://postmarkapp.com/developer/api/signatures-api): Gets a list of sender signatures containing brief details associated with your account.

## Setup guide

## Step 1: Set up the Postmarkapp connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, select **Postmarkapp** from the Source type dropdown.
4. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source (Postmarkapp).
3. Click **Set up source**.

## Supported sync modes

The Postmarkapp source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |
| Namespaces        | No         |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.1.4 | 2024-06-04 | [39062](https://github.com/airbytehq/airbyte/pull/39062) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.3 | 2024-04-19 | [37232](https://github.com/airbytehq/airbyte/pull/37232) | Upgrade to CDK 0.80.0 and manage dependencies with Poetry. |
| 0.1.2 | 2024-04-15 | [37232](https://github.com/airbytehq/airbyte/pull/37232) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.1 | 2024-04-12 | [37232](https://github.com/airbytehq/airbyte/pull/37232) | schema descriptions |
| 0.1.0   | 2022-11-09 | 18220                                                    | 🎉 New Source: Postmarkapp API [low-code CDK]                                   |

</details>