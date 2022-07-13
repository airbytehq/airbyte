# Freshservice

## Overview

The Freshservice supports full refresh syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Output schema

Several output streams are available from this source:

* [Tickets](https://api.freshservice.com/v2/#view_all_ticket) (Incremental)
* [Problems](https://api.freshservice.com/v2/#problems) (Incremental)
* [Changes](https://api.freshservice.com/v2/#changes) (Incremental)
* [Releases](https://api.freshservice.com/v2/#releases) (Incremental)
* [Requesters](https://api.freshservice.com/v2/#requesters)
* [Agents](https://api.freshservice.com/v2/#agents)
* [Locations](https://api.freshservice.com/v2/#locations)
* [Products](https://api.freshservice.com/v2/#products)
* [Vendors](https://api.freshservice.com/v2/#vendors)
* [Assets](https://api.freshservice.com/v2/#assets)
* [PurchaseOrders](https://api.freshservice.com/v2/#purchase-order)
* [Software](https://api.freshservice.com/v2/#software)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| SSL connection | No |
| Namespaces | No |

### Performance considerations

The Freshservice connector should not run into Freshservice API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Freshservice Account
* Freshservice API Key
* Freshservice domain name
* Replciation Start Date

### Setup guide

Please read [How to find your API key](https://api.freshservice.com/#authentication).

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.1 | 2021-12-28 | [9143](https://github.com/airbytehq/airbyte/pull/9143) | Update titles and descriptions |
| 0.1.0 | 2021-10-29 | [6967](https://github.com/airbytehq/airbyte/pull/6967) | 🎉 New Source: Freshservice |
