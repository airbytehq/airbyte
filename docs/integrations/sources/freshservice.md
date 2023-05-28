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

## Setup Guide

This guide will help you set up the Freshservice Source connector in Airbyte. You need to provide these pieces of information to configure this connector:

* Freshservice Account
* Freshservice API Key
* Freshservice Domain Name
* Replication Start Date

### Step 1: Obtain Your Freshservice Domain Name

The Freshservice Domain Name is the URL you use to access your Freshservice instance. It should be in the format `mydomain.freshservice.com`. Make a note of your domain name as you will need it to set up the connector.

### Step 2: Obtain Your Freshservice API Key

To obtain your Freshservice API Key, follow these steps:

1. Log in to your Freshservice account.
2. Click on your profile picture located in the top-right corner of your Freshservice dashboard, and then click on `Profile settings`.
3. Scroll down to the `Your API Key` section. You will find your API key here.
4. Make a note of your API key as you will need it to set up the connector. 

For more information, refer to the Freshservice documentation on [Authentication](https://api.freshservice.com/#authentication).

### Step 3: Determine Your Replication Start Date

The Replication Start Date is a UTC date and time in the format `YYYY-MM-DDT00:00:00Z`. Data before this date will not be replicated in Airbyte. Choose an appropriate date and time to start replicating your data.

### Step 4: Configure the Freshservice Source Connector

Now that you have the necessary information, follow these steps to configure the Freshservice Source Connector in Airbyte:

1. Enter your Freshservice Domain Name in the `Domain Name` field.
2. Enter your Freshservice API Key in the `API Key` field.
3. Enter your Replication Start Date in the `Start Date` field using the format provided.

Once you have entered the required information, you can proceed with setting up the Freshservice Source connector in Airbyte.

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 1.1.0 | 2023-05-09 | [25929](https://github.com/airbytehq/airbyte/pull/25929) | Add stream for customer satisfaction survey responses endpoint  |
| 1.0.0 | 2023-05-02 | [25743](https://github.com/airbytehq/airbyte/pull/25743) | Correct data types in tickets, agents and requesters schemas to match Freshservice API |
| 0.1.1 | 2021-12-28 | [9143](https://github.com/airbytehq/airbyte/pull/9143) | Update titles and descriptions |
| 0.1.0 | 2021-10-29 | [6967](https://github.com/airbytehq/airbyte/pull/6967) | 🎉 New Source: Freshservice |
