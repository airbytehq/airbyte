# Delighted

This page contains the setup guide and reference information for the Delighted source connector.

## Prerequisites

To set up the Delighted source connector, you'll need the [Delighted API key](https://app.delighted.com/docs/api#authentication). If you're not sure how to generate an API key in Delighted, please follow these steps:

1. Log into your Delighted account at https://delighted.com/.
2. Click on your name in the top right corner and select "Account" from the dropdown menu.
3. Click on the "API" tab.
4. Click "Generate new API key".
5. Copy the generated key to your clipboard.

## Set up the Delighted connector in Airbyte

1. In the Airbyte UI, navigate to the Delighted configuration form.
2. For **Since**, enter the date from which you'd like to replicate the data in the format `yyyy-mm-ddThh:mm:ss` (e.g., `2022-01-01T00:00:00`).
3. For **API Key**, paste in the API key you generated from your Delighted account.
4. Click **Test** to verify the connection between Airbyte and Delighted.
5. If the connection test completes successfully, click **Save** to save and activate the Delighted connector.

## Supported sync modes

The Delighted source connector supports the following [ sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

* [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
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
| 0.2.2   | 2023-03-09 | [23909](https://github.com/airbytehq/airbyte/pull/23909) | Updated the input config pattern to accept both `RFC3339` and `datetime string` formats in UI    |
| 0.2.1   | 2023-02-14 | [23009](https://github.com/airbytehq/airbyte/pull/23009) |Specified date formatting in specification                                                                |
| 0.2.0   | 2022-11-22 | [19822](https://github.com/airbytehq/airbyte/pull/19822) | Migrate to Low code + certify to Beta                                                                |
| 0.1.4   | 2022-06-10 | [13439](https://github.com/airbytehq/airbyte/pull/13439) | Change since parameter input to iso date                                                             |
| 0.1.3   | 2022-01-31 | [9550](https://github.com/airbytehq/airbyte/pull/9550)   | Output only records in which cursor field is greater than the value in state for incremental streams |
| 0.1.2   | 2022-01-06 | [9333](https://github.com/airbytehq/airbyte/pull/9333)   | Add incremental sync mode to streams in `integration_tests/configured_catalog.json`                  |
| 0.1.1   | 2022-01-04 | [9275](https://github.com/airbytehq/airbyte/pull/9275)   | Fix pagination handling for `survey_responses`, `bounces` and `unsubscribes` streams                 |
| 0.1.0   | 2021-10-27 | [4551](https://github.com/airbytehq/airbyte/pull/4551)   | Add Delighted source connector                                                                       |