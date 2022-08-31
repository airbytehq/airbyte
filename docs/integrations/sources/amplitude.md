# Amplitude

This page guides you through setting up the Amplitude source connector to sync data for the [Amplitude API](https://developers.amplitude.com/docs/http-api-v2).

## Prerequisite

To set up the Amplitude source connector, you'll need your Amplitude [`API Key` and `Secret Key`](https://help.amplitude.com/hc/en-us/articles/360058073772-Create-and-manage-organizations-and-projects#view-and-edit-your-project-information).

## Set up the Amplitude source connector

1. Log into your [Airbyte Cloud](https://cloud.airbyte.io/workspaces) or Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**. 
3. On the Set up the source page, select **Amplitude** from the Source type dropdown.
4. Enter a name for your source.
5. For **API Key** and **Secret Key**, enter the Amplitude [API key and secret key](https://help.amplitude.com/hc/en-us/articles/360058073772-Create-and-manage-organizations-and-projects#view-and-edit-your-project-information).
6. For **Replication Start Date**, enter the date in YYYY-MM-DDTHH:mm:ssZ format. The data added on and after this date will be replicated. If this field is blank, Airbyte will replicate all data.
7. Click **Set up source**.

## Supported Streams

The Amplitude source connector supports the following streams:

* [Active Users Counts](https://developers.amplitude.com/docs/dashboard-rest-api#active-and-new-user-counts) \(Incremental sync\)
* [Annotations](https://developers.amplitude.com/docs/chart-annotations-api#get-all-annotations)
* [Average Session Length](https://developers.amplitude.com/docs/dashboard-rest-api#average-session-length) \(Incremental sync\)
* [Cohorts](https://developers.amplitude.com/docs/behavioral-cohorts-api#listing-all-cohorts)
* [Events](https://developers.amplitude.com/docs/export-api#export-api---export-your-projects-event-data) \(Incremental sync\)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

## Supported sync modes

The Amplitude source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh
- Incremental

## Performance considerations

The Amplitude connector ideally should gracefully handle Amplitude API limitations under normal usage. [Create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                         |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------------------------------------------------------|
| 0.1.12  | 2022-08-11 | [15506](https://github.com/airbytehq/airbyte/pull/15506) | Changed slice day window to 1, instead of 3 for Events stream
| 0.1.11  | 2022-07-21 | [14924](https://github.com/airbytehq/airbyte/pull/14924) | Remove `additionalProperties` field from spec                                                   |
| 0.1.10  | 2022-06-16 | [13846](https://github.com/airbytehq/airbyte/pull/13846) | Try-catch the BadZipFile error                                                                  |
| 0.1.9   | 2022-06-10 | [13638](https://github.com/airbytehq/airbyte/pull/13638) | Fixed an infinite loop when fetching Amplitude data                                             |
| 0.1.8   | 2022-06-01 | [13373](https://github.com/airbytehq/airbyte/pull/13373) | Fixed the issue when JSON Validator produces errors on `date-time` check                        |
| 0.1.7   | 2022-05-21 | [13074](https://github.com/airbytehq/airbyte/pull/13074) | Removed time offset for `Events` stream, which caused a lot of duplicated records               |
| 0.1.6   | 2022-04-30 | [12500](https://github.com/airbytehq/airbyte/pull/12500) | Improve input configuration copy                                                                |
| 0.1.5   | 2022-04-28 | [12430](https://github.com/airbytehq/airbyte/pull/12430) | Added HTTP error descriptions and fixed `Events` stream fail caused by `404` HTTP Error         |
| 0.1.4   | 2021-12-23 | [8434](https://github.com/airbytehq/airbyte/pull/8434)   | Update fields in source-connectors specifications                                               |
| 0.1.3   | 2021-10-12 | [6375](https://github.com/airbytehq/airbyte/pull/6375)   | Log Transient 404 Error in Events stream                                                        |
| 0.1.2   | 2021-09-21 | [6353](https://github.com/airbytehq/airbyte/pull/6353)   | Correct output schemas on cohorts, events, active\_users, and average\_session\_lengths streams |
| 0.1.1   | 2021-06-09 | [3973](https://github.com/airbytehq/airbyte/pull/3973)   | Add AIRBYTE\_ENTRYPOINT for kubernetes support                                                  |
| 0.1.0   | 2021-06-08 | [3664](https://github.com/airbytehq/airbyte/pull/3664)   | New Source: Amplitude                                                                           |
