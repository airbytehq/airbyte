# Freshsales

## Overview

The Freshsales supports full refresh syncs.

### Output schema

Several output streams are available from this source:

* [Contacts](https://developers.freshworks.com/crm/api/#contacts)
* [Accounts](https://developers.freshworks.com/crm/api/#accounts)
* [Open Deals](https://developers.freshworks.com/crm/api/#deals)
* [Won Deals](https://developers.freshworks.com/crm/api/#deals)
* [Lost Deals](https://developers.freshworks.com/crm/api/#deals)
* [Open Tasks](https://developers.freshworks.com/crm/api/#tasks)
* [Completed Tasks](https://developers.freshworks.com/crm/api/#tasks)
* [Past appointments](https://developers.freshworks.com/crm/api/#appointments)
* [Upcoming appointments](https://developers.freshworks.com/crm/api/#appointments)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature           | Supported? |
|:------------------|:-----------|
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |
| SSL connection    | No         |
| Namespaces        | No         |

### Performance considerations

The Freshsales connector should not run into Freshsales API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Freshsales Account
* Freshsales API Key
* Freshsales domain name

### Setup guide

Please read [How to find your API key](https://crmsupport.freshworks.com/support/solutions/articles/50000002503-how-to-find-my-api-key-).

## Changelog

| Version | Date       | Pull Request                                             | Subject                         |
|:--------|:-----------|:---------------------------------------------------------|:--------------------------------|
| 0.1.2   | 2022-07-14 | [00000](https://github.com/airbytehq/airbyte/pull/00000) | Tune the `get_view_id` function |
| 0.1.1   | 2021-12-24 | [9101](https://github.com/airbytehq/airbyte/pull/9101)   | Update fields and descriptions  |
| 0.1.0   | 2021-11-03 | [6963](https://github.com/airbytehq/airbyte/pull/6963)   | 🎉 New Source: Freshsales       |
