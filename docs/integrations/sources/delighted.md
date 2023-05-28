# Delighted

This page contains the setup guide and reference information for the Delighted source connector.

## Prerequisites

To set up the Delighted source connector, you'll need the [Delighted API key](https://app.delighted.com/docs/api#authentication).

## Setup Guide

This guide will help you set up the Delighted source connector in Airbyte.

### Obtain API Key from Delighted

1. Log into your [Delighted account](https://delighted.com/login).
2. Click on **Settings** at the bottom left corner of the page.
3. Select **API** from the settings menu.
4. Find the **API key** section and copy the generated API key. If the API key is not visible, click on **Generate API key** to create one.

   For more information, please refer to the [Delighted API Key Guide](https://help.delighted.com/article/69-about-delighteds-api#api-key).

### Configure the Delighted Source Connector

1. In the connector configuration form in Airbyte, enter the following information:

   - **API Key**: Paste the API key you copied from the Delighted website.
   - **Date Since**: Enter the date from which you want to replicate the data. The input format should be one of the following: `YYYY-MM-DDTHH:mm:ssZ` or `YYYY-MM-DD HH:mm:ss`. Please note that data added on and after this date will be replicated.

2. After entering the required information, proceed to complete the setup process.

Now you have successfully set up the Delighted source connector in Airbyte.

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
