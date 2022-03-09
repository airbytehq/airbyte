# Iterable

## Overview

The Iterable supports full refresh and incremental sync.

This source can sync data for the [Iterable API](https://api.iterable.com/api/docs).

### Output schema

Several output streams are available from this source:

* [Campaigns](https://api.iterable.com/api/docs#campaigns_campaigns)
* [Campaign Metrics](https://api.iterable.com/api/docs#campaigns_metrics)
* [Channels](https://api.iterable.com/api/docs#channels_channels)
* [Email Bounce](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental sync\)
* [Email Click](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental sync\)
* [Email Complaint](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental sync\)
* [Email Open](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental sync\)
* [Email Send](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental sync\)
* [Email Send Skip](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental sync\)
* [Email Subscribe](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental sync\)
* [Email Unsubscribe](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental sync\)
* [Events](https://api.iterable.com/api/docs#events_User_events)
* [Lists](https://api.iterable.com/api/docs#lists_getLists)
* [List Users](https://api.iterable.com/api/docs#lists_getLists_0)
* [Message Types](https://api.iterable.com/api/docs#messageTypes_messageTypes)
* [Metadata](https://api.iterable.com/api/docs#metadata_list_tables)
* [Templates](https://api.iterable.com/api/docs#templates_getTemplates) \(Incremental sync\)
* [Users](https://api.iterable.com/api/docs#export_exportDataJson) \(Incremental sync\)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| SSL connection | Yes |

### Performance considerations

The Iterable connector should not run into Iterable API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Iterable Account
* Iterable API Key with `standard` permissions. See [API Keys docs](https://support.iterable.com/hc/en-us/articles/360043464871-API-Keys-) for more details.

### Setup guide
<!-- markdown-link-check-disable-next-line -->
Please read [How to find your API key](https://support.iterable.com/hc/en-us/articles/360043464871-API-Keys-#creating-api-keys).

## CHANGELOG

| Version | Date | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| `0.1.15` | 2021-12-06 | [8524](https://github.com/airbytehq/airbyte/pull/8524) | Update connector fields title/description |
| `0.1.14` | 2021-12-01 | [8380](https://github.com/airbytehq/airbyte/pull/8380) | Update `Events` stream to use `export/userEvents` endpoint |
| `0.1.13` | 2021-11-22 | [8091](https://github.com/airbytehq/airbyte/pull/8091) | Adjust slice ranges for email streams |
| `0.1.12` | 2021-11-09 | [7780](https://github.com/airbytehq/airbyte/pull/7780) | Split EmailSend stream into slices to fix premature connection close error |
| `0.1.11` | 2021-11-03 | [7619](https://github.com/airbytehq/airbyte/pull/7619) | Bugfix type error while incrementally loading the `Templates` stream |
| `0.1.10` | 2021-11-03 | [7591](https://github.com/airbytehq/airbyte/pull/7591) | Optimize export streams memory consumption for large requests |
| `0.1.9` | 2021-10-06 | [5915](https://github.com/airbytehq/airbyte/pull/5915) | Enable campaign_metrics stream |
| `0.1.8` | 2021-09-20 | [5915](https://github.com/airbytehq/airbyte/pull/5915) | Add new streams: campaign_metrics, events |
| `0.1.7` | 2021-09-20 | [6242](https://github.com/airbytehq/airbyte/pull/6242) | Updated schema for: campaigns, lists, templates, metadata |

