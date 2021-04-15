# Iterable

## Overview

The Iterable supports full refresh sync. 

This source can sync data for the [Iterable API](https://api.iterable.com/api/docs).

### Output schema

Several output streams are available from this source:

* [Campaigns](https://api.iterable.com/api/docs#campaigns_campaigns)
* [Channels](https://api.iterable.com/api/docs#channels_channels)
* [Email Bounce](https://api.iterable.com/api/docs#export_exportDataJson)
* [Email Click](https://api.iterable.com/api/docs#export_exportDataJson)
* [Email Complaint](https://api.iterable.com/api/docs#export_exportDataJson)
* [Email Open](https://api.iterable.com/api/docs#export_exportDataJson)
* [Email Send](https://api.iterable.com/api/docs#export_exportDataJson)
* [Email Send Skip](https://api.iterable.com/api/docs#export_exportDataJson)
* [Email Subscribe](https://api.iterable.com/api/docs#export_exportDataJson)
* [Email Unsubscribe](https://api.iterable.com/api/docs#export_exportDataJson)
* [Lists](https://api.iterable.com/api/docs#lists_getLists)
* [List Users](https://api.iterable.com/api/docs#lists_getLists_0)
* [Message Types](https://api.iterable.com/api/docs#messageTypes_messageTypes)
* [Metadata](https://api.iterable.com/api/docs#metadata_list_tables)
* [Templates](https://api.iterable.com/api/docs#templates_getTemplates)
* [Users](https://api.iterable.com/api/docs#export_exportDataJson)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | No |
| SSL connection | Yes |

### Performance considerations

The Iterable connector should not run into Iterable API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Iterable Account
* Iterable API Key

### Setup guide

Please read [How to find your API key](https://support.iterable.com/hc/en-us/articles/360043464871-API-Keys-#creating-api-keys).

