# Delighted

This page contains the setup guide and reference information for the Delighted source connector.

## Prerequisites

To set up the Delighted source connector, you'll need a Delighted API key. 

### Obtain a Delighted API Key

1. Log in to your [Delighted account](https://delighted.com/account/login) or create a new one if you haven't already.
2. Once logged in, navigate to your account [API settings page](https://delighted.com/account/api).
3. Generate a new API key or use an existing one.

## Set up the Delighted connector in Airbyte

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, enter the name for the Delighted connector and select **Delighted** from the Source type dropdown.
4. For **Since**, enter the date from which you'd like to replicate the data in the `YYYY-MM-DDThh:mm:ssZ` format. For example, `2022-06-01T00:00:00Z`.
5. For **API Key**, enter the Delighted API key obtained earlier.
6. Click **Set up source**.

## Supported sync modes

The Delighted source connector supports the following [sync modes](https://docs.airbyte.io/integrations/sources/delighted):

* [Full Refresh - Overwrite](https://docs.airbyte.io/integrations/sources/delighted#full-refresh-overwrite)
* [Full Refresh - Append](https://docs.airbyte.io/integrations/sources/delighted#full-refresh-append)
* [Incremental - Append](https://docs.airbyte.io/integrations/sources/delighted#incremental-append)
* [Incremental - Deduped History](https://docs.airbyte.io/integrations/sources/delighted#incremental-deduped-history)

## Supported Streams

This Source is capable of syncing the following core Streams:

* [Survey Responses](https://docs.airbyte.io/integrations/sources/delighted#survey-responses)
* [People](https://docs.airbyte.io/integrations/sources/delighted#people)
* [Bounced People](https://docs.airbyte.io/integrations/sources/delighted#bounced-people)
* [Unsubscribed People](https://docs.airbyte.io/integrations/sources/delighted#unsubscribed-people)

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