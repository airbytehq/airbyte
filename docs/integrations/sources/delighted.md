# Delighted

This page contains the setup guide and reference information for the [Delighted](https://delighted.com/) source connector.

## Prerequisites

- A Delighted API Key.
- A desired start date and time. Only data added on and after this point will be replicated.

## Setup guide

### Step 1: Obtain a Delighted API Key

To set up the Delighted source connector, you'll need a Delighted API key. For detailed instructions, please refer to the
[official Delighted documentation](https://app.delighted.com/docs/api).

### Step 2: Set up the Delighted connector in Airbyte

1. [Log in to your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account, or navigate to the Airbyte Open Source dashboard.
2. From the Airbyte UI, click **Sources**, then click on **+ New Source** and select **Delighted** from the list of available sources.
3. Enter a **Source name** of your choosing.
4. Enter your **Delighted API Key**.
5. In the **Replication Start Date** field, enter the desired UTC date and time. Only the data added on and after this date will be replicated.

:::note
If you are configuring this connector programmatically, please format your date as such: `yyyy-mm-ddThh:mm:ssZ`. For example, an input of `2022-05-30T14:50:00Z` signifies a start date of May 30th, 2022 at 2:50 PM UTC. For help converting UTC to your local time,
[use a UTC Time Zone Converter](https://dateful.com/convert/utc).
:::

6. Click **Set up source** and wait for the tests to complete.

## Supported sync modes

The Delighted source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Supported streams

This source is capable of syncing the following core streams:

- [Bounced People](https://app.delighted.com/docs/api/listing-bounced-people)
- [People](https://app.delighted.com/docs/api/listing-people)
- [Survey Responses](https://app.delighted.com/docs/api/listing-survey-responses)
- [Unsubscribed People](https://app.delighted.com/docs/api/listing-unsubscribed-people)

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                              |
| :------ | :--------- | :------------------------------------------------------- | :--------------------------------------------------------------------------------------------------- |
| 0.2.9 | 2024-06-04 | [39047](https://github.com/airbytehq/airbyte/pull/39047) | [autopull] Upgrade base image to v1.2.1 |
| 0.2.8 | 2024-05-14 | [38142](https://github.com/airbytehq/airbyte/pull/38142) | Make compatible with the builder |
| 0.2.7 | 2024-04-19 | [37149](https://github.com/airbytehq/airbyte/pull/37149) | Updating to 0.80.0 CDK |
| 0.2.6 | 2024-04-18 | [37149](https://github.com/airbytehq/airbyte/pull/37149) | Manage dependencies with Poetry. |
| 0.2.5 | 2024-04-15 | [37149](https://github.com/airbytehq/airbyte/pull/37149) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.2.4 | 2024-04-12 | [37149](https://github.com/airbytehq/airbyte/pull/37149) | schema descriptions |
| 0.2.3 | 2023-09-08 | [27946](https://github.com/airbytehq/airbyte/pull/27946) | Changed `Date Since` input field title to `Replication Start Date` |
| 0.2.2 | 2023-03-09 | [23909](https://github.com/airbytehq/airbyte/pull/23909) | Updated the input config pattern to accept both `RFC3339` and `datetime string` formats in UI |
| 0.2.1 | 2023-02-14 | [23009](https://github.com/airbytehq/airbyte/pull/23009) | Specified date formatting in specification |
| 0.2.0 | 2022-11-22 | [19822](https://github.com/airbytehq/airbyte/pull/19822) | Migrate to Low code + certify to Beta |
| 0.1.4 | 2022-06-10 | [13439](https://github.com/airbytehq/airbyte/pull/13439) | Change since parameter input to iso date |
| 0.1.3 | 2022-01-31 | [9550](https://github.com/airbytehq/airbyte/pull/9550) | Output only records in which cursor field is greater than the value in state for incremental streams |
| 0.1.2 | 2022-01-06 | [9333](https://github.com/airbytehq/airbyte/pull/9333) | Add incremental sync mode to streams in `integration_tests/configured_catalog.json` |
| 0.1.1 | 2022-01-04 | [9275](https://github.com/airbytehq/airbyte/pull/9275) | Fix pagination handling for `survey_responses`, `bounces` and `unsubscribes` streams |
| 0.1.0 | 2021-10-27 | [4551](https://github.com/airbytehq/airbyte/pull/4551) | Add Delighted source connector |

</details>
