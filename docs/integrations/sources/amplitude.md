# Amplitude

This page contains the setup guide and reference information for the `Amplitude` source connector.
This source can sync data for the [Amplitude API](https://developers.amplitude.com/docs/http-api-v2).

## Prerequisites

Before you begin replicating the data from `Amplitude`, please follow this guide to obtain your credentials [How to get your API key and Secret key](https://help.amplitude.com/hc/en-us/articles/360058073772-Create-and-manage-organizations-and-projects#view-and-edit-your-project-information). 
Once you have your credentials, you now can use them in order to setup the connection in Airbyte.

## Setup guide
### Step 1: Set up Amplitude source
You would need to obtain your Amplitude `API Key` and `Secret Key` using this [guide](https://help.amplitude.com/hc/en-us/articles/360058073772-Create-and-manage-organizations-and-projects#view-and-edit-your-project-information) to set up the connector in Airbyte.

### Step 2: Set up Amplitude source connector in Airbyte

### For OSS Airbyte:
1. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
2. On the Set up the `source` page, enter the name for the `Amplitude` connector and select **Amplitude** from the Source type dropdown.
3. Enter your `API Key` and `Secret Key` to corresponding fields
4. Enter the `Start Date` as the statrting point for your data replication.
5. Click on `Check Connection` to finish configuring the Amplitude source.

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the Set up the `source` page, enter the name for the `Amplitude` connector and select **Amplitude** from the Source type dropdown.
4. Enter your `API Key` and `Secret Key` to corresponding fields
5. Enter the `Start Date` as the statrting point for your data replication.
6. Click on `Check Connection` to finish configuring the Amplitude source.

## Supported Streams

Several output streams are available from this source:

* [Active Users Counts](https://developers.amplitude.com/docs/dashboard-rest-api#active-and-new-user-counts) \(Incremental sync\)
* [Annotations](https://developers.amplitude.com/docs/chart-annotations-api#get-all-annotations)
* [Average Session Length](https://developers.amplitude.com/docs/dashboard-rest-api#average-session-length) \(Incremental sync\)
* [Cohorts](https://developers.amplitude.com/docs/behavioral-cohorts-api#listing-all-cohorts)
* [Events](https://developers.amplitude.com/docs/export-api#export-api---export-your-projects-event-data) \(Incremental sync\)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

## Supported sync modes

The `Amplitude` source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |

### Performance considerations

The Amplitude connector should gracefully handle Amplitude API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

| Version | Date       | Pull Request                                           | Subject |
|:--------| :--------- | :----------------------------------------------------- | :------ |
| 0.1.6   | 2022-04-30 | [12500](https://github.com/airbytehq/airbyte/pull/12500) | Improve input configuration copy                                                             |
| 0.1.5   | 2022-04-28 | [12430](https://github.com/airbytehq/airbyte/pull/12430) | Added HTTP error descriptions and fixed `Events` stream fail caused by `404` HTTP Error |
| 0.1.4   | 2021-12-23 | [8434](https://github.com/airbytehq/airbyte/pull/8434) | Update fields in source-connectors specifications |
| 0.1.3   | 2021-10-12 | [6375](https://github.com/airbytehq/airbyte/pull/6375) | Log Transient 404 Error in Events stream  |
| 0.1.2   | 2021-09-21 | [6353](https://github.com/airbytehq/airbyte/pull/6353) | Correct output schemas on cohorts, events, active\_users, and average\_session\_lengths streams |
| 0.1.1   | 2021-06-09 | [3973](https://github.com/airbytehq/airbyte/pull/3973) | Add AIRBYTE\_ENTRYPOINT for kubernetes support |
| 0.1.0   | 2021-06-08 | [3664](https://github.com/airbytehq/airbyte/pull/3664) | New Source: Amplitude |
