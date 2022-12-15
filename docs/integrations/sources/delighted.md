# Delighted

This page contains the setup guide and reference information for the Delighted source connector.

## Prerequisites

To set up the Delighted source connector, you'll need the [Delighted API key](https://app.delighted.com/docs/api#authentication).

## Set up the Delighted connector in Airbyte

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, enter the name for the Delighted connector and select **Delighted** from the Source type dropdown.
4. For **Since**, enter the date in a Unix Timestamp format. The data added on and after this date will be replicated.
5. For **API Key**, enter your [Delighted `API Key`](https://delighted.com/account/api).
6. Click **Set up source**.

## Supported sync modes

The Delighted source connector supports the following [ sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

* [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/glossary#full-refresh-sync)
* [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
* [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
* [Incremental - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history)

## Supported Streams

This Source is capable of syncing the following core Streams:

* [Survey Responses](https://app.delighted.com/docs/api/listing-survey-responses)
* [People](https://app.delighted.com/docs/api/listing-people)
* [Bounced People](https://app.delighted.com/docs/api/listing-bounced-people)
* [Unsubscribed People](https://app.delighted.com/docs/api/listing-unsubscribed-people)

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                              |
|:--------|:-----------|:---------------------------------------------------------|:-----------------------------------------------------------------------------------------------------|
| 0.2.0   | 2022-11-22 | [19822](https://github.com/airbytehq/airbyte/pull/19822) | Migrate to Low code + certify to Beta                                                                |
| 0.1.4   | 2022-06-10 | [13439](https://github.com/airbytehq/airbyte/pull/13439) | Change since parameter input to iso date                                                             |
| 0.1.3   | 2022-01-31 | [9550](https://github.com/airbytehq/airbyte/pull/9550)   | Output only records in which cursor field is greater than the value in state for incremental streams |
| 0.1.2   | 2022-01-06 | [9333](https://github.com/airbytehq/airbyte/pull/9333)   | Add incremental sync mode to streams in `integration_tests/configured_catalog.json`                  |
| 0.1.1   | 2022-01-04 | [9275](https://github.com/airbytehq/airbyte/pull/9275)   | Fix pagination handling for `survey_responses`, `bounces` and `unsubscribes` streams                 |
| 0.1.0   | 2021-10-27 | [4551](https://github.com/airbytehq/airbyte/pull/4551)   | Add Delighted source connector                                                                       |
