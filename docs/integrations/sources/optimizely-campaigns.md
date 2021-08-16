# Optimizely Campaigns

## Overview

The Optimizely Campaigns source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Output schema

This Source is capable of syncing the following core Streams:

* [Attribute Names](https://api.campaign.episerver.net/apidoc/index.html#/Recipient%20lists/getRecipientListAttributeNames)
* [Blacklist Entries](https://api.campaign.episerver.net/apidoc/index.html#/Blocklist%20entries)
* [Recipient Lists](https://api.campaign.episerver.net/apidoc/index.html#/Recipient%20lists)
* [Recipients](https://api.campaign.episerver.net/apidoc/index.html#/Recipients)
* [Smart Campaigns](https://api.campaign.episerver.net/apidoc/index.html#/Smart%20Campaigns)
* [Smart Campaign Reports](https://api.campaign.episerver.net/apidoc/index.html#/Smart%20Campaigns/getReport_1)
* [Transactional Mails](https://api.campaign.episerver.net/apidoc/index.html#/Transactional%20mails)
* [Transactional Mail Reports](https://api.campaign.episerver.net/apidoc/index.html#/Transactional%20mails/getReport_2)
* [Unsubscribes](https://api.campaign.episerver.net/apidoc/index.html#/Unsubscribes)

### Data type mapping

The [Optimizely Campaigns API](https://world.optimizely.com/documentation/developer-guides/campaign/rest-api/) uses the same [JSONSchema](https://json-schema.org/understanding-json-schema/reference/index.html) types that Airbyte uses internally \(`string`, `date-time`, `object`, `array`, `boolean`, `integer`, and `number`\), so no type conversions happen as part of this source.

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |
| Incremental - Deduped + history Sync | Yes |
| SSL connection | Yes |
| Namespaces | No |

### Performance considerations

The Optimizely Campaigns connector should not run into Optimizely Campaigns API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Optimizely Campaign Account
* Optimizely Campaign API Secret Key

### Setup guide

Visit the [Optimizely Campaigns Dashboard](https://www.campaign.episerver.net/action/workbench/workbench?showSideNavigationWorkbench=). To access the client id for the rest api, use the sidebar on the left and click on ```Administration -> API Overview```. To get the api token you have to follow the instructions explained [here](https://world.optimizely.com/documentation/developer-guides/campaign/rest-api/getting-started/).


## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.0.2   | 2021-08-16 | [3566](https://github.com/airbytehq/airbyte/pull/3368) | Create Connector |