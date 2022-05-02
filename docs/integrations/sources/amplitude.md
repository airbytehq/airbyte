# Amplitude

## Overview

The Amplitude supports full refresh and incremental sync.

This source can sync data for the [Amplitude API](https://developers.amplitude.com/docs/http-api-v2).

### Output schema

Several output streams are available from this source:

* [Active Users Counts](https://developers.amplitude.com/docs/dashboard-rest-api#active-and-new-user-counts) \(Incremental sync\)
* [Annotations](https://developers.amplitude.com/docs/chart-annotations-api#get-all-annotations)
* [Average Session Length](https://developers.amplitude.com/docs/dashboard-rest-api#average-session-length) \(Incremental sync\)
* [Cohorts](https://developers.amplitude.com/docs/behavioral-cohorts-api#listing-all-cohorts)
* [Events](https://developers.amplitude.com/docs/export-api#export-api---export-your-projects-event-data) \(Incremental sync\)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| SSL connection | Yes |

### Performance considerations

The Amplitude connector should gracefully handle Amplitude API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Amplitude API Key
* Amplitude Secret Key

### Setup guide
<!-- markdown-link-check-disable-next-line -->
Please read [How to get your API key and Secret key](https://help.amplitude.com/hc/en-us/articles/360058073772-Create-and-manage-organizations-and-projects#view-and-edit-your-project-information).

## Changelog

| Version | Date       | Pull Request                                           | Subject |
| :------ | :--------- | :----------------------------------------------------- | :------ |
| 0.1.5   | 2022-04-28 | [12430](https://github.com/airbytehq/airbyte/pull/12430) | Added HTTP error descriptions and fixed `Events` stream fail caused by `404` HTTP Error |
| 0.1.4   | 2021-12-23 | [8434](https://github.com/airbytehq/airbyte/pull/8434) | Update fields in source-connectors specifications |
| 0.1.3   | 2021-10-12 | [6375](https://github.com/airbytehq/airbyte/pull/6375) | Log Transient 404 Error in Events stream  |
| 0.1.2   | 2021-09-21 | [6353](https://github.com/airbytehq/airbyte/pull/6353) | Correct output schemas on cohorts, events, active\_users, and average\_session\_lengths streams |
| 0.1.1   | 2021-06-09 | [3973](https://github.com/airbytehq/airbyte/pull/3973) | Add AIRBYTE\_ENTRYPOINT for kubernetes support |
| 0.1.0   | 2021-06-08 | [3664](https://github.com/airbytehq/airbyte/pull/3664) | New Source: Amplitude |
