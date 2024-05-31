# Amplitude

This page guides you through setting up the Amplitude source connector to sync data for the [Amplitude API](https://www.docs.developers.amplitude.com/analytics/apis/http-v2-api/).

## Prerequisite

To set up the Amplitude source connector, you'll need your Amplitude [`API Key` and `Secret Key`](https://help.amplitude.com/hc/en-us/articles/360058073772-Create-and-manage-organizations-and-projects#view-and-edit-your-project-information).

## Set up the Amplitude source connector

1. Log into your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) or Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Amplitude** from the Source type dropdown.
4. Enter a name for your source.
5. For **API Key** and **Secret Key**, enter the Amplitude [API key and secret key](https://help.amplitude.com/hc/en-us/articles/360058073772-Create-and-manage-organizations-and-projects#view-and-edit-your-project-information).
6. For **Replication Start Date**, enter the date in YYYY-MM-DDTHH:mm:ssZ format. The data added on and after this date will be replicated. If this field is blank, Airbyte will replicate all data.
7. Click **Set up source**.

## Supported Streams

The Amplitude source connector supports the following streams:

- [Active Users Counts](https://www.docs.developers.amplitude.com/analytics/apis/dashboard-rest-api/#get-active-and-new-user-counts) \(Incremental sync\)
- [Annotations](https://www.docs.developers.amplitude.com/analytics/apis/chart-annotations-api/#get-all-chart-annotations)
- [Average Session Length](https://www.docs.developers.amplitude.com/analytics/apis/dashboard-rest-api/#get-average-session-length) \(Incremental sync\)
- [Cohorts](https://www.docs.developers.amplitude.com/analytics/apis/behavioral-cohorts-api/#get-all-cohorts-response)
- [Events](https://www.docs.developers.amplitude.com/analytics/apis/export-api/#response-schema) \(Incremental sync\)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

<!-- env:oss -->

## Supported sync modes

The Amplitude source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh
- Incremental

## Connector-specific features

There are two data region servers supported by Airbyte:

- Standard Server
- EU Residency Server

The `Standard Server` will be the default option until you change it in the Optional fields.

## Performance considerations

The Amplitude connector ideally should gracefully handle Amplitude API limitations under normal usage. [Create an issue](https://github.com/airbytehq/airbyte/issues/new/choose) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                      |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------------------- |
| 0.3.10  | 2024-04-19 | [36631](https://github.com/airbytehq/airbyte/pull/36631) | Updating to 0.80.0 CDK                                                                       |
| 0.3.9   | 2024-04-12 | [36631](https://github.com/airbytehq/airbyte/pull/36631) | schema descriptions                                                                          |
| 0.3.8   | 2024-03-12 | [35987](https://github.com/airbytehq/airbyte/pull/35987) | Unpin CDK version                                                                            |
| 0.3.7   | 2024-02-12 | [35162](https://github.com/airbytehq/airbyte/pull/35162) | Manage dependencies with Poetry.                                                             |
| 0.3.6   | 2023-10-23 | [31702](https://github.com/airbytehq/airbyte/pull/31702) | Base image migration: remove Dockerfile and use the python-connector-base image              |
| 0.3.5   | 2023-09-28 | [30846](https://github.com/airbytehq/airbyte/pull/30846) | Add support of multiple cursor date formats                                                  |
| 0.3.4   | 2023-09-28 | [30831](https://github.com/airbytehq/airbyte/pull/30831) | Add user friendly error description on 403 error                                             |
| 0.3.3   | 2023-09-21 | [30652](https://github.com/airbytehq/airbyte/pull/30652) | Update spec: declare `start_date` type as `date-time`                                        |
| 0.3.2   | 2023-09-18 | [30525](https://github.com/airbytehq/airbyte/pull/30525) | Fix `KeyError` while getting `data_region` from config                                       |
| 0.3.1   | 2023-09-15 | [30471](https://github.com/airbytehq/airbyte/pull/30471) | Fix `Event` stream: Use `start_time` instead of cursor in the case of more recent            |
| 0.3.0   | 2023-09-13 | [30378](https://github.com/airbytehq/airbyte/pull/30378) | Switch to latest CDK version                                                                 |
| 0.2.4   | 2023-05-05 | [25842](https://github.com/airbytehq/airbyte/pull/25842) | added missing attrs in events schema, enabled default availability strategy                  |
| 0.2.3   | 2023-04-20 | [25317](https://github.com/airbytehq/airbyte/pull/25317) | Refactor Events Stream, use pre-YAML version based on Python CDK                             |
| 0.2.2   | 2023-04-19 | [25315](https://github.com/airbytehq/airbyte/pull/25315) | Refactor to only fetch date_time_fields once per request                                     |
| 0.2.1   | 2023-02-03 | [25281](https://github.com/airbytehq/airbyte/pull/25281) | Reduce request_time_range to 4 hours                                                         |
| 0.2.0   | 2023-02-03 | [22362](https://github.com/airbytehq/airbyte/pull/22362) | Migrate to YAML                                                                              |
| 0.1.24  | 2023-03-28 | [21022](https://github.com/airbytehq/airbyte/pull/21022) | Enable event stream time interval selection                                                  |
| 0.1.23  | 2023-03-02 | [23087](https://github.com/airbytehq/airbyte/pull/23087) | Specified date formatting in specification                                                   |
| 0.1.22  | 2023-02-17 | [23192](https://github.com/airbytehq/airbyte/pull/23192) | Skip the stream if `start_date` is specified in the future.                                  |
| 0.1.21  | 2023-02-01 | [21888](https://github.com/airbytehq/airbyte/pull/21888) | Set `AvailabilityStrategy` for streams explicitly to `None`                                  |
| 0.1.20  | 2023-01-27 | [21957](https://github.com/airbytehq/airbyte/pull/21957) | Handle null values and empty strings in date-time fields                                     |
| 0.1.19  | 2022-12-09 | [19727](https://github.com/airbytehq/airbyte/pull/19727) | Remove `data_region` as required                                                             |
| 0.1.18  | 2022-12-08 | [19727](https://github.com/airbytehq/airbyte/pull/19727) | Add parameter to select region                                                               |
| 0.1.17  | 2022-10-31 | [18684](https://github.com/airbytehq/airbyte/pull/18684) | Add empty `series` validation for `AverageSessionLength` stream                              |
| 0.1.16  | 2022-10-11 | [17854](https://github.com/airbytehq/airbyte/pull/17854) | Add empty `series` validation for `ActtiveUsers` steam                                       |
| 0.1.15  | 2022-10-03 | [17320](https://github.com/airbytehq/airbyte/pull/17320) | Add validation `start_date` filed if it's in the future                                      |
| 0.1.14  | 2022-09-28 | [17326](https://github.com/airbytehq/airbyte/pull/17326) | Migrate to per-stream states.                                                                |
| 0.1.13  | 2022-08-31 | [16185](https://github.com/airbytehq/airbyte/pull/16185) | Re-release on new `airbyte_cdk==0.1.81`                                                      |
| 0.1.12  | 2022-08-11 | [15506](https://github.com/airbytehq/airbyte/pull/15506) | Changed slice day window to 1, instead of 3 for Events stream                                |
| 0.1.11  | 2022-07-21 | [14924](https://github.com/airbytehq/airbyte/pull/14924) | Remove `additionalProperties` field from spec                                                |
| 0.1.10  | 2022-06-16 | [13846](https://github.com/airbytehq/airbyte/pull/13846) | Try-catch the BadZipFile error                                                               |
| 0.1.9   | 2022-06-10 | [13638](https://github.com/airbytehq/airbyte/pull/13638) | Fixed an infinite loop when fetching Amplitude data                                          |
| 0.1.8   | 2022-06-01 | [13373](https://github.com/airbytehq/airbyte/pull/13373) | Fixed the issue when JSON Validator produces errors on `date-time` check                     |
| 0.1.7   | 2022-05-21 | [13074](https://github.com/airbytehq/airbyte/pull/13074) | Removed time offset for `Events` stream, which caused a lot of duplicated records            |
| 0.1.6   | 2022-04-30 | [12500](https://github.com/airbytehq/airbyte/pull/12500) | Improve input configuration copy                                                             |
| 0.1.5   | 2022-04-28 | [12430](https://github.com/airbytehq/airbyte/pull/12430) | Added HTTP error descriptions and fixed `Events` stream fail caused by `404` HTTP Error      |
| 0.1.4   | 2021-12-23 | [8434](https://github.com/airbytehq/airbyte/pull/8434)   | Update fields in source-connectors specifications                                            |
| 0.1.3   | 2021-10-12 | [6375](https://github.com/airbytehq/airbyte/pull/6375)   | Log Transient 404 Error in Events stream                                                     |
| 0.1.2   | 2021-09-21 | [6353](https://github.com/airbytehq/airbyte/pull/6353)   | Correct output schemas on cohorts, events, active_users, and average_session_lengths streams |
| 0.1.1   | 2021-06-09 | [3973](https://github.com/airbytehq/airbyte/pull/3973)   | Add AIRBYTE_ENTRYPOINT for kubernetes support                                                |
| 0.1.0   | 2021-06-08 | [3664](https://github.com/airbytehq/airbyte/pull/3664)   | New Source: Amplitude                                                                        |

</details>

<!-- /env:oss -->
