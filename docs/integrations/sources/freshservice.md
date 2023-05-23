# Freshservice

## Overview

The Freshservice connector supports full refresh syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

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
* [Satisfaction Survey Responses](https://api.freshservice.com/#ticket_csat_attributes)

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
* Replication Start Date

### Setup guide

1. To obtain your Freshservice API Key, go to your Freshservice dashboard and click on your profile picture in the top right corner.
2. Select "Profile settings" from the dropdown menu.
3. In the "Profile settings" page, you will find your API Key under the "Your API Key" section. Copy the API Key.
4. Go to the Airbyte Configuration form for the Freshservice connector.
5. Enter your Freshservice domain name in the "Domain Name" field. This can be found in the website URL when you are logged in to your Freshservice account (e.g., `mydomain.freshservice.com`).
6. Paste the copied API Key into the "API Key" field of the configuration form. Ensure that you have entered the API Key accurately, as it is case sensitive.
7. Set the desired Replication Start Date in the "Start Date" field in the format `YYYY-MM-DDThh:mm:ssZ` (e.g., `2020-10-01T00:00:00Z`). This will ensure that any data before this date will not be replicated.

For more information on Freshservice authentication and how to find your API key, please refer to the [Freshservice API documentation](https://api.freshservice.com/#authentication).

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 1.1.0 | 2023-05-09 | [25929](https://github.com/airbytehq/airbyte/pull/25929) | Add stream for customer satisfaction survey responses endpoint  |
| 1.0.0 | 2023-05-02 | [25743](https://github.com/airbytehq/airbyte/pull/25743) | Correct data types in tickets, agents and requesters schemas to match Freshservice API |
| 0.1.1 | 2021-12-28 | [9143](https://github.com/airbytehq/airbyte/pull/9143) | Update titles and descriptions |
| 0.1.0 | 2021-10-29 | [6967](https://github.com/airbytehq/airbyte/pull/6967) | 🎉 New Source: Freshservice |