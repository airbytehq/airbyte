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

* Freshservice account
* Freshservice API key
* Freshservice domain name
* Replication start date

### Setup guide

In order to set up the Freshservice connector, follow these steps:

1. Log in to your Freshservice account.
2. Click on the cog icon in the bottom left corner of the screen to access the Settings page.
3. Click on the “API Key” link. 
4. On the API key page, copy your API key to your clipboard.
5. Open Airbyte’s Freshservice connector configuration form and fill in the following required fields:
    * Domain Name: The name of your Freshservice domain, for example mydomain.freshservice.com.
    * API Key: Paste your API key from step 4.
    * Start Date: UTC date and time in the format 2020-10-01T00:00:00Z. Any data before this date will not be replicated.
6. Select the output streams you require from the list provided and specify tables and columns for replication.
7. Set up a schedule for when the connector should sync data.
8. Test the connection to ensure that it is properly established.
9. Save the connector configuration.
10. Run a manual sync to start replication of data from Freshservice.
11. Monitor the sync to ensure that it runs without errors and troubleshoot any issues that arise.

For more detailed information and tips on integrating Freshservice with Airbyte, refer to [Freshservice’s API documentation.](https://api.freshservice.com/v2/) 

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 1.0.0 | 2023-05-02 | [25743](https://github.com/airbytehq/airbyte/pull/25743) | Correct data types in tickets, agents and requesters schemas to match Freshservice API |
| 0.1.1 | 2021-12-28 | [9143](https://github.com/airbytehq/airbyte/pull/9143) | Update titles and descriptions |
| 0.1.0 | 2021-10-29 | [6967](https://github.com/airbytehq/airbyte/pull/6967) | 🎉 New Source: Freshservice |