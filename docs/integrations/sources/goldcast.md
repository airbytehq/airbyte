# Goldcast

This page contains the setup guide and reference information for the Goldcast source connector.

## Prerequisites

- A [Goldcast Pro plan](https://www.goldcast.io/pricing) at least
<!-- env:oss -->
- A Goldcast API Token generated [here](https://help.goldcast.io/hc/en-us/articles/22931655725723-How-To-Create-an-API-Token-in-Goldcast)
  <!-- /env:oss -->

## Setup guide

<!-- env:oss -->

### Step 1: (For Airbyte Open Source) Setup a Goldcast Account

Setup and account in [Goldcast](https://www.goldcast.io/) and makr sure you have a [Goldcast Pro plan](https://www.goldcast.io/pricing) is required. The Starter plan does not allow for API access.


### Step 2: (For Airbyte Open Source) Obtain an access token

A simple access token is all that is needed to access Goldcast API. This token is generated [here](https://help.goldcast.io/hc/en-us/articles/22931655725723-How-To-Create-an-API-Token-in-Goldcast).


#### For Airbyte Cloud:

To set up Goldcast as a source in Airbyte Cloud:

1. [Log in to your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. Find and select **Goldcast** from the list of available sources.
4. Enter a **Source name** of your choosing.
5. Enter the **access_key** you obtained from Goldcast.
6. Click **Set up source** and wait for the tests to complete.

<!-- /env:cloud -->

<!-- env:oss -->

#### For Airbyte Open Source:

To set up Goldcast as a source in Airbyte Open Source:

1. Log in to your Airbyte Open Source account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. Find and select **Goldcast** from the list of available sources.
4. Enter a **Source name** of your choosing.
5. Enter the **access_key** you obtained from Goldcast.
6. Click **Set up source** and wait for the tests to complete.

<!-- /env:oss -->

## Supported Sync Modes

The Goldcast source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)

Incremental modes are not supported as the Goldcast API does not contain a cursor field (modified at field for example) at the time of this writing.

## Supported Streams

The Goldcast source connector can sync the following tables. It can also sync custom queries using GAQL.

### Main Tables

Link to Goldcast API documentation [here](https://customapi.goldcast.io/swagger-ui/#/).

- [organization](https://customapi.goldcast.io/swagger-ui/#/Organization/List%20organization)

- [events](https://customapi.goldcast.io/swagger-ui/#/Event/List%20events)

- [event_members](https://customapi.goldcast.io/swagger-ui/#/Event%20members/List%20event%20members)

This is a child stream of the events stream representing users associated to events.

- [webinars](https://customapi.goldcast.io/swagger-ui/#/Webinars/Retrieve%20webinars)

This is a child stream of the events stream indicating webinars that belong to the parent event.

- [tracks](https://customapi.goldcast.io/swagger-ui/#/Tracks/List%20tracks)

- [agenda_items](https://customapi.goldcast.io/swagger-ui/#/Agenda%20item/List%20agenda%20item)

- [discussion_groups](https://customapi.goldcast.io/swagger-ui/#/Discussion%20groups/List%20discussion%20groups)




## Changelog

<details>
  <summary>Expand to review</summary>

| Version  | Date       | Pull Request                                             | Subject                                                                                                                              |
|:---------|:-----------|:---------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------|
| 0.2.12 | 2025-02-08 | [53338](https://github.com/airbytehq/airbyte/pull/53338) | Update dependencies |
| 0.2.11 | 2025-02-01 | [52838](https://github.com/airbytehq/airbyte/pull/52838) | Update dependencies |
| 0.2.10 | 2025-01-25 | [52325](https://github.com/airbytehq/airbyte/pull/52325) | Update dependencies |
| 0.2.9 | 2025-01-18 | [51636](https://github.com/airbytehq/airbyte/pull/51636) | Update dependencies |
| 0.2.8 | 2025-01-11 | [51103](https://github.com/airbytehq/airbyte/pull/51103) | Update dependencies |
| 0.2.7 | 2024-12-28 | [50571](https://github.com/airbytehq/airbyte/pull/50571) | Update dependencies |
| 0.2.6 | 2024-12-21 | [49998](https://github.com/airbytehq/airbyte/pull/49998) | Update dependencies |
| 0.2.5 | 2024-12-14 | [49480](https://github.com/airbytehq/airbyte/pull/49480) | Update dependencies |
| 0.2.4 | 2024-12-12 | [49158](https://github.com/airbytehq/airbyte/pull/49158) | Update dependencies |
| 0.2.3 | 2024-11-04 | [48148](https://github.com/airbytehq/airbyte/pull/48148) | Update dependencies |
| 0.2.2 | 2024-10-29 | [47875](https://github.com/airbytehq/airbyte/pull/47875) | Update dependencies |
| 0.2.1 | 2024-10-28 | [47533](https://github.com/airbytehq/airbyte/pull/47533) | Update dependencies |
| 0.2.0 | 2024-08-22 | [44568](https://github.com/airbytehq/airbyte/pull/44568) | Refactor connector to manifest-only format |
| 0.1.8 | 2024-08-12 | [43804](https://github.com/airbytehq/airbyte/pull/43804) | Update dependencies |
| 0.1.7 | 2024-08-10 | [43522](https://github.com/airbytehq/airbyte/pull/43522) | Update dependencies |
| 0.1.6 | 2024-08-03 | [43284](https://github.com/airbytehq/airbyte/pull/43284) | Update dependencies |
| 0.1.5 | 2024-07-27 | [42616](https://github.com/airbytehq/airbyte/pull/42616) | Update dependencies |
| 0.1.4 | 2024-07-20 | [42237](https://github.com/airbytehq/airbyte/pull/42237) | Update dependencies |
| 0.1.3 | 2024-07-13 | [41806](https://github.com/airbytehq/airbyte/pull/41806) | Update dependencies |
| 0.1.2 | 2024-07-10 | [41406](https://github.com/airbytehq/airbyte/pull/41406) | Update dependencies |
| 0.1.1 | 2024-07-09 | [41263](https://github.com/airbytehq/airbyte/pull/41263) | Update dependencies |
| 0.1.0 | 2024-06-26 | [38786](https://github.com/airbytehq/airbyte/pull/38786) | New Source: Goldcast |
</details>
